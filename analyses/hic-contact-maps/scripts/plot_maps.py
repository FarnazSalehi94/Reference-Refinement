#!/usr/bin/env python3
"""Plot only explicitly selected corrected matrices; never overwrite legacy figures."""
import argparse
import csv
import json
from pathlib import Path

import cooler
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


def bin_layout(c):
    """imshow pixel centers are integers; contig edges lie at offset - 0.5."""
    return [(name, *c.extent(name)) for name in c.chromnames]


def draw(a, title, labels, boundaries, path, balanced=False, xlabel='Assembly bin index'):
    a = np.asarray(a, dtype=float)
    positive = a[np.isfinite(a) & (a > 0)]
    if not len(positive):
        raise ValueError('No finite positive contacts: ' + title)
    # Raw counts have a natural minimum of one. Balanced values do not.
    vmin = float(np.percentile(positive, 1)) if balanced else 1.0
    vmax = max(float(np.percentile(positive, 99.8)), vmin * 1.01)
    fig, ax = plt.subplots(figsize=(11, 10))
    cmap = plt.get_cmap('magma').copy()
    cmap.set_bad('#d0d0d0')
    im = ax.imshow(np.ma.masked_where(~np.isfinite(a) | (a <= 0), a),
                   origin='upper', interpolation='nearest', cmap=cmap,
                   norm=LogNorm(vmin=vmin, vmax=vmax), rasterized=True)
    for edge in boundaries:
        ax.axvline(edge, color='white', lw=.25, alpha=.5)
        ax.axhline(edge, color='white', lw=.25, alpha=.5)
    ticks, names = labels
    ax.set_xticks(ticks, names, rotation=90, fontsize=6)
    ax.set_yticks(ticks, names, fontsize=6)
    # Explicit limits prevent labels/lines from expanding the displayed matrix.
    ax.set_xlim(-.5, a.shape[1] - .5)
    ax.set_ylim(a.shape[0] - .5, -.5)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(xlabel)
    label = 'ICE-balanced contact intensity (count × weight1 × weight2)' if balanced else 'Deduplicated Hi-C contacts per bin pair (raw count)'
    fig.colorbar(im, ax=ax, label=label, shrink=.72)
    fig.text(.5, .01, 'Log color scale; gray = zero or masked; limits scaled per panel (not quantitative across panels)',
             ha='center', fontsize=7)
    fig.tight_layout(rect=(0, .025, 1, 1))
    fig.savefig(path, dpi=300)
    fig.savefig(path.with_suffix('.pdf'))
    plt.close(fig)
    return {'file': path.name, 'balanced': balanced, 'vmin': vmin, 'vmax': vmax,
            'finite_positive_pixels': len(positive)}


def render(c, chrom, prefix, title, labels, boundaries, xlabel, scales):
    selector = c.matrix(balance=False, sparse=True)
    raw = (selector.fetch(chrom) if chrom else selector[:, :]).toarray()
    scales.append(draw(raw, title + ' — RAW', labels, boundaries,
                       prefix.with_name(prefix.name + '_raw.png'), xlabel=xlabel))
    # No fallback: absent, unconverged, or entirely masked weights must be visible.
    with c.open('r') as group:
        attrs = dict(group['bins/weight'].attrs)
    if not bool(attrs.get('converged', False)):
        raise RuntimeError('Unconverged ICE weights: ' + c.uri)
    weights = c.bins().fetch(chrom)['weight'].to_numpy() if chrom else c.bins()[:]['weight'].to_numpy()
    balanced = raw.astype(float) * weights[:, None] * weights[None, :]
    scales.append(draw(balanced, title + ' — ICE BALANCED', labels, boundaries,
                       prefix.with_name(prefix.name + '_balanced.png'), balanced=True, xlabel=xlabel))
    return raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('assembly', choices=['hifiasm', 'verkko'])
    parser.add_argument('--revision', required=True, help='Safe single directory name below corrections/')
    args = parser.parse_args()
    if Path(args.revision).name != args.revision or args.revision in ('.', '..'):
        parser.error('revision must be a single directory name')
    work = args.root / 'corrections' / args.revision / args.assembly
    mcool = work / 'cool/contacts.mcool'
    if not (work / 'validation.json').is_file():
        parser.error('Corrected matrix validation.json is required; legacy matrices are not accepted')
    out = work / 'figures'
    reports = work / 'reports'
    out.mkdir(exist_ok=False)
    reports.mkdir(exist_ok=False)
    c = cooler.Cooler(str(mcool) + '::resolutions/1000000')
    layout = bin_layout(c)
    ticks = [(start + end - 1) / 2 for name, start, end in layout if c.chromsizes[name] >= 20_000_000]
    names = [name for name, start, end in layout if c.chromsizes[name] >= 20_000_000]
    boundaries = [end - .5 for _, _, end in layout[:-1]]
    with (reports / 'overview_bin_layout.tsv').open('w') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(['contig', 'start_bin', 'end_bin_exclusive', 'tick_bin', 'right_edge'])
        for name, start, end in layout:
            w.writerow([name, start, end, (start + end - 1) / 2, end - .5])
    scales = []
    render(c, None, out / 'whole_assembly_1Mb', f'{args.assembly}: whole assembly (1 Mb bins)',
           (ticks, names), boundaries, 'Assembly bin index (contig order)', scales)
    c50 = cooler.Cooler(str(mcool) + '::resolutions/50000')
    long = c.chromsizes[c.chromsizes >= 15_000_000].sort_values(ascending=False).head(16)
    with (reports / 'contigs.tsv').open('w') as f, (reports / 'low_support_windows.bed').open('w') as bed:
        f.write('contig\tlength_bp\tbins_50kb\traw_median_bin_contacts\traw_min_bin_contacts\tlow_support_windows\n')
        for name, length in long.items():
            start, end = c50.extent(name)
            ticks = np.linspace(0, end - start - 1, min(6, end - start), dtype=int)
            labels = [f'{x * 50000 / 1e6:g}' for x in ticks]
            raw = render(c50, name, out / f'{name}_50kb', f'{args.assembly}: {name} (50 kb bins)',
                         (ticks, labels), [], 'Position along contig (Mb; bin starts)', scales)
            marginal = raw.sum(axis=0)
            sm = pd.Series(marginal).rolling(5, center=True, min_periods=1).median().to_numpy()
            inner = sm[10:-10] if len(sm) > 20 else sm
            med = float(np.median(inner))
            low = np.flatnonzero((sm < max(1, med * .1)) & (np.arange(len(sm)) >= 10)
                                 & (np.arange(len(sm)) < len(sm) - 10))
            runs = []
            for chunk in np.split(low, np.where(np.diff(low) > 1)[0] + 1):
                if len(chunk) >= 2:
                    runs.append((int(chunk[0]), int(chunk[-1]) + 1))
            f.write(f'{name}\t{length}\t{len(marginal)}\t{med:.2f}\t{float(np.min(inner)):.2f}\t{len(runs)}\n')
            for x, y in runs:
                bed.write(f'{name}\t{x*50000}\t{min(y*50000, int(length))}\traw marginal screening candidate; not proof of misassembly\n')
    # Contact totals from stored upper-triangle pixels, avoiding another full pairs scan.
    endpoints = np.zeros(len(c.chromnames), dtype=np.int64)
    cis = np.zeros_like(endpoints)
    bins = c.bins()[:]
    chrom_id = bins['chrom'].cat.codes.to_numpy()
    for start in range(0, c.info['nnz'], 1_000_000):
        p = c.pixels()[start:start + 1_000_000]
        a = chrom_id[p.bin1_id.to_numpy()]
        b = chrom_id[p.bin2_id.to_numpy()]
        counts = p['count'].to_numpy()
        np.add.at(endpoints, a, counts)
        np.add.at(endpoints, b, counts)
        same = a == b
        np.add.at(cis, a[same], counts[same])
    with (reports / 'contig_contact_support.tsv').open('w') as f:
        f.write('contig\tlength_bp\tendpoint_contacts\tcis_pairs\tintercontig_endpoint_contacts\tcontacts_per_Mb\n')
        for i, (name, length) in enumerate(c.chromsizes.items()):
            f.write(f'{name}\t{length}\t{endpoints[i]}\t{cis[i]}\t{endpoints[i]-2*cis[i]}\t{endpoints[i]/(length/1e6):.2f}\n')
    (reports / 'plot_scales.json').write_text(json.dumps(scales, indent=2) + '\n')


if __name__ == '__main__':
    main()
