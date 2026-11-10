# Hi-C structural evaluation — ongoing

Current exact code snapshots are under `scripts/` and `pretext/scripts/`. The [source workflow notes](README.source.md) and [correction execution record](corrections/20261109_pairs1based_v1/EXECUTION.md) document commands and resources. They are dated HPC records; use [live curated status](../../PROJECT_STATUS.md) for scheduler updates.

## Current safety gates

1. Preserve the existing BWA/pairtools jobs and original pairs.
2. Full EOF validation after each producer terminates: structural validity, coordinate bounds, dedup totals, BWA completion and stable inputs.
3. Pretext runs after both validated pairs, independently of corrected Cooler/plot success.
4. Corrected matrix-only jobs use standard 1-based pairs (no `--zero-based`) in a separate revision directory.
5. Validate dimensions, bin boundaries, exact contact totals, a bounded sample and ICE balancing.
6. Generate raw and balanced maps using Cooler bin offsets for labels; review interpretation manually.

Legacy matrices from original submitted jobs are excluded. No corrected heatmap is claimed complete until its job and validation outputs support that statement. A successful plot is not a diagnosis of misassembly.

The approved execution snapshots remain on HPC. These repository files are current script snapshots and are not a replacement for submitted-job provenance. No assemblies are changed and no scaffolding is performed by this workflow.
