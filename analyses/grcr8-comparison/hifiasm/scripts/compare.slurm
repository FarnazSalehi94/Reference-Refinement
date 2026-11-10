#!/bin/bash
#SBATCH --job-name=bn_grcr8_comparison
#SBATCH --partition=allnodes
#SBATCH --exclude=tux06
#SBATCH --cpus-per-task=24
#SBATCH --mem=128G
#SBATCH --time=3-00:00:00
#SBATCH --output=/moosefs/salehi/ref-refine/assemblies/analysis/logs/compare_%j.out
#SBATCH --error=/moosefs/salehi/ref-refine/assemblies/analysis/logs/compare_%j.err
set -euo pipefail
base=/moosefs/salehi/ref-refine/assemblies/analysis
run=/moosefs/salehi/ref-refine/assemblies/hifiasm/run_2871178
ref=/moosefs/raid5/salehi/ref-refine/GRCr8.fa
mm=/home/salehi/miniconda3/envs/verkko/bin/minimap2
samtools=/home/salehi/miniconda3/envs/verkko/bin/samtools
cd "$base"
echo "node=$(hostname) job=$SLURM_JOB_ID start=$(date -u -Is)"
"$mm" --version
for hap in hap1 hap2; do
  awk -F '\t' '$1=="S" {if ($3=="*" || $3=="") {print "Missing sequence in GFA segment " $2 > "/dev/stderr"; exit 1} print ">"$2"\n"$3; n++} END {if(n==0) exit 1}' "$run/bn.hic.$hap.p_ctg.gfa" > "$base/fasta/$hap.fasta.tmp"
  mv "$base/fasta/$hap.fasta.tmp" "$base/fasta/$hap.fasta"
done
"$samtools" faidx --fai-idx "$base/GRCr8.fai" "$ref"
"$samtools" faidx --fai-idx "$base/fasta/primary.fai" "$run/primary.fasta"
for hap in hap1 hap2; do "$samtools" faidx --fai-idx "$base/fasta/$hap.fai" "$base/fasta/$hap.fasta"; done
"$mm" -I 8G -t "$SLURM_CPUS_PER_TASK" -d "$base/GRCr8.mmi" "$ref"
for assembly in primary hap1 hap2; do
  if [[ "$assembly" == primary ]]; then fasta="$run/primary.fasta"; else fasta="$base/fasta/$assembly.fasta"; fi
  "$mm" -x asm5 -t "$SLURM_CPUS_PER_TASK" --secondary=yes -N 50 -c "$base/GRCr8.mmi" "$fasta" > "$base/alignments/$assembly.paf.tmp" 2> "$base/logs/$assembly.minimap2.log"
  mv "$base/alignments/$assembly.paf.tmp" "$base/alignments/$assembly.paf"
done
python3 "$base/scripts/compare.py" "$base"
echo "finish=$(date -u -Is)"
