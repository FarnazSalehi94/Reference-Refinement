# Assembly readiness — 2026-11-04 UTC

**Restarted successfully on 2026-11-05 UTC.** Hifiasm job 2871178 is running on tux05; Verkko job 2871179 is running on tux06. Both request 64 CPUs, 700G memory, and seven days. Their fresh outputs are `hifiasm/run_2871178` and `verkko/run_2871179`; logs are `logs/hifiasm_2871178.{out,err}` and `logs/verkko_2871179.{out,err}`. The user accepts that datasets may come from different animals of the same inbred BN/NHsdMcwi strain; metadata explicitly avoids claiming a shared individual.

## Replacement Hi-C validation

Full paired scan with `input_validation/fastq_check pair` reached EOF on both uncompressed FASTQs with exit code 0. R1 and R2 each have **433,992,207** records, consistent with 433,992,207 spots and 867,984,414 reads. Every record was checked for four-line structure, `@` and `+` markers, nonempty sequence, equal sequence/quality lengths, sequence character validity and printable Phred+33 quality characters. At each position, the first whitespace-delimited read identifier (with optional /1 or /2 removed) matched between mates. See `input_validation/logs/ERR5309023_new_pair.result` and `ERR5309023_new_pair.progress`. File sizes and modification times were unchanged during the scan. NCBI SRA validation was reported PASS by the user; source checksums for ENA compressed FASTQs do not apply to these fasterq-dump outputs.

Four HiFi FASTQs and the ONT FASTQ were previously fully validated; they were not rescanned.

## Preflight and scripts

Slurm job 2869953 completed on tux05 with exit 0 on 2026-11-04, and its status file says PASS. It tested the old Hi-C paths, long-read access, assembler versions, and listed executable dependencies. Access-only job 2871142 completed successfully on tux05 for the new files, testing readability and their first byte. `scripts/hifiasm.slurm` and `scripts/verkko.slurm` use the new Hi-C paths and allocate new job-specific output directories with `mkdir`, preventing reuse of pre-existing outputs.

## Provenance

The four HiFi runs have BioSample SAMN37807429. ERR5309023 has BioSample SAMN16261960; both are included in NCBI GRCr8 parent BioSample SAMN38730095 (https://www.ncbi.nlm.nih.gov/biosample/38730095). The HiFi BioSample is described as from the same BN/NHsdMcwi colony as the rat used for mRatBN7.2 (https://www.ncbi.nlm.nih.gov/sra/SRR26381151); published GRCr8 methods report using ERR5309023 and ERR5309024 for scaffolding (https://genome.cshlp.org/content/early/2024/11/08/gr.279292.124.full.pdf). Records do not establish that Hi-C and HiFi are from the same individual; ONT sample identity relative to HiFi is also unverified. The user accepts these provenance limitations for assembly of the inbred strain. They are recorded without claiming a shared individual in `assembly_metadata.md`.

## Restart preflight — 2026-11-05 UTC

All seven required input paths exist and are readable under `inputs/`; none of the top-level FASTQ paths is a symlink. On tux05, SHA256 checks passed for all four moved HiFi FASTQs and `reads.fastq`; results are in `logs/checksum_2871172.out`. Hi-C validation was not repeated.

The local `tools/hifiasm` binary reports version 0.25.1-r942 and matches the original executable checksum `eef06a643cade721fe1adca6ea93d1d0fc0cb0395d3fefbc02d290d056f66680`. It ran on tux05; its dynamic library paths resolve under `/home` and `/gnu`, not raid5. Verkko v2.3.2 ran in its configured conda environment on tux06. Both restart scripts pass `bash -n`, request 64 CPUs, 700G and seven days, and have no `/moosefs/raid5/` references. Slurm `--test-only` accepted both jobs on their respective nodes. Approximately 65T is available on `/moosefs`.

Previous jobs 2871145 and 2871146 are canceled. The live hifiasm command line uses `/moosefs/salehi/ref-refine/assemblies/tools/hifiasm`, and the live Verkko command and its generated tasks use only `/moosefs/salehi/ref-refine/assemblies/inputs/` for sequencing reads. The submission scripts contain no `/moosefs/raid5/` references. Both jobs were observed RUNNING in Slurm after submission; their initial processes are active and job-specific directories and logs exist.
