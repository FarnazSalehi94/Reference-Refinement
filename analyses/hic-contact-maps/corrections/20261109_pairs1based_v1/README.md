# Hi-C correction audit and proposed regeneration

Date: 2026-11-09 UTC. No SLURM jobs cancelled, submitted, held, or modified.
Original assemblies, BWA indexes/logs, pairtools files, and Pretext script are unchanged.
Original disk scripts and actual submitted batch-script snapshots are preserved in `provenance/`.

## Job audit at 20:52 UTC

| Job | State | Dependency | Submitted code |
|---|---|---|---|
| 2871279 | RUNNING, octopus07 | none | BWA/pairtools followed by incorrect Cooler `--zero-based` |
| 2871280 | PENDING | afterok:2871279 | Same incorrect Cooler command; Verkko mapping has not begun |
| 2871281 | PENDING | afterok:2871279,afterok:2871280 | Executes disk `scripts/plot_maps.py`; no embedded Cooler creation |
| 2871282 | PENDING | afterok:2871280 | Reads original pairs directly; no Cooler dependency in its commands |

Both submitted mapping scripts are immutable SLURM copies: editing disk `run_map.slurm` cannot fix them. At inspection no `.cool`, `.mcool`, maps or figures existed. Hifiasm pairs and dedup.stats were empty while BWA and sorting were active, so no actual project-contact sample could yet be validated.

## Coordinate evidence and scientific consequence

Installed pairtools parser source:
`/home/salehi/miniconda3/envs/hic_contact/lib/python3.12/site-packages/pairtools/lib/parse.py`, lines 290–295, converts pysam reference_start to 1-based ends with `reference_start + 1` (or reference_start + alignment span). With a 1M forward alignment, SAM POS is returned unchanged. The default reported end is 5'. Standard pairs positions remain 1-based, including reverse-strand endpoints; do not subtract from or rewrite the original pairs.

Correct bin index is `chromosome_bin_offset + (position - 1) // binsize`. Cooler `cload pairs` defaults to this conversion. `--zero-based` incorrectly treats boundary position 10000 as bin 1 instead of bin 0 at 10 kb. It can also mishandle terminal positions at exact contig-length/bin boundaries. No BWA/pairtools recomputation is needed.

Disk `run_map.slurm` no longer uses `--zero-based`. Existing `<assembly>/cool/contacts.10000.cool` and `contacts.mcool`, if produced by the submitted scripts, are legacy/incorrect and must not be interpreted. Any figures derived from them must be regenerated. Leave originals in place as provenance; never overwrite them.

## Plot correction

`plot_maps.py` now uses `Cooler.extent(contig)` for integer bin intervals `[start,end)`. For imshow, tick centers are `(start+end-1)/2`; boundary lines are `end-0.5`. A layout TSV records every contig, including small unlabeled contigs. Explicit axis limits keep the matrix bounds fixed. Individual contig tick labels report Mb at the actual displayed bin starts.

Separate `_raw` and `_balanced` PNG/PDF outputs are produced. Balanced intensities are count × ICE weight1 × ICE weight2; nonfinite weights are masked. Raw maps use a log scale starting at 1. Balanced maps use positive-value percentile limits rather than incorrectly clipping intensities below 1. All panels use per-panel 99.8th-percentile upper limits, recorded in `plot_scales.json`; colors are not a common quantitative scale across panels. Zero/masked cells are gray. These are contact-intensity maps, NOT observed/expected maps. Raw marginal-support screening remains explicitly raw and is not proof of structural error. Contact-support totals are derived from upper-triangle pixels without rereading the entire pairs file.

Balanced plotting refuses absent/unconverged/all-unusable weights rather than silently substituting raw data. Small/sparse contigs and coarse resolutions may be heavily masked. Failed balancing requires inspection, not automatic relaxation of filters. Regeneration uses `--convergence-policy error`.

The plotter requires `--revision` and an existing `validation.json`. It cannot silently consume the old matrices. It refuses to overwrite existing figure/report directories. The already submitted 2871281 invokes the changed disk Python script without this option and will now fail safely if left queued: replace/cancel this plotting job only after user approval. Editing the disk plot.slurm does not change its submitted batch wrapper.

## Regression validation performed

Run on the login node using only five synthetic contacts and temporary files:

```bash
/home/salehi/miniconda3/envs/moddotplot/bin/python \
 analysis/hic_contact_maps/scripts/test_hic_corrections.py
```

PASS (log: `provenance/regression_test.log`):
- The installed pairtools parser returned exact 1-based positions 1, 9999, 10000, 10001, and contig-terminal positions unchanged from synthetic SAM records (MAPQ 60; same 5unique policy).
- Toy contigs A=20001 bp and B=15000 bp give five 10-kb bins with truncated terminal bins.
- Five contacts aggregate exactly to pixels (0,3):3, (1,4):1, (2,4):1.
- The `--zero-based` negative control gives different pixels.
- Matrix shape, chromosome order, starts/ends, upper-triangle counts, contig offsets, tick centers (1,3.5), and boundary (2.5) were verified.
- Both raw/balanced PNG/PDF rendering worked; synthetic weights explicitly tested intensities below one. These test weights are NOT biological ICE results.
- Input test pairs were byte-identical afterward.
- Shell scripts passed `bash -n`.

Project matrices have NOT yet been regenerated or validated. The SLURM regeneration script will check full bin coordinates, dimensions, ordered positive upper-triangle pixels, contact conservation across four resolutions, and ICE convergence/finite weights. It will validate the first 10000 finished project pairs by exact independent `(position-1)//binsize` aggregation against a sample loaded through the installed Cooler CLI and confirm support in the full 10-kb matrix. This bounded prefix is not a random genome-wide sample. Full contact conservation across matrices is not an independent full pairs recount.

## Proposed plan — commands below NOT submitted

Least-disruptive choice: let both existing mapping jobs finish. They may create incorrect legacy Cooler matrices, but mapping/pairtools products remain reusable. Do not rerun BWA. Once pairs processing is independently confirmed complete (final dedup.stats, mapping logs, stable file metadata), run matrix-only correction, validation, and plotting per assembly:

```bash
cd /moosefs/salehi/ref-refine/assemblies
sbatch --export=ALL,ASSEMBLY=hifiasm,REVISION=20261109_pairs1based_v1,PAIRS_READY=YES \
 analysis/hic_contact_maps/scripts/regenerate_cooler.slurm
sbatch --export=ALL,ASSEMBLY=verkko,REVISION=20261109_pairs1based_v1,PAIRS_READY=YES \
 analysis/hic_contact_maps/scripts/regenerate_cooler.slurm
```

Only set PAIRS_READY=YES after reviewing completed pair processing. If a mapping job exits nonzero during Cooler creation, its pairs may still be complete; verify before reuse rather than rerunning alignment. If submitting ahead of completion after approval, add `--dependency=afterok:2871279` for hifiasm and `--dependency=afterok:2871280` for Verkko. A Cooler-stage failure can block afterok even when pairs are ready; manually review that situation.

Resources per assembly: 8 CPUs, 64G RAM, maximum 2 days; execute sequentially if minimizing simultaneous I/O. The matrix-only job also validates and generates figures, so no separate replacement plot job is needed. Actual memory/runtime remain to be measured. Output path:
`corrections/20261109_pairs1based_v1/<assembly>/{cool,figures,reports,provenance}` plus `validation.json`.
A pre-existing assembly revision directory causes a refusal, not overwrite; use a fresh revision for retries and retain partial results. Provenance records input stat metadata, dedup.stats, script copies/hashes, chrom.sizes hash, job ID, and Cooler version. No full sequencing/pairs hashes are imposed. Input pairs metadata is compared before/after.

Alternative after approval: replace pending Verkko mapping with a corrected submission before it starts, avoiding incorrect legacy matrix generation. This would be its FIRST mapping, not a remap, but requires cancelling/replacing 2871280 and rewiring dependent plotting/Pretext jobs. It is not necessary for scientific correctness if matrix-only regeneration is used, and no such scheduler action has been taken.

## Pretext

PretextMap consumes original standard pairs, not Cooler matrices. No coordinate rewriting, Cooler correction, or balanced normalization should be applied to those inputs. Existing Pretext code remains unchanged and scientifically compatible with this correction. It can proceed independently of corrected Cooler generation.

Scheduler coupling remains: 2871282 waits for success of 2871280 (including its legacy Cooler stage), which itself waits for 2871279. If Cooler fails after pairs finish, Pretext may stay blocked although its inputs are valid. Dependency changes/replacement would require approval. No completed Pretext outputs existed at inspection.
