# CODEX Work Log — RASCAS Static-Sphere Validation

## 2026-08-13 — Matched optical-depth/photon-count overlay requested

- Requested combined linear overlay pairs are `(tau_1e05,n1e5)`, `(tau_1e06,n1e6)`, and `(tau_1e07,n1e7)`, plus an input-spectrum indication in individual plots.
- Read-only inventory found only the first matched result. Existing τ₀=10⁶ and τ₀=10⁷ smoke outputs each contain 100,000 photons and cannot truthfully be substituted for the requested one-million and ten-million results.
- Updated individual linear/log plotting to mark the monochromatic input at `x=0` with a vertical dotted line. A Dirac-delta input cannot be represented as an ordinary finite-height density on the same ordinate.
- Added isolated, guarded RASCAS configs for the genuinely missing `tau_1e06/n1e6` and `tau_1e07/n1e7` results, reusing the already validated n1e6 and n1e7 photon IC files.
- Status: IMPLEMENTATION IN PROGRESS

## 2026-08-13 — Overlay scope corrected by user

- User clarified that no matched photon-count transports are wanted. The requested combined plot uses the already completed `smoke` results at τ₀=`1e5`, `1e6`, and `1e7`, each containing 100,000 photons.
- No new transport job had been submitted. Removed the newly drafted, unused matched-run configs and PBS wrappers.
- Retargeted the combined plotting program to the three existing smoke binaries and output directory `analysis/existing_tau_overlay/`.
- Status: PLOTTING IN PROGRESS

## 2026-08-13 — Existing three-optical-depth overlay complete

- Reparsed the original Fortran `Cont.res` binaries for τ₀=`1e5`, `1e6`, and `1e7`; each plotted smoke result contains exactly 100,000 successfully escaped photons.
- Regenerated all available individual linear and logarithmic spectrum plots with a crimson dotted marker labeled `input: monochromatic x=0`. This is a location marker for the delta-function input, not a finite-height output-density curve.
- Created `analysis/existing_tau_overlay/three_tau_existing_linear.{png,pdf}`. It overlays the three RASCAS spectra as solid colored steps, the three corresponding analytical curves as same-color dashed lines, and the common line-centre input marker.
- Wrote the plotted raw counts/PDFs/models to `three_tau_existing.csv` and validation metrics to `three_tau_existing_metrics.json`. Each spectrum integrates to unity; L1 values remain `0.1132904`, `0.0649187`, and `0.0446249` from τ₀=1e5 through 1e7.
- Visually inspected both the combined figure and an individual τ₀=1e6 figure; labels, input marker, curves, axes, and legends render correctly.
- Status: PASSED

## 2026-08-13 — Long-form LaTeX report compilation checkpoint

- Created `STATIC_SPHERE_VALIDATION_REPORT.tex`, a first-person, step-by-step scientific report covering parameter selection, atomic constants, temperature/internal energy, density derivation, the converter multiplier, Cartesian construction, RAMSES octree conversion, domain/ray validation, photon binaries, transport, analytical normalization, plotting, uncertainties, and case-by-case interpretation.
- The first `pdflatex` pass stopped because this host's minimal TeX installation lacks `siunitx.sty`. No PDF was produced. Removed that nonessential package and replaced its single unit-formatting command with standard LaTeX; scientific content is unchanged.
- Status: COMPILATION RETRY IN PROGRESS

## 2026-08-13 01:58 IST — Long-form LaTeX report complete

- Adapted the source to the host's minimal TeX installation by removing unavailable convenience packages (`siunitx`, `cleveref`, and `enumitem`) while preserving all equations and content.
- Compiled `STATIC_SPHERE_VALIDATION_REPORT.tex` three times with `pdflatex` to resolve the table of contents and cross-references.
- Final output is a 15-page A4 PDF, `STATIC_SPHERE_VALIDATION_REPORT.pdf` (approximately 308 KiB), with embedded linear/log τ₀=10⁵ one-million-photon figures and τ₀=10⁶/10⁷ comparison figures.
- Final compile contains no undefined-reference, float-size, overfull-box, LaTeX, or fatal-error warnings. Text extraction confirms the complete abstract, contents, conclusions, reproducibility map, and calculation recipe are present.
- Status: PASSED

## 2026-08-13 — Requested τ₀=10⁵, one-million-photon analytical plot

- Confirmed LEAP job `943195.leap` completed successfully with exit status 0 after 18m09s and produced the 73 MiB `rascas_run/tau_1e05/n1e6/Cont.res`.
- Extended the existing spectrum comparison interface to accept photon-count folder labels while retaining its established Fortran parsing, Doppler-frequency conversion, analytical equation, normalization, and diagnostics.
- Status: ANALYSIS IN PROGRESS

## 2026-08-13 01:47 IST — τ₀=10⁵, one-million-photon verification complete

- Parsed the complete RASCAS Fortran result and selected all successfully escaped packets without an angular cut: 1,000,000 of 1,000,000 packets have terminal status 1.
- Generated PNG/PDF linear, logarithmic, residual, fractional-residual, folded-half, and Poisson-count plots plus `spectrum.csv`, `spectrum_metrics.json`, and `VERIFICATION.md` under `analysis/tau_1e05/n1e6/`.
- RASCAS peaks are `x=-7.25,+7.25`, compared with analytical `|x|=7.2481089`; red/blue count ratio is `0.9993562`, symmetry fraction `0.000322`, and normalized L1 difference `0.1124296`.
- Interpretation: successful lower-`a*tau0` diagnostic with excellent peak position and symmetry. The residual profile-shape offset is consistent with the analytical diffusion-limit caveat at `a*tau0≈472` and documented core skipping.
- Status: PASSED AS DIAGNOSTIC

## 2026-08-13 — τ₀=10⁵ photon-count convergence requested

- New requested experiment: hold the gas sphere fixed at `tau0=1e5` and compare `100,000`, `1,000,000`, and `10,000,000` photon packets in sibling run folders `n1e5`, `n1e6`, and `n1e7`.
- Required plot: one overlaid all-direction spectrum panel containing all three Monte Carlo spectra and the common analytical static-sphere curve.
- Initial read-only inspection confirmed the prior `tau_1e05/smoke` result used 100,000 packets, while validated reusable photon IC files already exist for `n1e5` and `n1e6`; an `n1e7` photon IC must be generated.
- The previously discussed τ₀=10⁷, 100-million-packet transport is not part of this new comparison and is not being submitted in this step.
- Status: IN PROGRESS

## 2026-08-13 — τ₀=10⁵ convergence implementation checkpoint

- Created `rascas_run/tau_1e05/n1e5`, `n1e6`, and `n1e7`, each with an isolated `Cont.cfg` and guarded output path.
- All three configs reference the identical validated τ₀=10⁵ domain and identical physics. `nDirections=0` means the comparison uses the angle-integrated set of all escaped photons rather than a selected viewing cone.
- Created `photons/n1e7/PPIC.cfg` for exactly 10,000,000 central, zero-velocity, monochromatic packets with the established seed `-20260813`; existing validated n1e5 and n1e6 IC files remain unchanged.
- Extended the streaming photon validator to n1e7 and made the generic photon PBS job validate its binary before returning success.
- Added a guarded two-node/64-rank transport PBS script, a dependent analysis PBS script, and `analysis/compare_tau1e5_photon_counts.py`. The latter produces one single-axis overlay of all three unit-area spectra plus the common analytical curve, along with JSON metrics and CSV bins.
- Shell syntax, Python byte compilation, output-absence guards, paths, packet count, source properties, and protected input checksums passed.
- Status: READY TO SUBMIT

## 2026-08-13 01:24 IST — τ₀=10⁵ photon-count convergence submitted

- LEAP photon-generation job `943193.leap` completed successfully in 13 seconds. It produced an 840 MiB `photons/n1e7/Cont.IC`; streaming validation passed the exact 10,000,000 count, sequential unique IDs, central position, zero source velocity, line-centre frequency, unit directions, and packet seeds.
- Submitted three independent τ₀=10⁵ transports, each requesting 2 nodes × 32 ranks = 64 MPI ranks for up to 12 hours: `943194.leap` (`n1e5`), `943195.leap` (`n1e6`), and `943196.leap` (`n1e7`). All three are RUNNING.
- Submitted analysis job `943197.leap`, dependency-held on successful completion of all three transports. It will automatically create the one-panel all-direction overlay in `analysis/tau_1e05/photon_count_comparison/`.
- Expected primary plot names: `all_directions_overlay.png` and `all_directions_overlay.pdf`; numeric products: `metrics.json` and `spectra.csv`.
- Status: TRANSPORTS RUNNING; ANALYSIS QUEUED

## 2026-08-13 — n1e7 resource-change checkpoint

- User requested cancellation of τ₀=10⁵ `n1e7` job `943196.leap` and replacement with exactly 6 nodes × 32 ranks = 192 MPI ranks.
- Pre-cancellation check: `943196.leap` is RUNNING after 14m48s; no `n1e7/Cont.res` exists, so there is no result binary to delete or overwrite. Its diagnostic log and host files will be preserved.
- `n1e5` job `943194.leap` has already completed successfully (exit 0); `n1e6` job `943195.leap` remains RUNNING on 64 ranks.
- The old dependent analysis job `943197.leap` is no longer usable after replacing its n1e7 dependency and will be replaced with a new dependency-bound analysis job.
- Status: CANCELLATION AUTHORIZED; REPLACEMENT PREPARING

## 2026-08-13 01:42 IST — n1e7 restarted on six full nodes

- Cancelled only old τ₀=10⁵ n1e7 transport `943196.leap`. PBS confirms terminal exit status `271` after 16m44s, which is the requested deletion; it produced no `Cont.res`, so no result file required removal. Its partial execution log remains preserved.
- Added and shell-validated `job_scripts/run_tau1e05_n1e7_6nodes.pbs` with mandatory checks for exactly 6 distinct nodes and 192 MPI slots.
- Submitted replacement job `943198.leap`. It is RUNNING with `select=6:ncpus=32:mpiprocs=32`; its own startup log confirms 6 nodes and 192 ranks. Allocated hosts are compute-4-2, compute-4-4, compute-4-5, compute-4-6, compute-4-8, and compute-4-12, each supplying 32 slots.
- Old analysis dependency job `943197.leap` terminated when its old n1e7 prerequisite was cancelled. Submitted replacement analysis job `943199.leap`, held on `afterok:943195.leap:943198.leap`, so it will run after the ongoing n1e6 case and replacement n1e7 case both succeed.
- New six-node runtime log: `logs/rascas_tau_1e05_n1e7_6nodes_943198.leap.log`.
- Status: SIX-NODE N1E7 RUNNING; REPLACEMENT ANALYSIS QUEUED

## 2026-08-13 00:05:16 IST — Initialization

- Objective: validate the Cartesian-to-RAMSES-octree-to-RASCAS pipeline against the analytical homogeneous static-sphere Lyα spectrum.
- Validation root: `/user1/supriyo/Lya_RT_on_Ninja_Galaxy/Lyman_alpha_line_profile/homogenous/static_sphere_validation_r03_64_20260813_000500`
- Safety: converter source, RASCAS source/executables, and prior reference runs are read-only.
- Cluster: submit and monitor only through `ssh leap /opt/pbs/bin/...`; the interactive host is Swarm and its local PBS server must not be used.
- Requested cases: τ₀ = 10^5, 10^6, 10^7 at T = 100 K, R = 0.3 box units, 64³ cells.
- Command executed: `test ! -e <validation-root> && mkdir <validation-root>`.
- Status: PASSED

## 2026-08-13 01:11 IST — 100-million-photon production preparation

- User requested a `100,000,000`-packet τ₀=10⁷ production run on all eight LEAP nodes while smoke job `943187.leap` remains running.
- Added isolated photon config `photons/n1e8/PPIC.cfg` and transport config `rascas_run/tau_1e07/n1e8/Cont.cfg`; the existing n1e5/n1e6 files and smoke result are not reused or overwritten.
- Added serial photon generator `job_scripts/generate_n1e8_photons.pbs` and 8-node transport wrapper `job_scripts/run_tau1e07_n1e8_8nodes.pbs` requesting exactly 8 nodes × 32 ranks = 256 MPI ranks for 72 hours.
- The transport wrapper refuses an existing result and exits unless PBS supplies exactly 256 slots on eight distinct nodes.
- Replaced the photon validator with a streaming Fortran-record reader that supports compiler-chained logical records larger than 2 GiB; it checks the exact count, sequential unique IDs, finite monochromatic frequency, central position, zero source velocity, finite unit directions, and seed-array count before the generator dependency may succeed.
- Regression-tested the streaming validator against the existing 100,000- and 1,000,000-packet binaries; both passed. Shell syntax, Python byte compilation, target absence, config paths, count, and seed also passed.
- At this checkpoint `943187.leap` remains RUNNING; neither `photons/n1e8/Cont.IC` nor `rascas_run/tau_1e07/n1e8/Cont.res` exists.
- Status: READY TO SUBMIT

## 2026-08-13 01:12 IST — 100-million-photon jobs queued

- Submitted the 100,000,000-packet generator as LEAP job `943188.leap` (serial, 1 CPU, 32 GB, 6 hours); it is RUNNING on `compute-4-11`.
- Direct submission of the 8-node/256-rank transport, including a user-held attempt, was rejected by LEAP before job creation with `would exceed per-user limit on resource ncpus in complex`, because τ₀=10⁷ smoke job `943187.leap` is currently consuming 160 ranks. No transport output was created.
- To retain the requested eight-node allocation without violating the site limit, submitted scheduler-launch job `943191.leap` (serial, 1 CPU, 10 minutes) with `afterok:943187.leap:943188.leap`.
- Job `943191.leap` is dependency-held. Once both the τ₀=10⁷ smoke and validated n1e8 photon generator finish successfully, it will submit `job_scripts/run_tau1e07_n1e8_8nodes.pbs`, which requests exactly 8 nodes × 32 ranks = 256 ranks and records the resulting transport ID in `logs/tau_1e07_n1e8_transport_job_id.txt`.
- Logs: `logs/photons_n1e8_943188.leap.log`, `logs/pbs_photons_n1e8.out`, `logs/submit_tau_1e07_n1e8_943191.leap.log`, `logs/pbs_submit_tau_1e07_n1e8.out`; eventual transport logs are `logs/rascas_tau_1e07_n1e8_<jobid>.log` and `logs/pbs_rascas_tau_1e07_n1e8.out`.
- Status: GENERATOR RUNNING; EIGHT-NODE TRANSPORT SUBMISSION QUEUED BY DEPENDENCY

## 2026-08-13 01:15 IST — 100-million-photon binary complete

- Photon generator `943188.leap` exited 0 after 65 seconds and wrote `photons/n1e8/Cont.IC` (8.2 GiB displayed by `ls`).
- Streaming validation passed: exactly 100,000,000 packets, sequential unique IDs, 100,000,000 packet seeds, central positions, zero source velocities, finite line-centre frequency `2.466067748648893e15 Hz`, and unit direction norms within floating-point roundoff.
- Dependency launcher `943191.leap` now waits only for running τ₀=10⁷ smoke job `943187.leap`; after that succeeds it will submit the requested 8-node/256-rank transport.
- Status: PHOTONS PASSED; TRANSPORT SUBMISSION QUEUED

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
