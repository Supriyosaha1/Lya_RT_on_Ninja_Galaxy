# CODEX Work Log — RASCAS Static-Sphere Validation

## 2026-08-13 00:05:16 IST — Initialization

- Objective: validate the Cartesian-to-RAMSES-octree-to-RASCAS pipeline against the analytical homogeneous static-sphere Lyα spectrum.
- Validation root: `/user1/supriyo/Lya_RT_on_Ninja_Galaxy/Lyman_alpha_line_profile/homogenous/static_sphere_validation_r03_64_20260813_000500`
- Safety: converter source, RASCAS source/executables, and prior reference runs are read-only.
- Cluster: submit and monitor only through `ssh leap /opt/pbs/bin/...`; the interactive host is Swarm and its local PBS server must not be used.
- Requested cases: τ₀ = 10^5, 10^6, 10^7 at T = 100 K, R = 0.3 box units, 64³ cells.
- Command executed: `test ! -e <validation-root> && mkdir <validation-root>`.
- Status: PASSED

## 2026-08-13 00:48 IST — τ₀=10⁶ analysis and τ₀=10⁷ submission

- Job `943186.leap` exited 0 after 13m40s; RASCAS reported 815.721 s internally and wrote a complete 7.3 MB `Cont.res`.
- All 100,000 packets escaped with status 1.
- τ₀=10⁶ metrics: peaks `x=-15.25,+15.25` versus expected `|x|=15.6156`; red/blue ratio `1.00336565`; symmetry fraction `0.00168`; centre probability `5e-5`; normalized L1 difference `0.0649187`.
- Conclusion for the τ₀=10⁶ smoke comparison: PASS.
- At user request, submitted τ₀=10⁷ smoke job `943187.leap` with 5 nodes × 32 ranks = 160 MPI ranks, scatter placement, and 12-hour walltime. Target was confirmed absent before submission.
- Added `ANALYTIC_COMPARISON_METHOD.md` explaining the analytical equation, normalization, Fortran binary records, frequency conversion, histogram/plots, diagnostics, and physical interpretation.
- Status: τ₀=10⁶ PASSED; τ₀=10⁷ SUBMITTED

## 2026-08-13 00:49 IST — τ₀=10⁷ job start confirmation

- Job `943187.leap` is RUNNING on the requested five LEAP nodes with `select=5:ncpus=32:mpiprocs=32` and 12-hour walltime.
- No additional production jobs were submitted because the final million-photon stages depend on this smoke run passing.
- Status: RUNNING

## 2026-08-13 00:38 IST — Focused τ₀=10⁵ analytical verification

- User requested explicit verification of the τ₀=10⁵ analytic comparison while keeping τ₀=10⁶ running.
- Dense analytical grid gives normalization `1.0000000000000002`, `a*tau0=471.8729545`, and exact positive peak `x=7.2480`.
- Added `analysis/tau_1e05/ANALYTICAL_VERIFICATION.md`; conclusion is PASS for the diagnostic case with the diffusion-limit caveat.
- Job `943186.leap` was not altered and remains under active monitoring.
- Status: PASSED

## 2026-08-13 00:27 IST — First smoke transport submitted

- Case/stage: `tau_1e05/smoke`, 100,000 photons.
- LEAP job: `943185.leap`; resources: MPI queue, 3 nodes × 32 ranks, scatter placement, 12 hours.
- Status: SUBMITTED

## 2026-08-13 00:33 IST — τ₀=10^5 smoke complete

- Job `943185.leap` waited for three nodes, then exited 0 after 76 seconds; peak memory 2.09 GB and CPU time 39m36s across ranks.
- RASCAS used 95 workers and the intended new sphere/domain/photon/config files.
- Log emitted rare spherical-boundary roundoff warnings of 3–11 machine-precision units; all 100,000 packets nevertheless ended with escaped status 1.
- Spectrum: red peak `x=-7.25`, blue peak `x=6.75`, expected |x|≈7.248; red/blue ratio 1.00977; L1 difference 0.11329.
- This case passes its smoke/diagnostic role despite `a*tau0<1000`.
- Status: PASSED

## 2026-08-13 00:26 IST — Photon generation and validation

- LEAP jobs `943183.leap` (100,000 packets) and `943184.leap` (1,000,000 packets) exited 0.
- Fortran-record validation confirms exact counts, unique IDs, seed `-20260813`, central positions, zero source velocity, unit directions, and a single finite line-centre frequency `2.466067748648893e15 Hz`.
- Photon files: `photons/n1e5/Cont.IC` (8.4 MB) and `photons/n1e6/Cont.IC` (84 MB).
- Status: PASSED

## 2026-08-13 00:23 IST — Domain creation and validation

- LEAP jobs: `943180.leap` (`tau_1e05`), `943181.leap` (`tau_1e06`), `943182.leap` (`tau_1e07`); all exited 0 in ≤1 second.
- Each dump contains 33,696 selected level-6 leaves, 5,553 octs, and exact sphere geometry centre `(0.5,0.5,0.5)`, radius `0.3`.
- Dumped gas is homogeneous at the expected nHI, 100 K, and exactly zero velocity, turbulence, and dust.
- Six axis and 32 seeded random centre-to-surface rays use the exact clipped spherical path; measured τ₀ equals requested τ₀ to floating precision in all cases.
- Results and PNG/PDF diagnostics are under `analysis/<case>/domain/`.
- Status: PASSED

## 2026-08-13 00:15 IST — LEAP conversion submissions

- Submission command pattern: `ssh leap /opt/pbs/bin/qsub -v VALIDATION_ROOT=<root>,CASE=<case> -o <root>/logs/pbs_conversion_<case>.out job_scripts/run_conversion.pbs`.
- `tau_1e05`: job `943174.leap`.
- `tau_1e06`: job `943175.leap`.
- `tau_1e07`: job `943176.leap`.
- Resources per job: LEAP `serial`, 1 CPU, 8 GB, 2 hours.
- Output guards reject any pre-existing `output_00001`.
- Status: SUBMITTED

## 2026-08-13 00:20 IST — Conversion and RAMSES validation complete

- Retry jobs `943177.leap`, `943178.leap`, `943179.leap` exited 0 in 8–9 seconds.
- yt independently loaded each output as a non-cosmological `[64,64,64]` dataset with exactly 262,144 leaves.
- All cases have exact zero velocity/metallicity/scalar_01, uniform expected density/internal energy/pressure, and recovered temperature 100 K (floating error ≤ 1.4e-14 K).
- Per-case machine-readable results: `analysis/<case>/ramses/validation.json`.
- Status: PASSED

## 2026-08-13 00:17 IST — Conversion failure diagnosis

- Jobs `943174.leap`, `943175.leap`, and `943176.leap` all exited 1 after 15 seconds.
- Earliest error: `activate-binutils_linux-64.sh: line 68: ADDR2LINE: unbound variable` during `conda activate rascas-env` under `set -u`.
- No `output_00001` directory was produced in any case.
- Safe fix applied only to the validation PBS wrapper: invoke `/user1/supriyo/miniconda3/envs/rascas-env/bin/python` directly and skip Conda activation.
- Status: FAILED (diagnosed; safe resubmission prepared)

## 2026-08-13 00:18 IST — Conversion resubmission

- Confirmed all three guarded RAMSES target directories remain absent.
- Retry job IDs: `943177.leap` (`tau_1e05`), `943178.leap` (`tau_1e06`), `943179.leap` (`tau_1e07`).
- Status: SUBMITTED

## 2026-08-13 00:14 IST — Inspection, Cartesian inputs, and configurations

- Added converter, RASCAS-reader, and reference-pipeline reviews with source locations and suspicious findings.
- Recorded SHA-256 baselines for protected converter/RASCAS files and executables.
- Generated and reloaded all fields for `tau_1e05`, `tau_1e06`, and `tau_1e07`; all are `(64,64,64)`, float64, finite, C-contiguous, and homogeneous.
- Exact Cartesian densities: `2.577739764233766e-08`, `2.577739764233766e-07`, `2.5777397642337664e-06`.
- Exact internal energy: `1.0152911700772016`; velocities, metallicity, and xHII are exactly zero.
- Generated validation-owned converter/CDD/photon/RASCAS configs and PBS scripts. `bash -n` and Python byte compilation passed.
- RASCAS mock directions are set to zero because the required spectrum comes from escaped photons in `Cont.res`; photon transport physics is unchanged.
- Status: PASSED

## 2026-08-13 00:08 IST — Physics and Cartesian generator

- Confirmed available analysis stack in `rascas-env`: NumPy 1.26.4, SciPy 1.12.0, Matplotlib 3.9.4, yt 4.3.1.
- Implemented `analysis/physics.py` from the installed RASCAS constants and COLT line-centre approximation.
- Implemented `cartesian_input/generate_cartesian.py`; it refuses existing case directories, writes C-contiguous float64 fields, reloads them, validates invariants, and makes PNG/PDF central slices.
- Density input accounts for the converter factor `0.6736^2 / 0.125^3 = 232.31332352`.
- `pressure.npy` is diagnostic only; `write_hydro.py` derives pressure as `(gamma-1)*density*internal_energy`.
- Status: PASSED
