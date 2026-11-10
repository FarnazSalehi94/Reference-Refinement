#!/usr/bin/env python3
"""Tiny installed-tool regression test; no project read files or matrices are changed."""
from collections import Counter
from pathlib import Path
import subprocess
import tempfile

import cooler
import numpy as np

from plot_maps import bin_layout, render
from validate_cooler import check_matrix, check_sample
from validate_pairs import validate

PAIRTOOLS = '/home/salehi/miniconda3/envs/hic_contact/bin/pairtools'
COOLER = '/home/salehi/miniconda3/envs/moddotplot/bin/cooler'


def main():
    with tempfile.TemporaryDirectory(prefix='bn_hic_regression_') as tmp:
        root = Path(tmp)
        sizes = root / 'chrom.sizes'
        sizes.write_text('A\t20001\nB\t15000\n')
        sam = root / 'contacts.sam'
        lines = ['@HD\tVN:1.6\tSO:queryname\n', '@SQ\tSN:A\tLN:20001\n', '@SQ\tSN:B\tLN:15000\n']
        positions = [(1, 1), (9999, 9999), (10000, 10000), (10001, 10001), (20001, 15000)]
        for i, (a, b) in enumerate(positions):
            lines.extend([f'r{i}\t65\tA\t{a}\t60\t1M\tB\t{b}\t0\tA\tI\n',
                          f'r{i}\t129\tB\t{b}\t60\t1M\tA\t{a}\t0\tA\tI\n'])
        sam.write_text(''.join(lines))
        pairs = root / 'contacts.pairs'
        subprocess.run([PAIRTOOLS, 'parse', '--chroms-path', str(sizes), '--assembly', 'fixture',
                        '--min-mapq', '30', '--walks-policy', '5unique', '--drop-sam',
                        '--output', str(pairs), str(sam)], check=True)
        rows = [line.split() for line in pairs.read_text().splitlines() if not line.startswith('#')]
        assert [(int(r[2]), int(r[4])) for r in rows] == positions
        assert all(r[7] == 'UU' for r in rows)
        before = pairs.read_bytes()
        stats = root / 'dedup.stats'
        stats.write_text('total\t5\ntotal_mapped\t5\ntotal_dups\t0\ntotal_nodups\t5\ntotal_unmapped\t0\ntotal_single_sided_mapped\t0\ncis\t0\ntrans\t5\n')
        bwa = root / 'bwa.log'
        bwa.write_text('[main] CMD: bwa mem fixture\n[main] Real time: 1 sec\n')
        assert validate(pairs, sizes, stats, bwa)['records'] == 5
        stats.write_text(stats.read_text().replace('total_nodups\t5', 'total_nodups\t4'))
        try:
            validate(pairs, sizes, stats, bwa)
        except ValueError:
            pass
        else:
            raise AssertionError('Inconsistent dedup counts were accepted')
        print('PASS: full pairs validator accepts valid EOF/counts and rejects inconsistent statistics')
        command = [COOLER, 'cload', 'pairs', '--input-copy-status', 'unique',
                   '-c1', '2', '-p1', '3', '-c2', '4', '-p2', '5', f'{sizes}:10000', str(pairs)]
        dest = root / 'correct.cool'
        subprocess.run(command + [str(dest)], check=True)
        c = cooler.Cooler(str(dest))
        result = check_matrix(c, {'A': 20001, 'B': 15000})
        assert result['bins'] == 5 and result['stored_contact_count'] == 5
        expected = Counter({(0, 3): 3, (1, 4): 1, (2, 4): 1})
        observed = Counter({(int(r.bin1_id), int(r.bin2_id)): int(r.count) for r in c.pixels()[:].itertuples()})
        assert observed == expected
        sample = check_sample(pairs, sizes, c, COOLER)
        assert sample['records'] == 5
        bad = root / 'incorrect.cool'
        subprocess.run(command[:3] + ['--zero-based'] + command[3:] + [str(bad)], check=True)
        assert not cooler.Cooler(str(bad)).pixels()[:].equals(c.pixels()[:]), 'Negative control failed'
        assert bin_layout(c) == [('A', 0, 3), ('B', 3, 5)]
        ticks = [(s + e - 1) / 2 for _, s, e in bin_layout(c)]
        assert ticks == [1.0, 3.5]
        # Synthetic weights exercise rendering only; this is NOT biological ICE estimation.
        with c.open('a') as group:
            w = group['bins'].create_dataset('weight', data=np.full(5, .1))
            w.attrs['converged'] = True
        scales = []
        render(c, None, root / 'fixture', 'SYNTHETIC regression fixture',
               (ticks, ['A', 'B']), [2.5], 'Assembly bin index', scales)
        assert scales[0]['balanced'] is False and scales[1]['balanced'] is True
        assert scales[1]['vmin'] < 1, 'Balanced intensities must not be clipped at one'
        assert pairs.read_bytes() == before
        print('PASS: installed pairtools emits 1-based boundary positions unchanged')
        print('PASS: 5 contacts -> 5 bins; exact pixels (0,3):3, (1,4):1, (2,4):1')
        print('PASS: --zero-based negative control changes pixels')
        print('PASS: contig extents [0,3), [3,5); ticks 1,3.5; boundary 2.5')
        print('PASS: raw and balanced PNG/PDF rendering, balanced values below one, pairs unchanged')
        print('LIMIT: actual project pairs remain unavailable; full matrix QC must run in SLURM')


if __name__ == '__main__':
    main()
