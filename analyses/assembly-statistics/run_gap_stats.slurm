#!/bin/bash
#SBATCH --job-name=bn_gap_stats
#SBATCH --partition=allnodes
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=06:00:00
#SBATCH --output=/moosefs/salehi/ref-refine/assemblies/analysis/gap_stats/logs/gapstats_%j.out
#SBATCH --error=/moosefs/salehi/ref-refine/assemblies/analysis/gap_stats/logs/gapstats_%j.err
set -euo pipefail
root=/moosefs/salehi/ref-refine/assemblies
python3 "$root/analysis/gap_stats/gap_stats.py" \
 "$root/hifiasm/run_2871178/primary.fasta" \
 "$root/verkko/run_2871179/assembly/assembly.fasta" \
 "$root/analysis/merqury/reference/GRCr8.fasta"
