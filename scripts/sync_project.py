#!/usr/bin/env python3
"""Explicit allowlist curation: plan -> apply -> review/stage -> commit -> approved push."""
import argparse
import csv
from datetime import date
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys

from repository_guard import ROOT, check, inspect, links


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


def accounting(ids):
    text = subprocess.check_output(['sacct', '-X', '-n', '-P', '-j', ','.join(ids),
                                    '--format=JobID,State,ExitCode'], text=True)
    result = {}
    for line in text.splitlines():
        fields = line.split('|')
        if len(fields) >= 3 and fields[0] in ids:
            result[fields[0]] = {'state': fields[1], 'exit_code': fields[2]}
    missing = set(ids) - set(result)
    if missing:
        raise ValueError('Accounting unavailable; refusing to infer status: ' + ','.join(sorted(missing)))
    return result


def success(states, job):
    return states.get(job) == {'state': 'COMPLETED', 'exit_code': '0:0'}


def tsv(rows, fields):
    f = io.StringIO()
    w = csv.DictWriter(f, fieldnames=fields, delimiter='\t', lineterminator='\n')
    w.writeheader(); w.writerows(rows)
    return f.getvalue().encode()


def source_file(root, rel):
    path = root / rel
    if root.resolve() not in path.resolve().parents or path.is_symlink() or not path.is_file():
        raise ValueError('Missing/unsafe source: ' + rel)
    if path.stat().st_size > 5 * 1024 * 1024:
        raise ValueError('Source too large: ' + rel)
    return path


def approved_remote(url):
    return url in ('https://github.com/FarnazSalehi94/Reference-Refinement.git',
                   'git@github.com:FarnazSalehi94/Reference-Refinement.git')


def prepare(source):
    config = json.loads((ROOT/'configs/import_allowlist.json').read_text())
    policy = json.loads((ROOT/'configs/evaluation_policy.json').read_text())['previous_kmer_evaluation']
    if policy['classification'] != 'historical/preliminary' or policy['replacement_status'] != 'planned' or policy['replacement_job_ids']:
        raise ValueError('Evaluation policy changed: explicitly review generator and new evidence before promotion')
    jobs = dict(config['jobs'])
    for job in policy['jobs']:
        jobs[job] += ' — historical/preliminary outputs'
    # Future corrected Hi-C imports require a successful regeneration job and matrix QC.
    corrected = []
    for manifest in sorted((source/config['corrected_hic_root']).glob('*/submitted_regeneration.tsv')):
        for row in csv.DictReader(manifest.open(), delimiter='\t'):
            job = row['job_id'].split(';')[0]
            jobs[job] = row['assembly'] + ' corrected Cooler / plots (' + manifest.parent.name + ')'
            corrected.append((manifest.parent, row['assembly'], job))
    states = accounting(list(jobs))
    pending = {}
    entries = []
    figure_rows = []
    corrected_available = []

    def add(src, dest, job='', category='source snapshot'):
        path = source_file(source, src)
        before = path.stat()
        data = path.read_bytes()
        if path.stat().st_mtime_ns != before.st_mtime_ns or path.stat().st_size != len(data):
            raise ValueError('Source changed during read: ' + src)
        inspect(dest, data)
        if dest in pending:
            raise ValueError('Destination collision: ' + dest)
        pending[dest] = data
        entries.append({'source_relative': src, 'repository_path': dest,
                        'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
                        'evidence_job': job, 'category': category})
        if category == 'verified figure':
            figure_rows.append({'path': dest, 'source': src, 'job': job})

    for src, dest in config['files'].items():
        add(src, dest)
    for srcdir, destdir in config['script_groups'].items():
        for path in sorted((source/srcdir).iterdir()):
            if path.is_file() and path.suffix in ('.py', '.slurm'):
                add(path.relative_to(source).as_posix(), destdir + '/' + path.name)
    for category, key in [('verified result', 'verified_results'), ('verified figure', 'verified_figures')]:
        for entry in config[key]:
            if not success(states, entry['job']):
                raise ValueError('Required result job is not successfully completed: ' + entry['job'])
            if 'log' in entry and not source_file(source, entry['log']).read_text().rstrip().endswith('Done!'):
                raise ValueError('Merqury internal completion marker absent: ' + entry['log'])
            add(entry['source'], entry['destination'], entry['job'], category)
    for revision, assembly, job in corrected:
        if not success(states, job):
            continue
        work = revision/assembly
        qc = json.loads(source_file(source, (work/'validation.json').relative_to(source).as_posix()).read_text())
        if not qc.get('validated_pairs_contacts') or not qc.get('sample', {}).get('exact_bin_count_match'):
            raise ValueError('Corrected Hi-C validation incomplete: ' + str(work))
        if not all(v.get('balance_converged') for v in qc['resolutions'].values()):
            raise ValueError('Corrected Hi-C balancing incomplete')
        corrected_available.append(assembly + ' / ' + revision.name)
        prefix = f'figures/hic/{revision.name}/{assembly}/'
        for figure in sorted((work/'figures').glob('*.png')):
            add(figure.relative_to(source).as_posix(), prefix + figure.name, job, 'verified figure')
        for report in sorted((work/'reports').glob('*')):
            if report.suffix in ('.tsv', '.json'):
                add(report.relative_to(source).as_posix(), f'results/hic/{revision.name}/{assembly}/' + report.name, job, 'verified result')
        add((work/'validation.json').relative_to(source).as_posix(), f'results/hic/{revision.name}/{assembly}/validation.json', job, 'verified result')
    pending['metadata/import_manifest.tsv'] = tsv(entries, ['source_relative', 'repository_path', 'sha256', 'bytes', 'evidence_job', 'category'])
    pending['metadata/slurm_status.json'] = (json.dumps(states, indent=2, sort_keys=True) + '\n').encode()
    status = ['# Project status', '', 'Observed ' + date.today().isoformat() + ' (HPC sacct; source-file checks also required for result imports).', '',
              '## Quality-evaluation classification', '',
              '| Evaluation | Scientific status | Execution / replacement evidence |', '|---|---|---|',
              '| Previous Merqury, QV and read-kmer estimates/spectra | **Historical/preliminary; not current endorsed estimates** | Earlier jobs 2871273/2871275 completed; outputs preserved |',
              '| Replacement Merqury, QV and k-mer evaluation | **Planned; not confirmed running** | No replacement job IDs or new results available; no analyses submitted by this documentation update |', '',
              'A completed job below records execution, not acceptance of its estimates. Reclassification does not prove prior calculations incorrect. See [evaluation policy](configs/evaluation_policy.json).', '',
              '## Scheduler snapshot', '', '| Job | Analysis | State | Exit code |', '|---|---|---|---|']
    for job, name in jobs.items():
        r = states[job]
        exit_display = '— (not final)' if r['state'] in ('RUNNING', 'PENDING', 'CONFIGURING', 'COMPLETING', 'SUSPENDED') else r['exit_code']
        status.append(f'| {job} | {name} | {r["state"]} | {exit_display} |')
    status += ['', '## Interpretation and remaining work', '',
               '- Assembly runs, reference comparisons and gap statistics are completed; small source outputs passed import checks.',
               '- Previous Merqury/QV/k-mer outputs are historical/preliminary and preserved, not current quality conclusions. Repeat evaluation is planned; it has not been confirmed started.',
               '- Hi-C mapping job completion is not corrected-matrix validation. Legacy Cooler outputs are excluded.',
               '- Pair validation, Pretext and corrected matrix status must be read independently. Pretext completion does not imply visual review.',
               '- Full pairs validation and successful matrix QC are mandatory before corrected Hi-C figures enter the curated index.',
               '- BUSCO, contamination screening, repeat/missing-sequence characterization and independent read-supported refinement remain planned.',
               '- No automatic assembly correction, scaffolding or sequencing target design is performed by synchronization.',
               '- Cross-animal dataset provenance and reference-alignment ambiguity remain interpretation limitations.', '',
               'See [results](results/README.md), [figures](figures/README.md), and [Hi-C workflow](analyses/hic-contact-maps/README.md).', '']
    pending['PROJECT_STATUS.md'] = '\n'.join(status).encode()
    figure_index = ['# Figure index', '', 'Previous Merqury spectra are **historical/preliminary**, retained for provenance while repeat evaluation is planned. No replacement quality figures are available. Inclusion does not establish structural correctness.', '',
                    '| Figure | Source-relative path | Execution job | Scientific status |', '|---|---|---|---|']
    for r in figure_rows:
        classification = 'Historical/preliminary; not a current quality result' if r['job'] in policy['jobs'] else 'Completed screening output; interpretation remains qualified'
        figure_index.append(f'| [{r["path"]}](../{r["path"]}) | `{r["source"]}` | {r["job"]} | {classification} |')
    figure_index += ['', 'Reference coverage SVGs show aligned target-span unions, not base identity. Historical Merqury spectra used the same HiFi k=21 database; this is prior methodology, not a new evaluation.',
                     'Corrected Hi-C panels use per-panel color limits: do not compare colors as absolute contact strengths across panels.', '']
    pending['figures/README.md'] = '\n'.join(figure_index).encode()
    # Build one consistent metrics table from source tables, not hand-entered values.
    gap = list(csv.DictReader(io.StringIO(pending['results/assembly/gap_stats.tsv'].decode()), delimiter='\t'))
    mq = {r['assembly']: r for r in csv.DictReader(io.StringIO(pending['results/merqury/merqury_summary.tsv'].decode()), delimiter='\t')}
    if len(gap) != 3:
        raise ValueError('Expected exactly three assembly statistic rows')
    by_label = {}
    for row in gap:
        path = row['path']
        label = 'hifiasm' if '/hifiasm/run_2871178/' in path else ('verkko' if '/verkko/run_2871179/' in path else ('grcr8' if path.endswith('/GRCr8.fasta') else None))
        if label is None or label in by_label:
            raise ValueError('Unrecognized/duplicate assembly statistics source')
        by_label[label] = row
    rows = []
    table = ['| Metric | Hifiasm primary | Verkko main | GRCr8 |', '|---|---:|---:|---:|']
    for field, label in [('total_sequence_bp', 'Length (bp)'), ('fasta_records_scaffolds', 'FASTA records'),
                         ('contig_N50_bp', 'True contig N50 (bp)'), ('scaffold_N50_bp', 'Scaffold N50 (bp)'),
                         ('N_run_gap_count', 'N-run gaps'), ('total_N_gap_bases', 'Gap bases')]:
        table.append('| ' + label + ' | ' + ' | '.join(f'{int(by_label[s][field]):,}' for s in ('hifiasm','verkko','grcr8')) + ' |')
    headline_table = list(table)
    for field, label in [('QV', 'Previous Merqury QV — historical/preliminary'), ('completeness_percent', 'Previous solid-read k-mer completeness (%) — historical/preliminary')]:
        table.append('| ' + label + ' | ' + ' | '.join(mq[s][field] for s in ('hifiasm','verkko','grcr8')) + ' |')
    for s in ('hifiasm','verkko','grcr8'):
        rows.append(dict(assembly=s, **{k:v for k,v in by_label[s].items() if k!='path'}, QV=mq[s]['QV'], completeness_percent=mq[s]['completeness_percent']))
    pending['results/assembly/comparison.tsv'] = tsv(rows, list(rows[0]))
    pending['results/assembly/COMPARISON.md'] = ('# Assembly comparison and historical quality estimates\n\n'
        'Contiguity/gap metrics retain their current status. **QV and k-mer completeness below are historical/preliminary**, not endorsed current quality estimates. Replacement evaluation is planned; no new values/job IDs are available. The combined TSV retains all prior numerical values unchanged for provenance.\n\n' + '\n'.join(table) + '\n').encode()
    readme = (ROOT/'README.md').read_text()
    readme = re.sub(r'<!-- BEGIN VERIFIED_METRICS -->.*?<!-- END VERIFIED_METRICS -->',
                    '<!-- BEGIN VERIFIED_METRICS -->\n' + '\n'.join(headline_table) + '\n<!-- END VERIFIED_METRICS -->', readme, flags=re.S)
    current = ('Validated corrected Hi-C outputs available: ' + '; '.join(corrected_available) + '. Interpretation remains subject to visual/independent review.') if corrected_available else 'Corrected Hi-C outputs are not yet eligible for import; mapping, pairs validation and regeneration have separate status gates.'
    readme = re.sub(r'<!-- BEGIN CURRENT_STATUS -->.*?<!-- END CURRENT_STATUS -->',
                    '<!-- BEGIN CURRENT_STATUS -->\\n> ' + current + '\\n<!-- END CURRENT_STATUS -->', readme, flags=re.S)
    pending['README.md'] = readme.encode()
    return pending


def apply_or_plan(source, apply):
    pending = prepare(source)
    state_path = ROOT/'metadata/sync_state.json'
    old = json.loads(state_path.read_text()) if state_path.exists() else {}
    changed = []
    for dest, data in pending.items():
        inspect(dest, data)
        path = ROOT/dest
        if path.is_symlink() or ROOT.resolve() not in path.resolve().parents:
            raise ValueError('Unsafe destination symlink/path: ' + dest)
        current = path.read_bytes() if path.exists() else None
        if current == data:
            continue
        if dest not in ('README.md',) and current is not None:
            previous = old.get(dest)
            if previous is None or hashlib.sha256(current).hexdigest() != previous:
                raise ValueError('Local edits/unmanaged collision; review before overwriting: ' + dest)
        changed.append(dest)
    # No automatic deletions; an explicit manifest review is required for removed sources.
    removed = set(old) - set(pending)
    if removed:
        raise ValueError('Previously managed paths disappeared; review manually: ' + ', '.join(sorted(removed)))
    print('\n'.join('UPDATE ' + name for name in changed) if changed else 'No curated content changes')
    print(f'{len(pending)} managed files; {len(changed)} proposed updates; no staging/commit/push')
    if apply:
        for dest in changed:
            path = ROOT/dest
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(pending[dest])
        state = {name: hashlib.sha256(data).hexdigest() for name, data in sorted(pending.items())}
        state_path.write_text(json.dumps(state, indent=2) + '\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['plan','apply','check','commit','push'])
    p.add_argument('--source', type=Path)
    p.add_argument('--message')
    p.add_argument('--approve-push', action='store_true')
    args = p.parse_args()
    if args.command in ('plan','apply'):
        if args.source is None:
            p.error('--source is required; no implicit HPC dependency')
        apply_or_plan(args.source.resolve(), args.command == 'apply')
    elif args.command == 'check':
        check(staged=True); links()
    elif args.command == 'commit':
        if not args.message:
            p.error('--message is required')
        check(staged=True); links()
        subprocess.run(['git', '-C', str(ROOT), 'diff', '--cached', '--check'], check=True)
        subprocess.run(['git', '-C', str(ROOT), 'commit', '-m', args.message], check=True)
    else:
        if not args.approve_push:
            p.error('Push requires explicit --approve-push after reviewing every outgoing commit')
        branch = git('branch', '--show-current')
        if not branch.startswith(('curate/', 'research/')):
            raise ValueError('Push only review branches curate/* or research/*; no direct main push')
        if git('status', '--porcelain'):
            raise ValueError('Commit/review working-tree changes before push')
        if not approved_remote(git('remote', 'get-url', 'origin')):
            raise ValueError('Unexpected remote URL')
        ssl_setting = subprocess.run(['git', '-C', str(ROOT), 'config', '--get', 'http.sslVerify'], stdout=subprocess.PIPE, text=True)
        if ssl_setting.stdout.strip().lower() == 'false':
            raise ValueError('SSL verification must not be disabled')
        # Check every outgoing tree, not just the final index (secrets must not hide in earlier commits).
        subprocess.run(['git', '-C', str(ROOT), 'fetch', 'origin'], check=True)
        subprocess.run(['git', '-C', str(ROOT), 'merge-base', '--is-ancestor', 'origin/main', 'HEAD'], check=True)
        commits = git('rev-list', 'origin/main..HEAD').splitlines()
        for commit in commits:
            for line in git('ls-tree', '-r', commit).splitlines():
                meta, name = line.split('\t', 1)
                if meta.split()[0] not in ('100644','100755'):
                    raise ValueError('Unsafe tree entry: ' + name)
                data = subprocess.check_output(['git','-C',str(ROOT),'show',commit+':'+name])
                inspect(name, data)
        subprocess.run(['git', '-C', str(ROOT), 'push', 'origin', 'HEAD:refs/heads/' + branch], check=True)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, subprocess.CalledProcessError, OSError) as e:
        print('STOP:', str(e), file=sys.stderr)
        sys.exit(1)
