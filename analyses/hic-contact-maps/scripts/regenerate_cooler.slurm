#!/bin/bash
#SBATCH --job-name=bn_hic_correct
#SBATCH --partition=allnodes
#SBATCH --exclude=octopus02,octopus06,tux06
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=2-00:00:00
#SBATCH --output=/moosefs/salehi/ref-refine/assemblies/analysis/hic_contact_maps/logs/correct_%j.out
#SBATCH --error=/moosefs/salehi/ref-refine/assemblies/analysis/hic_contact_maps/logs/correct_%j.err
set -euo pipefail
base=/moosefs/salehi/ref-refine/assemblies/analysis/hic_contact_maps
scripts=${SCRIPT_DIR:-$base/scripts}
assembly=${ASSEMBLY:?Set ASSEMBLY=hifiasm or verkko}
revision=${REVISION:?Set a NEW revision directory name}
[[ "$assembly" == hifiasm || "$assembly" == verkko ]]
[[ "$revision" =~ ^[A-Za-z0-9][A-Za-z0-9_.-]*$ ]]
[[ ${PAIRS_READY:-NO} == YES ]] || { echo 'Verify completed BWA/pairtools and dedup.stats, then set PAIRS_READY=YES' >&2; exit 2; }
source="$base/$assembly"
pairs="$source/results/valid_dedup.pairs"
sizes="$source/index/chrom.sizes"
test -s "$pairs" && test -s "$sizes" && test -s "$source/results/dedup.stats"
python=/home/salehi/miniconda3/envs/moddotplot/bin/python
receipt="$base/corrections/$revision/validation/$assembly.json"
expected_contacts=$("$python" - "$receipt" <<'PY'
import json, pathlib, sys
r = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert r['status'] == 'PASS' and r['records'] > 0
for entry in r['inputs'].values():
    p = pathlib.Path(entry['path']); s = p.stat()
    assert (s.st_size, s.st_mtime_ns, s.st_ctime_ns) == (entry['size'], entry['mtime_ns'], entry['ctime_ns']), str(p) + ' changed since validation'
print(r['records'])
PY
)
work="$base/corrections/$revision/$assembly"
mkdir -p "$(dirname "$work")"
mkdir "$work"  # Never overwrite any earlier corrected run, including partial runs.
mkdir "$work/cool" "$work/provenance" "$work/tmp"
export TMPDIR="$work/tmp"
export OMP_NUM_THREADS=1
cooler=/home/salehi/miniconda3/envs/moddotplot/bin/cooler
python=/home/salehi/miniconda3/envs/moddotplot/bin/python
{
 date -u -Is
 echo "job=$SLURM_JOB_ID assembly=$assembly revision=$revision coordinates=pairs_1based"
 "$cooler" --version
 stat "$pairs" "$sizes" "$source/results/dedup.stats"
 sha256sum "$sizes" "$scripts/regenerate_cooler.slurm" "$scripts/validate_cooler.py" "$scripts/plot_maps.py"
} > "$work/provenance/inputs.txt"
cp -p "$source/results/dedup.stats" "$work/provenance/"
cp -p "$receipt" "$work/provenance/pairs_validation.json"
cp -p "$scripts/"{regenerate_cooler.slurm,validate_cooler.py,plot_maps.py} "$work/provenance/"
stat -c '%s:%Y:%Z' "$pairs" > "$work/provenance/pairs.before"
"$cooler" cload pairs --assembly "$assembly" --input-copy-status unique \
 -c1 2 -p1 3 -c2 4 -p2 5 "$sizes:10000" "$pairs" "$work/cool/contacts.10000.cool"
"$cooler" zoomify --nproc 8 --chunksize 5000000 --resolutions 10000,50000,250000,1000000 \
 --balance --balance-args '--nproc 8 --convergence-policy error' \
 --out "$work/cool/contacts.mcool" "$work/cool/contacts.10000.cool"
"$python" "$work/provenance/validate_cooler.py" "$work" "$pairs" "$sizes" --cooler "$cooler" --expected-contacts "$expected_contacts"
stat -c '%s:%Y:%Z' "$pairs" > "$work/provenance/pairs.after"
cmp "$work/provenance/pairs.before" "$work/provenance/pairs.after"
"$python" "$work/provenance/plot_maps.py" "$base" "$assembly" --revision "$revision"
echo "Validated corrected outputs: $work"
