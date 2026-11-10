#!/bin/bash
#SBATCH --job-name=bn_verkko
#SBATCH --partition=tux
# Run independently on the second idle 96-core node; hifiasm uses tux05.
#SBATCH --nodelist=tux06
#SBATCH --cpus-per-task=64
#SBATCH --mem=700G
#SBATCH --time=7-00:00:00
#SBATCH --output=/moosefs/salehi/ref-refine/assemblies/logs/verkko_%j.out
#SBATCH --error=/moosefs/salehi/ref-refine/assemblies/logs/verkko_%j.err
set -euo pipefail
base=/moosefs/salehi/ref-refine/assemblies
# Inputs were validated before submission. Hi-C/HiFi/ONT provenance limitation is
# documented in assemblies/assembly_metadata.md and accepted for this run.
run_dir="$base/verkko/run_${SLURM_JOB_ID:?}"
mkdir "$run_dir"
export TMPDIR="$run_dir/tmp"
mkdir -p "$TMPDIR"
/home/salehi/miniconda3/bin/conda run --no-capture-output -n verkko verkko \
 -d "$run_dir/assembly" \
 --hifi "$base/inputs/SRR26381151.fastq" "$base/inputs/SRR26381152.fastq" "$base/inputs/SRR26381153.fastq" "$base/inputs/SRR26381154.fastq" \
 --nano "$base/inputs/reads.fastq" \
 --hic1 /moosefs/salehi/ref-refine/assemblies/inputs/ERR5309023_1.fastq \
 --hic2 /moosefs/salehi/ref-refine/assemblies/inputs/ERR5309023_2.fastq \
 --local --local-cpus 64 --local-memory 700 --no-cleanup
ln -sfn assembly/assembly.fasta "$run_dir/primary.fasta"
python3 "$base/scripts/assembly_stats.py" "$run_dir/primary.fasta" > "$run_dir/primary.stats.tsv"
