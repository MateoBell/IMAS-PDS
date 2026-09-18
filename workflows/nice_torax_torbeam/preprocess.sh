#!/usr/bin/env bash
set -euo pipefail

INPUT_DATA_DIR="${CASE_DIR}/input_data"
mkdir -p "$INPUT_DATA_DIR"

PREBAKED_DIR="/home/ITER/belloum/git/pds_06_2026/workflows/nice_torax_torbeam/mytest/scenarios/${SHOT}/tmp/data/${SHOT}_in"

if [ -d "$PREBAKED_DIR" ]; then
    echo "Copying pre-baked coupled input data from $PREBAKED_DIR"
    cp -f "$PREBAKED_DIR"/*.h5 "$INPUT_DATA_DIR/"
else
    echo "Generating coupled input data from SCENARIOS_REPO"
    python - << 'PYEOF'
import os
import imas

shot = os.environ.get("SHOT", "105099")
scenarios_repo = os.environ.get("SCENARIOS_REPO", "/work/projects/pds/pds-scenarios")
case_dir = os.environ["CASE_DIR"]
target_dir = f"{case_dir}/input_data"

src_in = f"imas:hdf5?path={scenarios_repo}/{shot}/data/in"
src_md = f"imas:hdf5?path={scenarios_repo}/{shot}/data/in_md"
dst = f"imas:hdf5?path={target_dir}"

db_dst = imas.DBEntry(dst, "w")
with imas.DBEntry(src_in, "r") as db_in:
    for name in ["equilibrium", "core_profiles", "core_sources", "pf_active"]:
        try:
            db_dst.put(db_in.get(name))
        except Exception:
            pass

with imas.DBEntry(src_md, "r") as db_md:
    for name in ["wall", "pf_passive", "iron_core"]:
        try:
            db_dst.put(db_md.get(name))
        except Exception:
            pass
db_dst.close()
PYEOF
fi

echo "Preprocessed input data materialized at $INPUT_DATA_DIR:"
ls -l "$INPUT_DATA_DIR"
