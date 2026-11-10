# Assembly methods and run identity

These are exact HPC script snapshots, not portable launchers. Inputs and outputs remain outside Git. Source-relative paths and SHA256 digests are recorded in [the import manifest](../metadata/import_manifest.tsv).

| Method | Run | Version | Requested resources | Completion |
|---|---|---|---|---|
| Hifiasm **experimental hybrid_v1** | 2871178 | 0.25.1-r942 | 64 CPUs, 700G, 7 days | Exit 0; 27:02:06 |
| Verkko | 2871179 | 2.3.2 | 64 CPUs, 700G, 7 days | Exit 0; 55:46:42 |

Hifiasm executable SHA256: `eef06a643cade721fe1adca6ea93d1d0fc0cb0395d3fefbc02d290d056f66680`. The original hybrid_v1 source commit/build recipe has not yet been recovered; version string alone is insufficient. Do not substitute ordinary hifiasm or claim full build reproducibility. Its log has four `ERROR-r-break` and four `ERROR-read` messages; meaning remains unresolved despite successful completion.

The exact command in [hifiasm.slurm](hifiasm/hifiasm.slurm) uses `--ont --hf` with four comma-separated HiFi files, Hi-C `--h1/--h2`, and positional ONT reads. Primary FASTA was extracted from `bn.hic.p_ctg.gfa`. Haplotype GFAs were preserved. Hap1/hap2 lengths are 2,666,936,900 and 2,910,952,370 bp; the imbalance is not automatically missing DNA.

[Verkko's script](verkko/verkko.slurm) passes four files to `--hifi`, ONT to `--nano`, and paired Hi-C via `--hic1/--hic2`; local CPUs/memory are set explicitly. The main assembly, haplotypes, unassigned sequence and intermediates remain on HPC. Initial cancelled jobs 2871145/2871146 are not these successful runs.

New work must preserve both original assemblies and use fresh output directories. No automatic polishing, contig splitting or scaffolding is authorized by these snapshots.
