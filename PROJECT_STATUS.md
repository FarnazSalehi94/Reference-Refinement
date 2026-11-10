# Project status

Observed 2026-11-10 (HPC sacct; source-file checks also required for result imports).

## Quality-evaluation classification

| Evaluation | Scientific status | Execution / replacement evidence |
|---|---|---|
| Previous Merqury, QV and read-kmer estimates/spectra | **Historical/preliminary; not current endorsed estimates** | Earlier jobs 2871273/2871275 completed; outputs preserved |
| Replacement Merqury, QV and k-mer evaluation | **Planned; not confirmed running** | No replacement job IDs or new results available; no analyses submitted by this documentation update |

A completed job below records execution, not acceptance of its estimates. Reclassification does not prove prior calculations incorrect. See [evaluation policy](configs/evaluation_policy.json).

## Scheduler snapshot

| Job | Analysis | State | Exit code |
|---|---|---|---|
| 2871178 | Hifiasm hybrid_v1 assembly | COMPLETED | 0:0 |
| 2871179 | Verkko assembly | COMPLETED | 0:0 |
| 2871197 | Hifiasm versus GRCr8 | COMPLETED | 0:0 |
| 2871272 | Verkko versus GRCr8 | COMPLETED | 0:0 |
| 2871273 | Combined HiFi k=21 database — historical/preliminary outputs | COMPLETED | 0:0 |
| 2871274 | Official GRCr8 verification | COMPLETED | 0:0 |
| 2871275 | Merqury (three assemblies) — historical/preliminary outputs | COMPLETED | 0:0 |
| 2871277 | Consistent gap/contiguity statistics | COMPLETED | 0:0 |
| 2871279 | Hifiasm Hi-C mapping (legacy Cooler stage) | RUNNING | — (not final) |
| 2871280 | Verkko Hi-C mapping (legacy Cooler stage) | PENDING | — (not final) |
| 2871281 | Obsolete Hi-C plot job | CANCELLED by 1011 | 0:0 |
| 2871282 | Pretext maps/snapshots | PENDING | — (not final) |
| 2871285 | Hifiasm pairs EOF validation | PENDING | — (not final) |
| 2871286 | Verkko pairs EOF validation | PENDING | — (not final) |
| 2871287 | Deferred corrected Cooler submission | PENDING | — (not final) |

## Interpretation and remaining work

- Assembly runs, reference comparisons and gap statistics are completed; small source outputs passed import checks.
- Previous Merqury/QV/k-mer outputs are historical/preliminary and preserved, not current quality conclusions. Repeat evaluation is planned; it has not been confirmed started.
- Hi-C mapping job completion is not corrected-matrix validation. Legacy Cooler outputs are excluded.
- Pair validation, Pretext and corrected matrix status must be read independently. Pretext completion does not imply visual review.
- Full pairs validation and successful matrix QC are mandatory before corrected Hi-C figures enter the curated index.
- BUSCO, contamination screening, repeat/missing-sequence characterization and independent read-supported refinement remain planned.
- No automatic assembly correction, scaffolding or sequencing target design is performed by synchronization.
- Cross-animal dataset provenance and reference-alignment ambiguity remain interpretation limitations.

See [results](results/README.md), [figures](figures/README.md), and [Hi-C workflow](analyses/hic-contact-maps/README.md).
