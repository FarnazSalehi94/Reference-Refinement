# Brown Norway assembly run metadata

These new hifiasm hybrid_v1 and Verkko runs combine the four validated PacBio HiFi
runs, the validated ONT ultra-long FASTQ, and the validated ERR5309023 Hi-C pair.

The data are associated with the Brown Norway BN/NHsdMcwi inbred strain. The HiFi
runs and ERR5309023 have different public BioSample accessions, and the ONT source
has no independently confirmed public sample accession in the local provenance
record. The assembly therefore permits data from different animals of the same
inbred strain. It does not claim that the reads came from one individual.

Previous assembly outputs are preserved. Each submitted job writes to a new
job-specific directory: `hifiasm/run_<jobid>` or `verkko/run_<jobid>`.

For the 2026-11-05 restart, hifiasm job 2871178 runs from
`hifiasm/run_2871178` on tux05; Verkko job 2871179 runs from
`verkko/run_2871179` on tux06. Both use 64 CPUs, 700G memory, and a seven-day
limit. The four moved HiFi files and ONT file matched their recorded SHA256
checksums on tux05. Local hybrid_v1 executable `tools/hifiasm` has SHA256
`eef06a643cade721fe1adca6ea93d1d0fc0cb0395d3fefbc02d290d056f66680` and
reports version 0.25.1-r942. Sequencing inputs and this executable resolve
under the assemblies directory; neither submitted runtime command depends on
`/moosefs/raid5/`.
