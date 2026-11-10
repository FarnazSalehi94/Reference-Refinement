#!/usr/bin/env python3
"""Conservative publication guard; heuristic secret scanning does not replace human review."""
import argparse
import csv
import hashlib
import io
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 5 * 1024 * 1024
ALLOWED = {'.md', '.py', '.slurm', '.json', '.tsv', '.yaml', '.yml', '.svg', '.png'}
# Assemble patterns so this scanner's own source does not look like a leaked key.
SECRETS = [
    re.compile(r'-----BEGIN ' + r'(?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(r'gh[pousr]' + r'_[A-Za-z0-9]{30,}'),
    re.compile(r'github_' + r'pat_[A-Za-z0-9_]{30,}'),
    re.compile(r'AKIA' + r'[0-9A-Z]{16}'),
    re.compile(r'https?://[^\s/:]+:[^\s/@]+@'),
    re.compile(r'(?im)^\s*(?:export\s+)?(?:password|passwd|api_key|access_token|secret_key)\s*[:=]\s*[\"\']?[^\s\"\'{}$]{8,}')
]


def inspect(path, data):
    p = Path(path)
    if p.is_absolute() or '..' in p.parts or p.parts[0] in ('inputs', 'tools', 'logs', 'data', 'databases'):
        raise ValueError('Forbidden path: ' + path)
    if any(part.lower().startswith(('.env', 'credentials', 'secrets', 'id_rsa', 'id_ed25519')) for part in p.parts):
        raise ValueError('Sensitive filename: ' + path)
    if len(data) > MAX_BYTES:
        raise ValueError('File exceeds 5 MiB: ' + path)
    if p.suffix not in ALLOWED and p.name not in ('.gitignore', '.gitattributes', 'pre-commit'):
        raise ValueError('Non-allowlisted file type: ' + path)
    if p.suffix in ('.png', '.svg') and p.parts[0] != 'figures':
        raise ValueError('Figures must be curated below figures/: ' + path)
    if p.suffix == '.png':
        if not data.startswith(b'\x89PNG\r\n\x1a\n'):
            raise ValueError('Invalid PNG: ' + path)
        return
    text = data.decode('utf-8')
    if '\x00' in text:
        raise ValueError('Unexpected binary: ' + path)
    for pattern in SECRETS:
        if pattern.search(text):
            raise ValueError('Possible credential in ' + path + ' (value not printed)')
    if p.suffix == '.svg' and re.search(r'<script\b|<foreignObject\b|\bonload\s*=', text, re.I):
        raise ValueError('Active SVG content: ' + path)


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def check(staged=False):
    if staged:
        names = git('diff', '--cached', '--name-only', '--diff-filter=ACMR', '-z').decode().split('\0')
    else:
        names = git('ls-files', '-z').decode().split('\0')
    for name in filter(None, names):
        mode = git('ls-files', '-s', '--', name).decode().split()[0]
        if mode not in ('100644', '100755'):
            raise ValueError('Symlink/submodule not publishable: ' + name)
        data = git('show', ':' + name) if staged else (ROOT / name).read_bytes()
        inspect(name, data)
    manifest = 'metadata/import_manifest.tsv'
    tracked = set(filter(None, git('ls-files', '-z').decode().split('\0')))
    if manifest in tracked:
        text = git('show', ':' + manifest).decode() if staged else (ROOT / manifest).read_text()
        for row in csv.DictReader(io.StringIO(text), delimiter='\t'):
            name = row['repository_path']
            if name not in tracked:
                raise ValueError('Manifest file missing from index: ' + name)
            data = git('show', ':' + name) if staged else (ROOT / name).read_bytes()
            if hashlib.sha256(data).hexdigest() != row['sha256']:
                raise ValueError('Imported source hash differs: ' + name)
    print('Publication guard PASS (' + ('staged index' if staged else 'tracked working tree') + '; imported hashes verified)')


def links():
    failures = []
    tracked = set(filter(None, git('ls-files', '-z').decode().split('\0')))
    for p in ROOT.rglob('*.md'):
        rel = p.relative_to(ROOT).as_posix()
        # Exact historical/source snapshots may contain obsolete references; not current navigation.
        if '/history/' in rel or '.source.' in rel or rel.startswith('metadata/source_records/') or '/corrections/' in rel:
            continue
        for target in re.findall(r'!?\[[^\]]*\]\(([^)\s]+)', p.read_text()):
            if target.startswith(('https://', 'http://', '#', 'mailto:')):
                continue
            dest = (p.parent / target.split('#')[0]).resolve()
            if not dest.exists() or ROOT.resolve() not in dest.parents:
                failures.append(rel + ' -> ' + target)
            elif dest.is_file() and dest.relative_to(ROOT).as_posix() not in tracked:
                failures.append(rel + ' -> untracked target ' + target)
    if failures:
        raise ValueError('Broken local links:\n' + '\n'.join(failures))
    print('Current-document local links PASS (archived snapshots excluded)')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--staged', action='store_true')
    p.add_argument('--links', action='store_true')
    args = p.parse_args()
    check(args.staged)
    if args.links:
        links()


if __name__ == '__main__':
    main()
