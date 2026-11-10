# Scientific result index

Only small selected completed results are versioned. Source-relative locations, evidence jobs and checksums are in [metadata/import_manifest.tsv](../metadata/import_manifest.tsv).

| Directory | Contents | Evidence |
|---|---|---|
| `assembly/` | Consistent gap metrics; generated combined comparison | 2871277; Merqury 2871275 |
| `merqury/` | Common-HiFi k=21 QV and solid-kmer completeness | 2871275 |
| `grcr8-comparison/hifiasm/` | Primary/hap1/hap2 chromosome and query coverage | 2871197 |
| `grcr8-comparison/verkko/` | Four-assembly comparison including Verkko | 2871272 |
| `chromosomes/` | Per-contig chromosome-alignment summary | 2871272 |

[Combined metrics](assembly/COMPARISON.md) are regenerated from the two verified small source tables; the README uses the same data. Tables are observations under specific definitions, not proof of chromosome correctness or missing DNA. See [interpretation](../docs/INTERPRETATION.md).

Future `hic/<revision>/<assembly>/` reports are imported only after a successful corrected workflow, matrix validation, sample checks and converged balancing. Legacy matrices, unfinished figures, raw reads, assembly FASTAs, alignment files, k-mer databases and complete logs are excluded.
