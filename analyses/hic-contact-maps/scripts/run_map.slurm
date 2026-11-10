#!/bin/bash
#SBATCH --job-name=bn_hic_map
#SBATCH --partition=allnodes
#SBATCH --exclude=octopus02,octopus06,tux06
#SBATCH --cpus-per-task=32
#SBATCH --mem=192G
#SBATCH --time=7-00:00:00
#SBATCH --output=/moosefs/salehi/ref-refine/assemblies/analysis/hic_contact_maps/logs/map_%x_%j.out
#SBATCH --error=/moosefs/salehi/ref-refine/assemblies/analysis/hic_contact_maps/logs/map_%x_%j.err
set -euo pipefail
root=/moosefs/salehi/ref-refine/assemblies
base="$root/analysis/hic_contact_maps"
assembly=${ASSEMBLY:?Set ASSEMBLY=hifiasm or verkko}
case "$assembly" in
 hifiasm) fasta="$root/hifiasm/run_2871178/primary.fasta";;
 verkko) fasta="$root/verkko/run_2871179/assembly/assembly.fasta";;
 *) echo "Unsupported assembly: $assembly" >&2; exit 2;;
esac
work="$base/$assembly"
mkdir -p "$work/index" "$work/tmp" "$work/results" "$work/cool"
export TMPDIR="$work/tmp"
bwa=/home/salehi/miniconda3/envs/verkko/bin/bwa
pairtools=/home/salehi/miniconda3/envs/hic_contact/bin/pairtools
cooler=/home/salehi/miniconda3/envs/moddotplot/bin/cooler
samtools=/home/salehi/miniconda3/envs/verkko/bin/samtools
r1="$root/inputs/ERR5309023_1.fastq"
r2="$root/inputs/ERR5309023_2.fastq"
echo "assembly=$assembly node=$(hostname) job=$SLURM_JOB_ID start=$(date -u -Is)"
echo "BWA: $($bwa 2>&1 | sed -n '2p')"
echo "pairtools: $($pairtools --version)"
echo "cooler: $($cooler --version)"
test -r "$fasta" && test -s "$fasta" && test -r "$r1" && test -r "$r2"
"$samtools" faidx --fai-idx "$work/index/assembly.fai" "$fasta"
cut -f1,2 "$work/index/assembly.fai" > "$work/index/chrom.sizes"
"$bwa" index -p "$work/index/ref" "$fasta"
"$bwa" mem -5SP -T0 -t "$SLURM_CPUS_PER_TASK" -K 100000000 "$work/index/ref" "$r1" "$r2" 2> "$work/results/bwa.log" \
 | "$pairtools" parse --assembly "$assembly" --chroms-path "$work/index/chrom.sizes" --min-mapq 30 --walks-policy 5unique --nproc-in 8 --nproc-out 8 \
 | "$pairtools" sort --nproc 16 --tmpdir "$work/tmp" \
 | "$pairtools" dedup --mark-dups --output-stats "$work/results/dedup.stats" --nproc-in 8 --nproc-out 8 \
 | "$pairtools" split --output-pairs "$work/results/valid_dedup.pairs" --output-sam /dev/null --nproc-in 8 --nproc-out 8

test -s "$work/results/valid_dedup.pairs"
# Standard pairtools .pairs positions are 1-based; Cooler converts internally.
"$cooler" cload pairs --assembly "$assembly" --input-copy-status unique -c1 2 -p1 3 -c2 4 -p2 5 \
 "$work/index/chrom.sizes:10000" "$work/results/valid_dedup.pairs" "$work/cool/contacts.10000.cool"
"$cooler" zoomify --nproc 8 --chunksize 5000000 --resolutions 10000,50000,250000,1000000 --balance \
 --balance-args '--nproc 8' --out "$work/cool/contacts.mcool" "$work/cool/contacts.10000.cool"
echo "finish=$(date -u -Is)"
