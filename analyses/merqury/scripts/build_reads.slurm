#!/bin/bash
#SBATCH --job-name=bn_meryl_reads
#SBATCH --partition=allnodes
#SBATCH --cpus-per-task=32
#SBATCH --mem=192G
#SBATCH --time=7-00:00:00
#SBATCH --output=/moosefs/salehi/ref-refine/assemblies/analysis/merqury/logs/reads_%j.out
#SBATCH --error=/moosefs/salehi/ref-refine/assemblies/analysis/merqury/logs/reads_%j.err
set -euo pipefail
root=/moosefs/salehi/ref-refine/assemblies
out="$root/analysis/merqury/reads"
meryl=/home/salehi/miniconda3/envs/assembly_eval/bin/meryl
mkdir -p "$out/tmp"
export TMPDIR="$out/tmp" OMP_NUM_THREADS="$SLURM_CPUS_PER_TASK"
"$meryl" --version 2>&1 || true
for run in 151 152 153 154; do
 file="$root/inputs/SRR26381${run}.fastq"
 "$meryl" k=21 threads=32 memory=160 count output "$out/SRR26381${run}.k21.meryl" "$file"
done
"$meryl" threads=32 memory=160 union-sum output "$out/all_hifi.k21.meryl" "$out/SRR26381151.k21.meryl" "$out/SRR26381152.k21.meryl" "$out/SRR26381153.k21.meryl" "$out/SRR26381154.k21.meryl"
"$meryl" threads=32 memory=160 histogram "$out/all_hifi.k21.meryl" > "$out/all_hifi.k21.hist"
"$meryl" threads=32 memory=160 statistics "$out/all_hifi.k21.meryl" > "$out/all_hifi.k21.statistics.txt"
test -s "$out/all_hifi.k21.hist"
