# Latest completed Brown Norway Merqury and k-mer evaluation

## Completed on 9 November 2026

| Job | Task | Verified execution status |
|---|---|---|
| 2871273 | Four-run HiFi k=21 database, meryl union-sum | COMPLETED, exit 0:0; ended 16:25:26 |
| 2871274 | Official GRCr8 reference verification | COMPLETED, exit 0:0; ended 15:30:34 |
| 2871275 | Hifiasm primary, Verkko main and GRCr8 Merqury | COMPLETED, exit 0:0; ended 17:37:12 |

These are the **latest completed Brown Norway evaluations**. Expected QV/completeness files and spectra are present; all three internal Merqury logs end in `Done!`. Input links resolve to hifiasm run 2871178, Verkko run 2871179 and the verified GRCr8 FASTA. All three use the same combined four-run HiFi k=21 database and recorded solid threshold 9. Times are UTC. No analysis was rerun for this documentation check.

## Preserved numerical results — scientific interpretation preliminary

| Assembly | QV | Solid-read k-mer completeness (%) |
|---|---:|---:|
| Hifiasm primary | 64.2134 | 99.7315 |
| Verkko main | 58.9038 | 99.7451 |
| GRCr8 | 68.5593 | 99.7160 |

The [original summary](../../results/merqury/merqury_summary.tsv), [result note](../../results/merqury/README.md), spectra in the [figure index](../../figures/README.md), and prior source commands remain unchanged. [Source methodology notes](README.source.md) record the performed workflow.

**Completed execution is not the same as final scientific validation.** QV is a read-kmer estimate; completeness measures distinct solid read k-mers, not genome bases. Sample differences, read errors, filtering, repeats and copy representation require further evaluation. Do not infer confirmed errors or final assembly rankings from these numbers alone. Missing/overrepresented k-mer localization and copy-number interpretation remain unresolved.

## Older historical work — separate provenance

Legacy analyses under the older raid5 tree are not automatically comparable to these BN runs. In particular, historical job 1954396 and its script/log explicitly reference DLD1, not Brown Norway. Older Verkko-labelled outputs require sample/assembly identity checks. One legacy QV file was unreadable during inspection; its contents were not inferred or altered. The earlier archived README also contains older metrics that are not established as estimates for the current assemblies.

Retain all historical outputs; do not merge datasets or classify unrelated jobs as BN reruns. New workflows must not depend on raid5. The current November BN evaluation should not be labeled merely historical or unfinished because further validation is planned.

## Further validation — planned, not confirmed running

No later Merqury/k-mer job was found in the checked SLURM queue/accounting, and no later completed result set was verified. There are no new job IDs or replacement values to report. Ongoing Hi-C mapping is a separate workflow.

Before additional evaluation, agree and document dataset provenance, database construction/filtering, k, assembly/reference identity, versions, parameters and SLURM resources. Use fresh outputs and preserve these completed results. See [evaluation policy](../../configs/evaluation_policy.json), which keeps execution, preliminary interpretation, older history and planned work distinct.
