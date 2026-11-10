# Pretext maps for Brown Norway assemblies

## Reused alignment and filtering

No new Hi-C alignment is performed here. The maps consume the `.pairs` files produced by the current Cooler mapping workflow:

- `../hifiasm/results/valid_dedup.pairs`
- `../verkko/results/valid_dedup.pairs`

Both come from the exact paired reads `inputs/ERR5309023_1.fastq` and `inputs/ERR5309023_2.fastq` and the current mapping pipeline against each assembly. The selected replacement read pair was previously fully checked and synchronized: 433,992,207 records in each mate, with no pairing errors (`input_validation/logs/ERR5309023_new_pair.result`, exit code 0). The earlier failed, truncated ENA mirror file under `/moosefs/raid5` is not the read pair used by this workflow.

Shared mapping filters, applied before PretextMap:

- BWA-MEM paired Hi-C mapping (`-5SP -T0`)
- pairtools `parse --min-mapq 30 --walks-policy 5unique`
- pairtools coordinate sort and deduplication (`--mark-dups`)

PretextMap receives the resulting standard pairs-format records without applying an additional MAPQ filter. This gives both assemblies the same read set and filters. Pair metadata and the first data record are checked in the SLURM script before each map is built.

## Commands

```bash
PretextMap -o hifiasm.pretext --sortby length --sortorder descend --highRes \
  < analysis/hic_contact_maps/hifiasm/results/valid_dedup.pairs
PretextMap -o verkko.pretext --sortby length --sortorder descend --highRes \
  < analysis/hic_contact_maps/verkko/results/valid_dedup.pairs
PretextSnapshot --map hifiasm.pretext --sequences '=full' --resolution 3000 \
  --format png --folder snapshots --prefix hifiasm_overview_
PretextSnapshot --map verkko.pretext --sequences '=full' --resolution 3000 \
  --format png --folder snapshots --prefix verkko_overview_
```

PretextMap 0.2.4 is installed in `/home/salehi/miniconda3/envs/pretext`; PretextSnapshot 0.1.1 is in the same dedicated environment. PretextView is a desktop OpenGL application and has no Bioconda package in the queried channel; the `.pretext` files are its native map format and are intended to be opened with the official Linux desktop build. High-resolution maps require a compatible PretextView (>=0.2.5 per PretextMap documentation).

## Outputs and interpretation

For each assembly, the interactive map is `analysis/hic_contact_maps/pretext/<assembly>/<assembly>.pretext`; overview PNG is in that assembly's `snapshots/` directory. No assembly FASTA or Cooler result is modified. Contact anomalies are candidates for independent validation, not confirmed misassemblies. No automatic correction or scaffolding is part of this workflow.

The SLURM task requests 4 CPUs, 64 GB RAM, and 2 days; both maps are generated sequentially in one job. This includes the >=16 GB RAM recommendation for `--highRes` maps and conservative allowance for the pair file and snapshot generation.
