# Reproducibility

## Scope

This repository records an existing research project, not an instruction to rerun it from scratch. Exact imported scripts retain HPC absolute paths and original output naming. They may refer to other files at their original source locations; repository organization does not rewrite runtime dependencies. The [import manifest](../metadata/import_manifest.tsv) maps each snapshot back to that layout.

Current scientific tree: `/moosefs/salehi/ref-refine/assemblies/`. Archived experiments may be consulted but new workflows must not depend on raid5. The historical `analyses/grcr8-comparison/hifiasm/scripts/compare.slurm` has such a reference dependency: retain it as evidence, do not resubmit it unchanged. Use the verified local GRCr8 reference for future work after path/index review.

## Before any execution

1. Read [current status](../PROJECT_STATUS.md); check `squeue` and `sacct`. Do not duplicate active/completed work.
2. Confirm public accessions, validated local data, sample limitations and reference identity.
3. Review exact tool identity, particularly experimental hifiasm hybrid_v1, conda paths and resource requests. The hybrid source commit/build is still an open reproducibility item.
4. Preserve original outputs and choose a fresh run/revision directory. Do not run source snapshots directly from the curated checkout assuming portability.
5. Discuss scientific purpose and resources before expensive SLURM submission. No heavy login-node analysis.
6. Record job IDs, commands, versions, output checks and interpretation in project documentation; then curate selected small results.

## Computational definitions

- Gap/contig metrics: source `analysis/gap_stats/gap_stats.py`; split at every N-run, including lower-case n.
- Reference alignment: minimap2 asm5, `--secondary=yes -N 50 -c`; primary target-span unions, MAPQ ≥20 conservative view. BED coordinates in HPC results are 0-based half-open.
- K-mers: meryl k=21 count per HiFi run followed by union-sum; common database for all three Merqury evaluations.
- Hi-C: BWA-MEM `-5SP -T0`, pairtools MAPQ ≥30, 5unique and deduplication. Original pairs remain 1-based; Cooler default conversion is required.

## Auditability and limitations

Small imported source/result files have SHA256 provenance. Raw data and assembly checksums are not recomputed by synchronization. Exact full environment lockfiles and hybrid source/build provenance have not been recovered; the software table is an inventory, not a claim of bitwise reproducibility. Existing figure generation is complete where indexed, but structural interpretation is separate.

Repository maintenance requires only Python 3.7+ and Git; scientific scripts have their own environment requirements. No scientific dependencies are installed by synchronization.
