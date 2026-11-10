#!/bin/bash
#SBATCH --job-name=bn_hic_submit_corrected
#SBATCH --partition=allnodes
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:10:00
#SBATCH --no-requeue
#SBATCH --output=/moosefs/salehi/ref-refine/assemblies/analysis/hic_contact_maps/logs/submit_corrected_%j.out
#SBATCH --error=/moosefs/salehi/ref-refine/assemblies/analysis/hic_contact_maps/logs/submit_corrected_%j.err
# This lightweight job submits regeneration only AFTER both completed pairs pass QC.
set -euo pipefail
base=/moosefs/salehi/ref-refine/assemblies/analysis/hic_contact_maps
revision=${REVISION:?}
scripts=${SCRIPT_DIR:?}
root="$base/corrections/$revision"
/home/salehi/miniconda3/envs/moddotplot/bin/python - "$root" <<'PY'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
for assembly in ('hifiasm', 'verkko'):
    r = json.loads((root/'validation'/f'{assembly}.json').read_text())
    assert r['status'] == 'PASS' and r['records'] > 0
    assert not (root/assembly).exists(), 'Refusing to overwrite an earlier revision'
PY
manifest="$root/submitted_regeneration.tsv"
(set -o noclobber; printf 'assembly\tjob_id\tsubmitted_utc\n' > "$manifest")
for assembly in hifiasm verkko; do
 job=$(sbatch --parsable --export="ALL,ASSEMBLY=$assembly,REVISION=$revision,PAIRS_READY=YES,SCRIPT_DIR=$scripts" \
       "$scripts/regenerate_cooler.slurm")
 printf '%s\t%s\t%s\n' "$assembly" "$job" "$(date -u -Is)" | tee -a "$manifest"
done
