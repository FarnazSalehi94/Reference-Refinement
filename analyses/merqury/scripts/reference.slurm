#!/bin/bash
#SBATCH --job-name=bn_grcr8_reference
#SBATCH --partition=allnodes
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=2-00:00:00
#SBATCH --output=/moosefs/salehi/ref-refine/assemblies/analysis/merqury/logs/reference_%j.out
#SBATCH --error=/moosefs/salehi/ref-refine/assemblies/analysis/merqury/logs/reference_%j.err
set -euo pipefail
root=/moosefs/salehi/ref-refine/assemblies/analysis
out="$root/merqury/reference"
cd "$out"
name=GCF_036323735.1_GRCr8_genomic.fna.gz
url=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/036/323/735/GCF_036323735.1_GRCr8
wget -c --tries=15 --timeout=90 "$url/$name"
wget -O md5checksums.txt "$url/md5checksums.txt"
awk -v f="./$name" '$2==f {print}' md5checksums.txt > expected.md5
test -s expected.md5
md5sum -c expected.md5
gzip -t "$name"
gzip -dc "$name" > GRCr8.fasta.tmp
mv GRCr8.fasta.tmp GRCr8.fasta
/home/salehi/miniconda3/envs/verkko/bin/samtools faidx --fai-idx "$out/GRCr8.fai" "$out/GRCr8.fasta"
cut -f1,2 "$out/GRCr8.fai" > "$out/reference_ids_lengths.tsv"
cut -f1,2 "$root/GRCr8.fai" > "$out/index_ids_lengths.tsv"
if ! cmp -s "$out/reference_ids_lengths.tsv" "$out/index_ids_lengths.tsv"; then echo 'Reference and existing minimap index source differ in IDs or lengths' >&2; exit 1; fi
