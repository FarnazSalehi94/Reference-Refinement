# Scientific result index

Only small selected outputs are versioned. **Jobs 2871273/2871274/2871275 form the latest completed BN k-mer/reference/Merqury evaluation (9 November 2026).** QV/completeness outputs are retained with preliminary scientific interpretation and further validation planned. Older historical analyses are separate; completion is not final biological validation. Source-relative locations, evidence jobs and checksums are in [metadata/import_manifest.tsv](../metadata/import_manifest.tsv).

| Directory | Contents | Evidence |
|---|---|---|
| `assembly/` | Gap/contiguity metrics and latest completed BN QV/completeness estimates, interpretation preliminary | 2871277; quality evaluation 2871275 |
| `merqury/` | Latest completed BN HiFi k=21 QV, error/k-mer counts and completeness; interpretation preliminary | 2871273/2871274/2871275 completed 2026-11-09 |
| `grcr8-comparison/hifiasm/` | Primary/hap1/hap2 chromosome and query coverage | 2871197 |
| `grcr8-comparison/verkko/` | Four-assembly comparison including Verkko | 2871272 |
| `chromosomes/` | Per-contig chromosome-alignment summary | 2871272 |

[Combined metrics](assembly/COMPARISON.md) and the README retain the exact numerical values from the latest completed evaluation with preliminary-interpretation labels. Further validation is planned, with no later estimates or job IDs verified. Older legacy outputs must not be conflated with these BN results. Tables are observations under specific definitions, not proof of chromosome correctness or missing DNA. See [interpretation](../docs/INTERPRETATION.md).

Future `hic/<revision>/<assembly>/` reports are imported only after a successful corrected workflow, matrix validation, sample checks and converged balancing. Legacy matrices, unfinished figures, raw reads, assembly FASTAs, alignment files, k-mer databases and complete logs are excluded.
