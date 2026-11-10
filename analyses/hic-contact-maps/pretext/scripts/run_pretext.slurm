#!/bin/bash
#SBATCH --job-name=bn_pretext
#SBATCH --partition=allnodes
#SBATCH --exclude=octopus02,octopus06,tux06
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=2-00:00:00
#SBATCH --output=/moosefs/salehi/ref-refine/assemblies/analysis/hic_contact_maps/pretext/logs/pretext_%j.out
#SBATCH --error=/moosefs/salehi/ref-refine/assemblies/analysis/hic_contact_maps/pretext/logs/pretext_%j.err
set -euo pipefail
root=/moosefs/salehi/ref-refine/assemblies
base="$root/analysis/hic_contact_maps"
pretext=/home/salehi/miniconda3/envs/pretext/bin/PretextMap
snapshot=/home/salehi/miniconda3/envs/pretext/bin/PretextSnapshot
pairs_root="$base"
printf 'job=%s node=%s start=%s\n' "$SLURM_JOB_ID" "$(hostname)" "$(date -u -Is)"
printf 'PretextMap package=0.2.4; PretextSnapshot package=%s\n' "$("$snapshot" --version)"
printf 'filtering inherited from pairtools workflow: MAPQ>=30; walks-policy=5unique; deduplicated pairs\n'
for assembly in hifiasm verkko; do
    work="$pairs_root/$assembly"
    pairs="$work/results/valid_dedup.pairs"
    out="$base/pretext/$assembly"
    mkdir -p "$out/snapshots"
    test -s "$pairs"
    # Confirm standard pairs-format metadata and a syntactically plausible first record.
    grep -q '^#columns:.*chrom1.*pos1.*chrom2.*pos2' "$pairs"
    awk 'BEGIN{FS="\t"} /^#/ {next} NF>=7 {if ($2=="" || $4=="" || $3 !~ /^[0-9]+$/ || $5 !~ /^[0-9]+$/) exit 1; ok=1; exit} END{if (!ok) exit 1}' "$pairs"
    printf 'assembly=%s pairs=%s\n' "$assembly" "$pairs"
    "$pretext" -o "$out/${assembly}.pretext" --sortby length --sortorder descend --highRes < "$pairs"
    test -s "$out/${assembly}.pretext"
    "$snapshot" --map "$out/${assembly}.pretext" --sequences '=full' --resolution 3000 --format png --folder "$out/snapshots" --prefix "${assembly}_overview_"
done
printf 'finish=%s\n' "$(date -u -Is)"
