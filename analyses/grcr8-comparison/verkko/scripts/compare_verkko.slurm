#!/bin/bash
#SBATCH --job-name=bn_verkko_grcr8
#SBATCH --partition=allnodes
#SBATCH --cpus-per-task=24
#SBATCH --mem=128G
#SBATCH --time=3-00:00:00
#SBATCH --output=/moosefs/salehi/ref-refine/assemblies/analysis/verkko_comparison/logs/slurm_%j.out
#SBATCH --error=/moosefs/salehi/ref-refine/assemblies/analysis/verkko_comparison/logs/slurm_%j.err
set -euo pipefail
base=/moosefs/salehi/ref-refine/assemblies/analysis
out="$base/verkko_comparison"
asm=/moosefs/salehi/ref-refine/assemblies/verkko/run_2871179/assembly/assembly.fasta
mm=/home/salehi/miniconda3/envs/verkko/bin/minimap2
samtools=/home/salehi/miniconda3/envs/verkko/bin/samtools
"$samtools" faidx --fai-idx "$out/fasta/verkko.fai" "$asm"
"$mm" -x asm5 -t "$SLURM_CPUS_PER_TASK" --secondary=yes -N 50 -c "$base/GRCr8.mmi" "$asm" > "$out/alignments/verkko.paf.tmp" 2> "$out/logs/verkko.minimap2.log"
mv "$out/alignments/verkko.paf.tmp" "$out/alignments/verkko.paf"
python3 "$out/scripts/compare_four.py" "$out"
python3 "$base/chromosome_investigation/summarize_contigs.py"
