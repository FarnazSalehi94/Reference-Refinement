#!/bin/bash
#SBATCH --job-name=bn_merqury
#SBATCH --partition=allnodes
#SBATCH --cpus-per-task=32
#SBATCH --mem=192G
#SBATCH --time=7-00:00:00
#SBATCH --output=/moosefs/salehi/ref-refine/assemblies/analysis/merqury/logs/assess_%j.out
#SBATCH --error=/moosefs/salehi/ref-refine/assemblies/analysis/merqury/logs/assess_%j.err
set -euo pipefail
root=/moosefs/salehi/ref-refine/assemblies
base="$root/analysis/merqury"
export PATH="/home/salehi/miniconda3/envs/assembly_eval/bin:$PATH"
export MERQURY=/home/salehi/miniconda3/envs/assembly_eval/share/merqury
export OMP_NUM_THREADS="$SLURM_CPUS_PER_TASK"
export TMPDIR="$base/tmp"
mkdir -p "$TMPDIR"
for sample in hifiasm verkko grcr8; do
 out="$base/results/$sample"
 mkdir -p "$out"
 cd "$out"
 case "$sample" in
  hifiasm) input="$root/hifiasm/run_2871178/primary.fasta";;
  verkko) input="$root/verkko/run_2871179/assembly/assembly.fasta";;
  grcr8) input="$base/reference/GRCr8.fasta";;
 esac
 ln -sfn "$input" "${sample}.fasta"
 "$MERQURY/merqury.sh" "$base/reads/all_hifi.k21.meryl" "$out/${sample}.fasta" "$sample" > "$base/logs/${sample}.merqury.log" 2>&1
 test -s "$sample.qv"
 test -s "$sample.completeness.stats"
 test -s "$sample.$sample.spectra-cn.hist"
 ls "$sample"*.spectra-cn.*png >/dev/null
 done
python3 "$base/scripts/summarize.py" "$base/results"
