#!/usr/bin/env python3
"""One read-only EOF scan of finished pairs on a compute node, with dedup count reconciliation."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess


def signature(path):
    s = path.stat()
    return {'path': str(path.resolve()), 'size': s.st_size,
            'mtime_ns': s.st_mtime_ns, 'ctime_ns': s.st_ctime_ns}


def validate(pairs, sizes_path, stats_path, bwa_log):
    before = {str(p): signature(p) for p in (pairs, sizes_path, stats_path, bwa_log)}
    if any(v['size'] == 0 for v in before.values()):
        raise ValueError('Empty required output')
    with bwa_log.open('rb') as f:
        f.seek(max(0, bwa_log.stat().st_size - 16384))
        tail = f.read().decode(errors='replace')
    if '[main] Real time:' not in tail or '[main] CMD:' not in tail or ' mem ' not in tail:
        raise ValueError('BWA-MEM completion footer missing')
    sizes = dict((a, int(b)) for a, b in (line.split() for line in sizes_path.read_text().splitlines()))
    stats = {}
    for line in stats_path.read_text().splitlines():
        fields = line.split('\t')
        if len(fields) == 2:
            try:
                stats[fields[0]] = int(fields[1])
            except ValueError:
                pass
    for key in ('total', 'total_mapped', 'total_dups', 'total_nodups', 'total_unmapped', 'total_single_sided_mapped'):
        if key not in stats:
            raise ValueError('Missing dedup statistic: ' + key)
    if stats['total_mapped'] != stats['total_dups'] + stats['total_nodups']:
        raise ValueError('Inconsistent mapped/duplicate totals')
    if stats['total'] != stats['total_mapped'] + stats['total_unmapped'] + stats['total_single_sided_mapped']:
        raise ValueError('Inconsistent total pair categories')
    header_sizes = {}
    columns = None
    pair_types = Counter()
    counts = Counter()
    records = 0
    with pairs.open('rb', buffering=8*1024*1024) as f:
        for line_number, line in enumerate(f, 1):
            if not line.endswith(b'\n'):
                raise ValueError(f'Truncated/non-newline-terminated line {line_number}')
            if line.startswith(b'#'):
                if records:
                    raise ValueError('Header inside contact records')
                if line.startswith(b'#chromsize:'):
                    _, chrom, length = line.decode().split()
                    header_sizes[chrom] = int(length)
                elif line.startswith(b'#columns:'):
                    columns = line.decode().split(':', 1)[1].split()
                continue
            if columns is None or columns[:7] != ['readID', 'chrom1', 'pos1', 'chrom2', 'pos2', 'strand1', 'strand2'] or 'pair_type' not in columns:
                raise ValueError('Missing or unsupported standard pairs header')
            fields = line.decode().rstrip('\n').split('\t')
            if len(fields) != len(columns) or not fields[0]:
                raise ValueError(f'Malformed contact at line {line_number}')
            for chrom, pos, strand in ((fields[1], fields[2], fields[5]), (fields[3], fields[4], fields[6])):
                if chrom not in sizes or not 1 <= int(pos) <= sizes[chrom] or strand not in ('+', '-'):
                    raise ValueError(f'Invalid mapped 1-based endpoint at line {line_number}')
            pt = fields[columns.index('pair_type')]
            if len(pt) != 2 or pt == 'DD':
                raise ValueError(f'Invalid/duplicate pair_type at line {line_number}')
            pair_types[pt] += 1
            counts['cis' if fields[1] == fields[3] else 'trans'] += 1
            records += 1
            if records % 10_000_000 == 0:
                print(f'Validated {records} contacts', flush=True)
    if header_sizes != sizes:
        raise ValueError('Pairs header chromosome lengths differ from index chrom.sizes')
    if not records or records != stats['total_nodups']:
        raise ValueError(f'EOF contact count {records} != dedup total_nodups {stats["total_nodups"]}')
    for key in ('cis', 'trans'):
        if key in stats and counts[key] != stats[key]:
            raise ValueError(f'{key} count differs from dedup.stats')
    after = {str(p): signature(p) for p in (pairs, sizes_path, stats_path, bwa_log)}
    if before != after:
        raise ValueError('Input changed during validation')
    return {'status': 'PASS', 'records': records, 'pair_types': dict(pair_types),
            'counts': dict(counts), 'dedup_totals': stats, 'inputs': before,
            'coordinate_convention': '1-based; original pairs unchanged',
            'checks': ['BWA completion footer', 'full EOF structural/endpoint scan',
                       'no DD records', 'dedup totals and cis/trans reconciliation', 'stable input metadata'],
            'limitation': 'Uses existing pairtools duplicate calls; does not repeat positional deduplication.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    p.add_argument('assembly', choices=['hifiasm', 'verkko'])
    p.add_argument('--mapping-job', required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    # afterany permits recovery of valid pairs if only the legacy Cooler stage failed.
    accounting = subprocess.check_output(['sacct', '-X', '-n', '-P', '-j', args.mapping_job,
                                         '--format=JobID,State,ExitCode'], text=True).strip()
    lines = [line.split('|') for line in accounting.splitlines() if line.split('|')[0] == args.mapping_job]
    if len(lines) != 1 or not lines[0][1].split()[0] in ('COMPLETED', 'FAILED', 'TIMEOUT', 'CANCELLED', 'OUT_OF_MEMORY', 'NODE_FAIL'):
        raise ValueError('Mapping job is not confirmed terminal: ' + accounting)
    work = args.root / args.assembly
    result = validate(work/'results/valid_dedup.pairs', work/'index/chrom.sizes',
                      work/'results/dedup.stats', work/'results/bwa.log')
    result.update(mapping_accounting=accounting, validation_job=os.environ.get('SLURM_JOB_ID'),
                  completed_utc=datetime.now(timezone.utc).isoformat())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
    print(json.dumps({k: result[k] for k in ('status', 'records', 'pair_types', 'counts', 'mapping_accounting')}, indent=2))


if __name__ == '__main__':
    main()
