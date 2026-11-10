#!/bin/bash
#SBATCH --job-name=bn_hic_plots
#SBATCH --partition=allnodes
#SBATCH --exclude=octopus02,octopus06,tux06
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=2-00:00:00
#SBATCH --output=/moosefs/salehi/ref-refine/assemblies/analysis/hic_contact_maps/logs/plots_%j.out
#SBATCH --error=/moosefs/salehi/ref-refine/assemblies/analysis/hic_contact_maps/logs/plots_%j.err
set -euo pipefail
root=/moosefs/salehi/ref-refine/assemblies/analysis/hic_contact_maps
python=/home/salehi/miniconda3/envs/moddotplot/bin/python
# Explicit corrected revision is mandatory; never consume legacy Cooler files.
revision=${REVISION:?Set REVISION to a validated corrected run}
for asm in hifiasm verkko; do
 "$python" "$root/scripts/plot_maps.py" "$root" "$asm" --revision "$revision"
done
