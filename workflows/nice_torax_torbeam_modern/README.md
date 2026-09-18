# nice_torax_torbeam_modern

Modern PDS coupled multi-physics MUSCLE3 workflow combining NICE inverse equilibrium reconstruction, TORAX core transport, and TORBEAM EC heating.

## Architecture

1. **NICE Inverse (`nice_inv`)**: Free-boundary equilibrium reconstruction from scenario magnetic boundaries and coil configurations.
2. **TORAX (`torax`)**: 1D core transport solver evolving kinetic profiles ($T_e, T_i, n_e$) and current density $j_\parallel$.
3. **HCD Workflow (`hcd_workflow` / `run_torbeam`)**: Electron Cyclotron Heating and Current Drive (ECRH/ECCD) coordinator.
4. **TORBEAM (`torbeam`)**: Paraxial beam tracing code modeling wave propagation and relativistic absorption.
5. **HCD2CORE_SOURCES (`hcd2core_sources`)**: Converts wave energy and momentum absorption into standard IMAS `core_sources` power and current drive profiles.
6. **OLC Validator (`validator`)**: Checks operational limits on coil currents (`iter-olc`).
7. **Sinks (`sink_nice`, `sink_torax`, `sink_hcd`, `sink_oi_hcd`)**: Record time-resolved output IDSs.

---

## Setup & Configuration for New Users

### 1. Shared Library `libtorbeamIMAS.so`

The TORBEAM executable dynamically links against `libtorbeamIMAS.so`. In PDS, this library is hosted in:
```
workflows/nice_torax_torbeam/lib/libtorbeamIMAS.so
```

- **If you are a new user or rebuilding TORBEAM**:
  Ensure that your compiled `libtorbeamIMAS.so` is placed into `workflows/nice_torax_torbeam/lib/`:
  ```bash
  mkdir -p workflows/nice_torax_torbeam/lib
  cp /path/to/your/build/lib/libtorbeamIMAS.so workflows/nice_torax_torbeam/lib/libtorbeamIMAS.so
  ```

> [!NOTE]
> `libtorbeamIMAS.so` depends on `libal-fortran-4.1.0.so`. The actor definition in `workflows/lib/local_programs.ymmsl` automatically includes `/work/imas/opt/EasyBuild/software/IMAS-Fortran/5.5.0-intel-2023b-DD-4.1.0/lib` in `LD_LIBRARY_PATH` so all symbols resolve cleanly at runtime.

### 2. Pointing to a Custom TORBEAM Executable

By default, the workflow executes the public TORBEAM binary:
```
/home/ITER/schneim/public/PYTHON_ACTORS/torbeam/torbeam_m3.exe
```

If you have built your own `torbeam_m3.exe` (or want to test an updated version), you can point the workflow to it using either of the following methods:

- **Method A: Set `TORBEAM_EXE` in `env.sh` (Recommended)**
  Edit `workflows/nice_torax_torbeam_modern/env.sh`:
  ```bash
  export TORBEAM_EXE="/path/to/your/torbeam_m3.exe"
  ```
  `bin/pds-run-case.sbatch` automatically sources `env.sh` before starting MUSCLE3, so the custom binary will be used without altering repository configuration files.

- **Method B: Edit `workflows/lib/local_programs.ymmsl`**
  Modify the `torbeam` entry in [workflows/lib/local_programs.ymmsl](file:///home/ITER/belloum/git/pds_09_2026/workflows/lib/local_programs.ymmsl):
  ```yaml
  torbeam:
    script: |
      ...
      TORBEAM_EXE="${TORBEAM_EXE:-/path/to/your/torbeam_m3.exe}"
  ```

---

## Running the Workflow

### 1. Materialize a Case
```bash
export SCENARIOS_REPO=/work/projects/pds/pds-scenarios   # default location
bin/pds-create-case nice_torax_torbeam_modern 105099    # -> cases/nice_torax_torbeam_modern_105099
```

`pds-create-case` stacks:
- `workflow.ymmsl` (component definitions, coupling topology)
- `settings.ymmsl` (generic case parameters, resource allocations)
- `cases/overrides/nice_torax_torbeam_modern_<shot>.ymmsl` (shot-specific overrides)

All configuration files (`config_nice.xml`, `config_torax.py`, `input_torbeam.xml`, `input_hcd2core_sources.xml`, `ec_waveforms.yaml`) are localized and frozen into `cases/<case_name>/config/`.

### 2. Submit to Slurm
```bash
sbatch bin/pds-run-case.sbatch cases/nice_torax_torbeam_modern_105099
```

### 3. Verify Output Against Baseline
Once the simulation completes, compare the generated profiles and equilibrium against baseline results:

```bash
module load PDS
python3 workflows/nice_torax_torbeam/compare_to_baseline.py cases/runs/nice_torax_torbeam_modern_105099_<timestamp>
```

