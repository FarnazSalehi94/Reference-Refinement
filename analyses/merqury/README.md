# Merqury, QV and read-kmer evaluation

## Previous evaluation: historical/preliminary

**The previous numerical estimates and spectra are retained for provenance, not endorsed as current assembly-quality results.** The owner plans to repeat these analyses. Reclassification does not, by itself, demonstrate an error in the prior calculations.

Historical execution evidence: job 2871275 completed three evaluations using the same combined meryl k=21 database from four HiFi runs (database job 2871273). The recorded solid threshold was 9. Computational completion is distinct from scientific acceptance as a current estimate.

| Assembly | Previous QV — historical/preliminary | Previous solid-read k-mer completeness (%) — historical/preliminary |
|---|---:|---:|
| Hifiasm primary | 64.2134 | 99.7315 |
| Verkko main | 58.9038 | 99.7451 |
| GRCr8 | 68.5593 | 99.7160 |

Unmodified [original summary](../../results/merqury/merqury_summary.tsv), [result-status note](../../results/merqury/README.md), and [figure index](../../figures/README.md) preserve these outputs. Prior commands remain under `scripts/`; [source methodology notes](README.source.md) are an unchanged dated record, not the protocol for a new evaluation.

Completeness is a fraction of distinct solid read k-mers, not genome bases. Missing/overrepresented k-mer localization and copy-number interpretation remain unresolved. Do not rank final assembly accuracy/completeness using these preliminary values or label assembly-only k-mers as confirmed errors.

## Replacement evaluation: planned

No replacement Merqury/QV/k-mer run has been confirmed started, submitted or completed. There are **no replacement job IDs or new estimates** to report. Hi-C mapping is a separate ongoing workflow, not evidence of a new k-mer evaluation.

Before submission, agree and document dataset provenance, read database construction/filtering, k, assembly/reference identities, software versions, parameters, interpretation and SLURM resources. Use fresh versioned outputs and preserve prior databases/results. Validate and review replacement results before promoting them to current status. This documentation update submits no analyses.

The persistent classification is recorded in [configs/evaluation_policy.json](../../configs/evaluation_policy.json). Synchronization must preserve the historical/preliminary labels even while earlier SLURM jobs remain COMPLETED.
