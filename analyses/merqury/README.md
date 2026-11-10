# Read-kmer accuracy and completeness — completed

Job 2871275 completed all three evaluations using the same combined meryl k=21 database from all four HiFi runs (build job 2871273). Solid threshold recorded in each result directory: 9.

[QV/completeness table](../../results/merqury/merqury_summary.tsv) and [spectra index](../../figures/README.md) are available. Source commands are under `scripts/`; [unmodified methodology notes](README.source.md) describe database construction and limitations.

Hifiasm QV 64.2134 / completeness 99.7315%; Verkko 58.9038 / 99.7451%; GRCr8 68.5593 / 99.7160%. Completeness is a fraction of distinct solid read k-mers, not reference bases. Missing/overrepresented k-mer localization and copy-number interpretation remain unfinished. Do not label assembly-only k-mers as confirmed errors without independent evidence.
