# GRCr8 comparison — completed alignment screening

Hifiasm primary/hap1/hap2 were aligned in 2871197; Verkko was added in 2871272 using the same existing reference index. Commands: minimap2 asm5 with primary/secondary PAF, `-N 50 -c`; chromosome summaries use primary target-span unions with MAPQ ≥20. Reference chromosome accessions NC_086019.1–NC_086040.1 correspond to chromosomes 1–20, X and Y.

[Result tables](../../results/README.md), [coverage figures](../../figures/README.md), and [original definitions](interpretation.source.md) are available. Scripts remain organized by hifiasm and Verkko comparison. Chromosome-investigation notes are a separate preliminary interpretation, not confirmed duplications/deletions.

Historical `hifiasm/scripts/compare.slurm` references the old raid5 reference. It is retained as provenance only. New jobs must use the official local reference and reviewed paths/indexes. The official GRCr8 download passed MD5/gzip and sequence-ID/length checks, not a byte-identity comparison to the old index source. See [reproducibility](../../docs/REPRODUCIBILITY.md).
