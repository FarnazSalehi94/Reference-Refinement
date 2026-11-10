#!/bin/bash
#SBATCH --job-name=bn_hic_pairs_qc
#SBATCH --partition=allnodes
#SBATCH --exclude=octopus02,octopus06,tux06
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=1-00:00:00
#SBATCH --output=/moosefs/salehi/ref-refine/assemblies/analysis/hic_contact_maps/logs/pairs_qc_%j.out
#SBATCH --error=/moosefs/salehi/ref-refine/assemblies/analysis/hic_contact_maps/logs/pairs_qc_%j.err
set -euo pipefail
base=/moosefs/salehi/ref-refine/assemblies/analysis/hic_contact_maps
scripts=${SCRIPT_DIR:?Set approved snapshot directory}
revision=${REVISION:?}
assembly=${ASSEMBLY:?}
job=${MAPPING_JOB:?}
/home/salehi/miniconda3/envs/moddotplot/bin/python "$scripts/validate_pairs.py" \
 "$base" "$assembly" --mapping-job "$job" \
 --output "$base/corrections/$revision/validation/$assembly.json"
