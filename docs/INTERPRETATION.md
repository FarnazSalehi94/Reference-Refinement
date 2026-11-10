# Scientific interpretation and open questions

## Evaluation status

Previous Merqury/QV/read-kmer counts, completeness, error estimates and spectra are **historical/preliminary** because repeat evaluation is planned. Retain all outputs, but do not use them as current endorsed quality estimates or final assembly rankings. No replacement analysis is confirmed running and no new results/job IDs are available. This classification does not establish that previous calculations were incorrect. See [evaluation policy](../configs/evaluation_policy.json).

## Observations versus inference

- Zero N-run gaps and high contig N50 quantify continuity, not correctness or absence of collapsed repeats.
- Merqury QV is a read-kmer estimate. In the historical evaluation, all three assemblies used the same four-run HiFi k=21 database, solid threshold 9. Assembly-only k-mers are not automatically errors; cross-animal sequence, read errors and representation affect estimates.
- Reference coverage is a union of minimap2 primary target spans at MAPQ ≥20, including indels—not exact matched bases. Chromosome tables exclude nonchromosomal/mitochondrial sequences, although those sequences were present in alignment.
- Query aligned-base sums may overlap; distinct-contig target overlaps are candidates, not confirmed duplications. Secondary alignment reporting is limited by `-N 50`.
- Unaligned ≥100-kb regions may reflect repeats, low confidence, gaps, divergence, structural variation or missing sequence. Establish reliable read support and repeat/gap context before labeling missing DNA.

## Current signals

Hap2 minus hap1 X/Y high-confidence reference coverage is 152,853,988 + 49,162,941 = 202,016,929 bp. Their assembly-length difference is 244,015,470 bp. These are different quantities; coverage does not exactly account for the size difference. Sex-chromosome assignment is a supported explanation, not proof of biological deletion.

Chromosome 19 distinct-contig overlap is approximately 0.65 Mb in primary, 1.29 Mb in hap1, 3.85 Mb in hap2 and 1.80 Mb in Verkko. Mapping ambiguity and true copy representation must be distinguished using independent evidence.

## Hi-C safeguards

Pairtools positions are 1-based. Legacy submitted Cooler commands used `--zero-based`; legacy matrices and their plots are not valid for interpretation. Corrected loading must reuse validated original pairs without modifying them. Balanced/raw maps answer different questions; masked balanced bins are not evidence of absent DNA. Per-panel color limits prevent quantitative color comparisons between panels. Hi-C contributed to assembly and is not an independent validation dataset.

## Refinement policy

Preserve originals. Record each candidate in original coordinates, evidence sources, uncertainty and proposed change. Require independent spanning reads/contact structure/reference context as appropriate. Validate any new assembly against the original using accuracy, completeness, copy representation and structural evidence. No correction or scaffolding has been performed as part of curation.
