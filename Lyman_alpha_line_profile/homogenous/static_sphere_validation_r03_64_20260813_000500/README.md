# RASCAS Static-Sphere Validation at R=0.3, 64³

This directory is a self-contained validation of homogeneous Cartesian NumPy fields converted to a RAMSES-like octree, read into a spherical RASCAS domain, and compared with the analytical static-sphere Lyα solution.

The physical cases are `tau_1e05`, `tau_1e06`, and `tau_1e07`, all at 100 K. Cartesian density includes the inverse of the converter's factor 232.31332352. The source is monochromatic at 1215.67 Å and centred at `(0.5,0.5,0.5)`.

All PBS jobs are submitted to LEAP explicitly with `ssh leap /opt/pbs/bin/qsub`. Do not invoke the local `qsub` from Swarm. See `CODEX_WORKLOG.md` for exact commands/job IDs and `FINAL_VALIDATION_REPORT.md` for the result when complete.

Reproduction order:

1. Run `cartesian_input/generate_cartesian.py` for each optical depth.
2. Run `configs/prepare_configs.py`.
3. Submit `job_scripts/run_conversion.pbs` once per case and validate with `analysis/validate_ramses.py`.
4. Submit `job_scripts/run_domain.pbs` once per case and validate with `analysis/validate_domain.py`.
5. Submit `job_scripts/run_photons.pbs` for 100,000 and 1,000,000 packets; validate with `analysis/validate_photons.py`.
6. Submit `job_scripts/run_rascas.pbs` for the staged transport runs.
7. Run `analysis/compare_spectrum.py` for each completed result.

The converter and RASCAS trees are read-only inputs and are not copied or modified.

