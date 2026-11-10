# Provenance and metadata

**Evaluation status is separate from computational completion and checksum verification.** Previous Merqury/QV/read-kmer outputs are historical/preliminary; a repeat evaluation is planned, with no replacement results or job IDs. The controlling policy is [configs/evaluation_policy.json](../configs/evaluation_policy.json). Original result tables, figures, methods and import hashes are preserved. A historical job remaining COMPLETED must not silently promote its results to current status.

- [datasets.tsv](datasets.tsv): public accessions and same-individual limitations. No private animal identifiers are included.
- [software_versions.tsv](software_versions.tsv): observed tool versions and evidence; installation metadata is not a complete environment lockfile.
- [import_manifest.tsv](import_manifest.tsv): exact HPC-relative source, repository destination, content SHA256, size, result evidence job and category.
- [slurm_status.json](slurm_status.json): scheduler states observed by synchronization, not a substitute for output validation.
- `sync_state.json`: hashes used to prevent automatic overwrite of locally edited managed files.
- `source_records/`: unmodified historical HPC notes. The 2026-11-02 integrity report describes failed **old ENA Hi-C files**, not the replacement SRA-derived mates used in the successful runs. `assembly_readiness.md` records the successful replacement validation and moved-file checks. Stale running/not-ready statements are historical; consult [current status](../PROJECT_STATUS.md).

The large scientific tree is `/moosefs/salehi/ref-refine/assemblies/`; this curated checkout is separate. ONT individual relationship to the public HiFi sample is unconfirmed. The provenance record does not establish that HiFi, ONT and Hi-C are from the same animal. Approximate long-read base totals and N50 come from the project handoff and are not newly recalculated.

GRCr8 accession: GCF_036323735.1. The official download passed NCBI MD5 and gzip checks (2871274); identifiers/lengths matched the previous index input. That does not prove the old reference sequence is byte-identical. Do not revalidate huge sequencing inputs without a reason.
