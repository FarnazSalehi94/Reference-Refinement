#!/usr/bin/env python3
"""Structural/count validation plus bounded, exact 1-based contact-bin validation."""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import tempfile

import cooler
import numpy as np


def check_matrix(c, sizes):
    assert list(c.chromsizes.items()) == list(sizes.items()), 'Chromosome order/length mismatch'
    bins = c.bins()[:]
    offset = 0
    layout = []
    for name, length in sizes.items():
        starts = np.arange(0, length, c.binsize)
        block = bins.iloc[offset:offset + len(starts)]
        assert (block['chrom'].astype(str) == name).all()
        assert np.array_equal(block.start, starts)
        assert np.array_equal(block.end, np.minimum(starts + c.binsize, length))
        assert c.extent(name) == (offset, offset + len(starts))
        layout.append([name, offset, offset + len(starts)])
        offset += len(starts)
    assert c.shape == (offset, offset)
    total = 0
    previous = (-1, -1)
    for start in range(0, c.info['nnz'], 1_000_000):
        p = c.pixels()[start:start + 1_000_000]
        a, b, n = (p[k].to_numpy() for k in ('bin1_id', 'bin2_id', 'count'))
        assert ((0 <= a) & (a <= b) & (b < offset)).all()
        assert np.isfinite(n).all() and (n > 0).all() and (n == np.floor(n)).all()
        if len(p):
            assert (int(a[0]), int(b[0])) > previous
            assert ((a[1:] > a[:-1]) | ((a[1:] == a[:-1]) & (b[1:] > b[:-1]))).all()
            previous = (int(a[-1]), int(b[-1]))
        total += int(n.sum())
    assert total == c.info['sum']
    result = {'bins': offset, 'nnz': c.info['nnz'], 'stored_contact_count': total, 'layout': layout}
    with c.open('r') as group:
        if 'weight' in group['bins']:
            w = group['bins/weight'][:]
            result['finite_weights'] = int(np.isfinite(w).sum())
            result['balance_converged'] = bool(group['bins/weight'].attrs.get('converged', False))
    return result


def check_sample(pairs, sizes_path, c, executable, limit=10000):
    sizes = dict(c.chromsizes.items())
    expected = Counter()
    rows = []
    columns = None
    with open(pairs) as f:
        for line in f:
            if line.startswith('#columns:'):
                columns = line.split(':', 1)[1].split()
            if line.startswith('#'):
                continue
            a = line.split()
            assert columns is not None and columns[:7] == ['readID', 'chrom1', 'pos1', 'chrom2', 'pos2', 'strand1', 'strand2']
            assert len(a) == len(columns)
            if 'pair_type' in columns:
                assert a[columns.index('pair_type')] != 'DD', 'Duplicate in deduplicated input'
            ids = []
            for chrom, text in ((a[1], a[2]), (a[3], a[4])):
                pos = int(text)
                assert chrom in sizes and 1 <= pos <= sizes[chrom], 'Nonstandard/unmapped position'
                ids.append(c.offset(chrom) + (pos - 1) // c.binsize)
            expected[tuple(sorted(ids))] += 1
            rows.append(line)
            if len(rows) >= limit:
                break
    assert rows, 'No finished pairs available'
    # Exact aggregation of the bounded sample through the installed Cooler CLI.
    with tempfile.TemporaryDirectory(prefix='cooler_sample_') as tmp:
        sample = Path(tmp) / 'sample.pairs'
        sample.write_text(''.join(rows))
        dest = Path(tmp) / 'sample.cool'
        subprocess.run([executable, 'cload', 'pairs', '--input-copy-status', 'unique',
                        '-c1', '2', '-p1', '3', '-c2', '4', '-p2', '5',
                        f'{sizes_path}:{c.binsize}', str(sample), str(dest)], check=True)
        p = cooler.Cooler(str(dest)).pixels()[:]
        observed = Counter({(int(r.bin1_id), int(r.bin2_id)): int(r.count) for r in p.itertuples()})
        assert observed == expected, '1-based sample aggregation mismatch'
    # Each sample pixel must also be supported by the complete matrix.
    for (a, b), n in expected.items():
        assert c.matrix(balance=False)[a, b] >= n
    return {'records': len(rows), 'sample_pixels': len(expected), 'exact_bin_count_match': True,
            'coordinate_formula': 'chromosome_bin_offset + (pairs_position - 1) // bin_size'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('work', type=Path)
    p.add_argument('pairs', type=Path)
    p.add_argument('sizes', type=Path)
    p.add_argument('--cooler', required=True)
    p.add_argument('--expected-contacts', type=int, required=True, help='Full validated pairs EOF count')
    args = p.parse_args()
    sizes = dict((a, int(b)) for a, b in (line.split() for line in args.sizes.read_text().splitlines()))
    base = cooler.Cooler(str(args.work / 'cool/contacts.10000.cool'))
    result = {'base': check_matrix(base, sizes)}
    assert result['base']['stored_contact_count'] == args.expected_contacts, 'Contacts lost/added compared with full validated pairs'
    result['validated_pairs_contacts'] = args.expected_contacts
    result['sample'] = check_sample(args.pairs, args.sizes, base, args.cooler)
    result['resolutions'] = {}
    for resolution in (10000, 50000, 250000, 1000000):
        c = cooler.Cooler(f'{args.work}/cool/contacts.mcool::resolutions/{resolution}')
        qc = check_matrix(c, sizes)
        assert qc['stored_contact_count'] == result['base']['stored_contact_count'], 'Contact loss during coarsening'
        assert qc.get('balance_converged') and qc.get('finite_weights', 0) > 0, 'Unusable balancing weights'
        result['resolutions'][resolution] = qc
    result['note'] = 'Count conservation against prior full pairs EOF validation and across resolutions. Sample is first 10000 records, not random.'
    (args.work / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
