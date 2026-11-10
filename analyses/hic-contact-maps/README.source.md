# Brown Norway Hi-C contact-map analysis

This workflow remaps the validated paired Hi-C FASTQs independently to the exact hifiasm primary and Verkko main assembly FASTAs. It does not scaffold, split, or alter either assembly. Hi-C was used during assembly, so contact anomalies below are hypotheses for review rather than proof of misassembly.

## Correction notice — 2026-11-09

See `corrections/20261109_pairs1based_v1/README.md` for the coordinate correction, submitted-job audit, regression tests, and unsubmitted regeneration plan. The legacy `<assembly>/cool/` paths are **not approved for interpretation**: submitted mapping jobs 2871279 and 2871280 contain the old `--zero-based` command even though the disk script below has been fixed. Corrected matrices/figures go into a new revision directory; original pairs and legacy outputs are preserved.

## Mapping and contact generation

For each assembly the SLURM script runs:

```bash
bwa mem -5SP -T0 -t 32 -K 100000000 INDEX inputs/ERR5309023_1.fastq inputs/ERR5309023_2.fastq \
  | pairtools parse --assembly ASSEMBLY --chroms-path chrom.sizes --min-mapq 30 --walks-policy 5unique --nproc-in 8 --nproc-out 8 \
  | pairtools sort --nproc 16 --tmpdir WORK/tmp \
  | pairtools dedup --mark-dups --output-stats WORK/results/dedup.stats --nproc-in 8 --nproc-out 8 \
  | pairtools split --output-pairs WORK/results/valid_dedup.pairs --output-sam /dev/null
cooler cload pairs --assembly ASSEMBLY --input-copy-status unique \
  -c1 2 -p1 3 -c2 4 -p2 5 chrom.sizes:10000 WORK/results/valid_dedup.pairs WORK/cool/contacts.10000.cool
cooler zoomify --nproc 8 --chunksize 5000000 --resolutions 10000,50000,250000,1000000 \
  --balance --balance-args '--nproc 8' --out WORK/cool/contacts.mcool WORK/cool/contacts.10000.cool
```

The BWA index, sorted-pair temporary files, mapping logs, deduplicated pairs, and cooler files are placed under the corresponding assembly subdirectory here. Inputs and original assemblies remain read-only.

## Figures and candidate summaries

After corrected matrices pass validation, `scripts/plot.slurm` requires an explicit `REVISION` and generates separate ICE-balanced and raw-count whole-assembly 1 Mb maps and individual maps at 50 kb for up to 16 longest contigs (at least 15 Mb), as PNG and PDF. Figures use logarithmic color scales with per-panel limits recorded in `reports/plot_scales.json`; color intensities must not be quantitatively compared across panels. Masked/zero cells are gray. Overview ticks and contig boundary lines use Cooler bin offsets, not cumulative base-pair lengths. Corrected outputs are isolated under `corrections/<revision>/<assembly>/`. Existing figure/report directories are never overwritten. Reports include contig contact support and low-marginal-contact windows. These are screening signals only: restriction-site distribution, sequence composition, mappability, and assembly-induced Hi-C data selection can all affect contact intensity. Inspect map structure together with independent evidence before making any assembly changes.

## Resources and ordering

Each mapping job requests 32 CPUs, 192 GB RAM, and 7 days on `allnodes`; temporary sorting data are stored below this analysis directory. The Verkko mapping job is submitted with an `afterok` dependency on hifiasm. Plot generation requests 8 CPUs, 64 GB RAM, and 2 days, and is submitted after both map jobs.
