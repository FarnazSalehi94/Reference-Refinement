# Approved execution — 2026-11-09 21:22 UTC

User approved corrections, scheduler changes, pairs validation, deferred corrected Cooler regeneration, and Pretext generation. No assembly modifications or scaffolding are authorized or performed.

## Actions performed

- Inspected job states and actual submitted batches before scheduler changes.
- Left running Hifiasm BWA/pairtools job 2871279 untouched. No mapping has been repeated.
- Cancelled obsolete PENDING plot job **2871281** after verifying dependencies. It would invoke the revised Python script without its required revision and/or consume invalid legacy matrices. Corrected regeneration jobs produce their own plots instead.
- Submitted **2871285**, Hifiasm full pairs validation, `afterany:2871279`.
- Submitted **2871286**, Verkko full pairs validation, `afterany:2871280`.
- Updated existing PENDING Pretext job **2871282** to `afterok:2871285:2871286`. Its batch commands remain unchanged; it reads the original validated standard pairs directly, independently of corrected Cooler/plot success.
- Submitted lightweight coordinator **2871287**, `afterok:2871285:2871286`. Only after both validators pass does it submit two matrix-only correction jobs. Their future IDs will be recorded in `submitted_regeneration.tsv` beside this document and in `../../logs/submit_corrected_2871287.out`.
- Updated still-PENDING Verkko mapping **2871280** from `afterok:2871279` to `afterok:2871285`. This retains serial mapping and ensures that a failure confined to Hifiasm's legacy Cooler stage cannot block Verkko if its pairs validate. It adds the validation wait but does not replace/repeat mapping or change its submitted command.

Hifiasm mapping remains RUNNING; all validators/Pretext/coordinator are dependency-gated. No corrected Cooler jobs have yet been submitted because finished pairs are not yet available.

## Execution graph

```
2871279 Hifiasm mapping (unchanged, RUNNING)
  -> afterany 2871285 Hifiasm pairs validation
       -> afterok 2871280 Verkko mapping (original submitted batch)
            -> afterany 2871286 Verkko pairs validation
2871285 + 2871286 PASS
  -> 2871282 original Pretext job (independent branch)
  -> 2871287 coordinator
       -> sbatch Hifiasm corrected Cooler + matrix QC + raw/balanced figures
       -> sbatch Verkko corrected Cooler + matrix QC + raw/balanced figures
```

If a validator fails, neither Pretext nor coordinator proceeds; inspect its logs and do not bypass the gate. The `afterany` validator dependencies allow inspection/recovery of pairs after a terminal mapping job whose downstream legacy Cooler step failed. Validators do not accept a running producer or incomplete products.

## Validation gates

Each pairs validator requests **1 CPU, 8G RAM, 1 day** and performs a read-only full EOF scan on a compute node, not a login node. It checks:
- terminal producer accounting and BWA-MEM completion footer;
- nonempty pairs, dedup.stats, chrom.sizes, and BWA log;
- standard columns and chromosome sizes matching the assembly index;
- newline-terminated complete records, field counts, mapped 1-based endpoint bounds/strands;
- no DD pair records;
- complete contact count exactly equals `dedup.stats total_nodups`, internal category sums, and cis/trans totals;
- unchanged input metadata throughout the scan.

It does not repeat pairtools deduplication or align reads. PASS receipts go to `validation/hifiasm.json` and `validation/verkko.json`. Receipt metadata is checked again immediately before regeneration; the receipt is copied into corrected-run provenance.

Each future correction job requests **8 CPUs, 64G RAM, 2 days**. It performs 1-based cload without `--zero-based`, zoomification at 10 kb/50 kb/250 kb/1 Mb, and ICE balancing with error on nonconvergence. It compares stored contact counts to the full validated pairs EOF count and across resolutions, checks full bin coordinates/dimensions/upper-triangle pixel validity, exactly checks a bounded contact sample, and produces separately labeled raw and balanced PNG/PDF maps using true Cooler bin offsets. Missing/unconverged weights are not silently replaced with raw counts. Scientific matrix validation has NOT yet run.

If balancing or validation fails, retain all partial outputs and inspect the failure. Do not overwrite a revision or automatically weaken filters. Plot reruns require a new output location/revision or deliberate provenance-preserving handling of partial figures.

## Paths and immutable execution snapshots

- Corrected outputs: `hifiasm/` and `verkko/` below this revision directory, each with `cool/`, `figures/`, `reports/`, `provenance/`, and `validation.json`.
- Original BWA/pairtools and legacy Cooler outputs stay under `../../hifiasm/` and `../../verkko/`.
- Pretext stays under `../../pretext/{hifiasm,verkko}/` (no completed outputs existed when inspected).
- Executed script copies and before/after scheduler records: `provenance/approved_execution_20261109T2123/`.
- Corrected jobs are submitted from this execution snapshot and copy those same Python scripts into their output provenance, avoiding later disk-script drift.
- Regression log: `provenance/approved_regression_test.log`.

Regression tests passed on five synthetic SAM/pairs contacts with the installed tools, including positive 1-based boundary cases, incorrect `--zero-based` negative control, exact five-bin/five-contact accounting, bin-based labels/boundaries, raw/balanced rendering below intensity one, and pairs validator rejection of inconsistent dedup totals. Shell/Python syntax checks passed. These tests are not a substitute for real-project validation, which is pending.

## Failure reporting / monitoring

```
squeue -j 2871279,2871280,2871282,2871285,2871286,2871287
sacct -X -j 2871279,2871280,2871281,2871282,2871285,2871286,2871287 --format=JobID,State,ExitCode,Elapsed
```

Logs are under `../../logs/`: `pairs_qc_<job>.{out,err}`, `submit_corrected_2871287.{out,err}`, and future `correct_<job>.{out,err}`. Pretext logs remain under `../../pretext/logs/`. Actual regeneration IDs, receipt results and scientific plots are pending; do not report them as completed.
