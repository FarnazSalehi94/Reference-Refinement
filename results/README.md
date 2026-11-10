# Scientific result index

Only small selected outputs are versioned. **Previous Merqury, QV and read-kmer outputs are historical/preliminary**, retained for provenance while repeat evaluation is planned. File verification and computational completion do not make those estimates current endorsed quality conclusions. Source-relative locations, evidence jobs and checksums are in [metadata/import_manifest.tsv](../metadata/import_manifest.tsv).

| Directory | Contents | Evidence |
|---|---|---|
| `assembly/` | Current gap/contiguity metrics; combined TSV also retains historical/preliminary QV/completeness columns | 2871277; historical quality estimates from 2871275 |
| `merqury/` | Historical/preliminary HiFi k=21 QV, error/k-mer counts and completeness; not replacement results | Historical execution 2871275 |
| `grcr8-comparison/hifiasm/` | Primary/hap1/hap2 chromosome and query coverage | 2871197 |
| `grcr8-comparison/verkko/` | Four-assembly comparison including Verkko | 2871272 |
| `chromosomes/` | Per-contig chromosome-alignment summary | 2871272 |

[Combined metrics](assembly/COMPARISON.md) retain the previous numerical values with explicit historical quality labels. The headline README table includes contiguity/gap metrics only; it does not present previous QV/completeness values as current conclusions. The repeat quality evaluation is planned, with no replacement estimates or job IDs. Tables are observations under specific definitions, not proof of chromosome correctness or missing DNA. See [interpretation](../docs/INTERPRETATION.md).

Future `hic/<revision>/<assembly>/` reports are imported only after a successful corrected workflow, matrix validation, sample checks and converged balancing. Legacy matrices, unfinished figures, raw reads, assembly FASTAs, alignment files, k-mer databases and complete logs are excluded.
