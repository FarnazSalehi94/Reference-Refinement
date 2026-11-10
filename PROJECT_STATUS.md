# Project status

Observed 2026-11-10 (HPC sacct; source-file checks also required for result imports).

## Quality-evaluation classification

| Evaluation | Execution status | Scientific interpretation / evidence |
|---|---|---|
| Latest Brown Norway HiFi k=21 / Merqury evaluation | **COMPLETED on 2026-11-09** | Jobs 2871273/2871275 and reference verification 2871274 succeeded; numerical outputs preserved; interpretation preliminary |
| Further quality validation | **Planned; not confirmed running** | No later evaluation job IDs or new results verified; no analyses submitted by this documentation update |
| Older legacy analyses | Separate historical provenance | Not the November BN evaluation; sample/assembly identity requires verification; DLD1 work is not BN evidence |

Completed execution and preliminary interpretation are separate labels. Planning further validation does not make the completed evaluation unfinished or merely historical. See [evaluation policy](configs/evaluation_policy.json).

## Scheduler snapshot

| Job | Analysis | State | Exit code |
|---|---|---|---|
| 2871178 | Hifiasm hybrid_v1 assembly | COMPLETED | 0:0 |
| 2871179 | Verkko assembly | COMPLETED | 0:0 |
| 2871197 | Hifiasm versus GRCr8 | COMPLETED | 0:0 |
| 2871272 | Verkko versus GRCr8 | COMPLETED | 0:0 |
| 2871273 | Combined HiFi k=21 database — latest completed BN evaluation; interpretation preliminary | COMPLETED | 0:0 |
| 2871274 | Official GRCr8 verification | COMPLETED | 0:0 |
| 2871275 | Merqury (three assemblies) — latest completed BN evaluation; interpretation preliminary | COMPLETED | 0:0 |
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
- Jobs 2871273/2871274/2871275 are the latest completed BN k-mer/reference/Merqury evaluation. QV/completeness outputs remain available with preliminary scientific interpretation; further validation is planned, not confirmed running.
- Hi-C mapping job completion is not corrected-matrix validation. Legacy Cooler outputs are excluded.
- Pair validation, Pretext and corrected matrix status must be read independently. Pretext completion does not imply visual review.
- Full pairs validation and successful matrix QC are mandatory before corrected Hi-C figures enter the curated index.
- BUSCO, contamination screening, repeat/missing-sequence characterization and independent read-supported refinement remain planned.
- No automatic assembly correction, scaffolding or sequencing target design is performed by synchronization.
- Cross-animal dataset provenance and reference-alignment ambiguity remain interpretation limitations.

See [results](results/README.md), [figures](figures/README.md), and [Hi-C workflow](analyses/hic-contact-maps/README.md).
