#!/bin/bash
#SBATCH --job-name=bn_hifiasm
#SBATCH --partition=tux
#SBATCH --nodelist=tux05
#SBATCH --cpus-per-task=64
#SBATCH --mem=700G
#SBATCH --time=7-00:00:00
#SBATCH --output=/moosefs/salehi/ref-refine/assemblies/logs/hifiasm_%j.out
#SBATCH --error=/moosefs/salehi/ref-refine/assemblies/logs/hifiasm_%j.err
set -euo pipefail
base=/moosefs/salehi/ref-refine/assemblies
# Inputs were validated before submission. Hi-C/HiFi/ONT provenance limitation is
# documented in assemblies/assembly_metadata.md and accepted for this run.
run_dir="$base/hifiasm/run_${SLURM_JOB_ID:?}"
mkdir "$run_dir"
export TMPDIR="$run_dir/tmp"
mkdir -p "$TMPDIR"
"$base/tools/hifiasm" \
 --ont --hf "$base/inputs/SRR26381151.fastq,$base/inputs/SRR26381152.fastq,$base/inputs/SRR26381153.fastq,$base/inputs/SRR26381154.fastq" \
 --h1 /moosefs/salehi/ref-refine/assemblies/inputs/ERR5309023_1.fastq \
 --h2 /moosefs/salehi/ref-refine/assemblies/inputs/ERR5309023_2.fastq \
 -t 64 -o "$run_dir/bn" "$base/inputs/reads.fastq" \
 2> "$run_dir/hifiasm.log"
awk -F '\t' '$1=="S" {if ($3=="*") exit 1; print ">"$2"\n"$3}' "$run_dir/bn.hic.p_ctg.gfa" > "$run_dir/primary.fasta"
python3 "$base/scripts/assembly_stats.py" "$run_dir/primary.fasta" > "$run_dir/primary.stats.tsv"
