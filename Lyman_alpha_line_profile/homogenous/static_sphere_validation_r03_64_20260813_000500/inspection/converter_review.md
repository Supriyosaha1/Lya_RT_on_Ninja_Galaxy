# Converter Review

## Entry points and formats

- AMR: `/user1/supriyo/Gadget_to_Ramses_Converter/converter/write_amr.py`; hydro: `write_hydro.py`. Both accept `--config`, `--iout`, and `--serial`.
- Configuration-relative paths are resolved in `path_utils.py:30-47`, so a validation-owned absolute-path JSON is safe.
- Required field keys/filenames are configurable. This validation uses `density.npy`, `velocity_x.npy`, `velocity_y.npy`, `velocity_z.npy`, `metallicity.npy`, `internal_energy.npy`, and `scalar_01.npy`.
- Arrays are loaded with NumPy mmap and sampled as `field[ix,iy,iz]` (`write_hydro.py:217-227`), i.e. `(x,y,z)` order. Sampling is converted to contiguous little-endian float64 records.
- Hydro order is density, three velocity components, pressure, metallicity, internal energy, and scalar_01. Pressure is derived, not loaded: `P=(gamma-1)*rho*u` (`write_hydro.py:300-318`).
- Density is multiplied by `h0^2/aexp^3` (`write_hydro.py:72-85,277-280`); velocity and internal energy use their configured factors.
- A missing density/internal-energy file falls back to nonphysical values rather than failing (`write_hydro.py:246-249,277-308`), so this validation preflights every field.
- `scalar_01` is populated from config key `XHII`; it is not neutral fraction.
- `amr_hierarchy.py:35-53` makes a complete 8× hierarchy. With `nlevelmax=6`, level-6 has 32³ grids and 8 cells/grid, yielding 64³ leaves. All coarser cells are refined.
- The writers emit one RAMSES CPU domain regardless of MPI ranks (`write_hydro.py:117-123`). This validation uses serial execution.

## Units and outputs

- `write_amr.py` writes `info_00001.txt` from `info_block`, including `unit_l`, derived `unit_d=unit_m/unit_l^3`, and `unit_t=unit_l/unit_v`.
- Output is `output_00001/{amr,hydro}_00001.out00001` plus info and hydro descriptor. Particle files are unnecessary for gas-domain construction.
- Writers create/overwrite their target files. The job wrapper therefore rejects any existing `output_00001` before invoking them.

## Suspicious or potentially important findings

1. The repository default config points to an older external static-sphere directory and has `info_block.levelmin=1`; it is not suitable as-is. A validation-owned copied config sets absolute paths and `levelmin=6` without modifying the source config.
2. `amr_hierarchy.py:221-225` clears the last refinement flag after setting flags from `son`. This is suspicious, but the prior output was successfully read as 262,144 leaves by RASCAS. The validation will independently enforce the leaf count and stop if it differs.
3. `meta["boxlen"]` is hard-coded to 1.0 at `amr_hierarchy.py:316` rather than copied from config. That matches this test but is a general converter limitation.
4. The density multiplier is cosmological in form even though the RASCAS test is non-cosmological. It is left unchanged as required and exactly inverted in the Cartesian input.
5. No input shape-consistency check exists across fields; validation performs this before conversion.

