# How the RASCAS Spectrum Is Compared with the Analytical Static Sphere

## 1. Physical experiment being compared

The numerical and analytical problems use the same physical model:

- a homogeneous, static sphere of neutral primordial hydrogen;
- centre `(0.5, 0.5, 0.5)` and radius `R = 0.3` box units;
- physical box length `1 kpc`, hence `R = 0.3 kpc`;
- gas temperature `T = 100 K`;
- zero bulk velocity, turbulence, metallicity, dust, recoil, and cosmological expansion;
- monochromatic Lyα photons emitted at line centre by a point source at the sphere centre;
- isotropic H I scattering.

The Cartesian cube is homogeneous. The sphere is imposed by the RASCAS computational boundary, so photons escape through a spherical surface rather than through Cartesian box faces.

The optical depth is defined from the centre to the surface, not across the diameter:

$$
	au_0 = n_{\rm HI}\,\sigma_0(T)\,R.
$$

The domain-dump validation measured exactly the requested centre-to-surface optical depths for all three cases. Therefore the analytical comparison does not fit or tune density after transport.

## 2. Physical constants and line-centre quantities

`analysis/physics.py` reproduces the constants and definitions in the installed RASCAS source and atom file:

$$
v_{\rm th}=\sqrt{\frac{2k_{\rm B}T}{m_{\rm ion}}},
\qquad
\Delta\nu_D=\frac{v_{\rm th}}{\lambda_\alpha},
$$

where RASCAS uses `m_ion = 1.008 amu`. The Voigt damping parameter is

$$
a_v=\frac{A_{21}}{4\pi\Delta\nu_D}.
$$

At 100 K the values used in both the grid construction and spectrum comparison are

- `v_th = 1.284404517466905 km/s`;
- `Delta_nu_D = 1.056540440635127e10 Hz`;
- `a_v = 4.7187295446605125e-3`;
- `sigma_0 = 5.864298336730396e-13 cm^2`.

The line-centre cross-section includes the installed COLT approximation to the Voigt function at `x=0`; it is not taken from a rounded textbook constant.

## 3. Analytical static-sphere spectrum

For a homogeneous static sphere, the angle-averaged solution used here is

$$
J(x)=
\sqrt{\frac{\pi}{6}}
\frac{1}{4a_v\tau_0}
\frac{x^2}{
1+\cosh\!\left[
\sqrt{\frac{2\pi^3}{27}}
\frac{|x|^3}{a_v\tau_0}
\right]}.
$$

This convention satisfies

$$
\int_{-\infty}^{+\infty}J(x)\,dx=\frac{1}{4\pi}.
$$

The Monte Carlo histogram is a unit-area probability density, so it must be compared with

$$
p_{\rm analytic}(x)=4\pi J(x),
\qquad
\int p_{\rm analytic}(x)\,dx=1.
$$

The expected peak magnitude is used only as a diagnostic:

$$
|x_{\rm peak}|\simeq0.931(a_v\tau_0)^{1/3}.
$$

The complete analytical curve—not merely its peak—is evaluated at every histogram-bin centre. Large `cosh` arguments are safely clipped to avoid floating-point overflow. The sampled analytical curve is then divided by its numerical integral over the plotted range, removing only negligible finite-grid quadrature error and not fitting it to RASCAS.

## 4. Meaning and sign of the dimensionless frequency x

RASCAS stores escaped external-frame frequency `nu_ext` in Hz. Each escaped photon is converted using

$$
x=\frac{\nu-\nu_\alpha}{\Delta\nu_D},
\qquad
\nu_\alpha=\frac{c}{\lambda_\alpha}.
$$

Consequently:

- `x < 0` is the red side because red photons have lower frequency;
- `x > 0` is the blue side;
- `x = 0` is line centre.

No wavelength-sign convention is mixed into the calculation. If wavelength were used instead, its displacement would have the opposite sign to frequency displacement near line centre.

## 5. Reading the Fortran binary files

RASCAS writes sequential unformatted Fortran records. Each record consists of a leading byte count, its payload, and the same trailing byte count. `scipy.io.FortranFile` checks and removes these record markers.

### Photon initial-condition file (`Cont.IC`)

`analysis/validate_photons.py` reads records in the exact order used by `module_photon.f90`:

1. number of Monte Carlo packets: one 32-bit integer;
2. represented real-photon rate: one float64;
3. global random seed: one 32-bit integer;
4. packet IDs: `nPhoton` integers;
5. emitted frequencies: `nPhoton` float64 values;
6. emission positions: `3*nPhoton` float64 values;
7. propagation directions: `3*nPhoton` float64 values;
8. per-packet random seeds: `nPhoton` integers;
9. source velocities: `3*nPhoton` float64 values.

The position, direction, and velocity streams are reshaped to `(nPhoton,3)`. Validation confirmed that all source positions are exactly the centre, all source velocities are zero, every direction has unit norm to floating precision, and all emitted frequencies are the same Lyα line-centre frequency.

### Escaped result file (`Cont.res`)

`analysis/compare_spectrum.py` reads:

1. packet count;
2. packet IDs;
3. status flags;
4. last positions `(x,y,z)`;
5. external-frame frequencies `nu_ext`;
6. final directions `(kx,ky,kz)`;
7. scattering counts;
8. propagation times.

Only packets with `status == 1` are treated as successfully escaped. The analysis also records every status count, so lost, unfinished, or invalid packets cannot silently disappear from the spectrum. In the completed `10^5` and `10^6` smoke runs, all 100,000 packets have status 1.

## 6. Constructing the Monte Carlo spectrum

The escaped `x` values are histogrammed over

$$
-100\le x\le100
$$

with bin width

$$
\Delta x=0.5.
$$

If bin `i` contains `N_i` escaped packets and the total escaped count is `N_esc`, then

$$
p_{\rm MC}(x_i)=\frac{N_i}{N_{\rm esc}\Delta x},
$$

and its Poisson uncertainty is

$$
\sigma_i=\frac{\sqrt{N_i}}{N_{\rm esc}\Delta x}.
$$

Thus

$$
\sum_i p_{\rm MC}(x_i)\Delta x=1.
$$

The CSV output preserves bin centres, raw counts, normalized density, Poisson error, analytical density, absolute residual, and fractional residual.

## 7. Plots and what each one tests

For every completed run, `analysis/compare_spectrum.py` writes both PNG and PDF versions of:

1. `spectrum_linear`: direct unit-area RASCAS/analytical overlay; tests peaks and overall shape.
2. `spectrum_log`: logarithmic density; exposes discrepancies in the wings.
3. `folded_halves`: folds the negative-frequency/red half onto `|x|` and compares it with the blue half; tests symmetry without assuming it.
4. `residual`: `p_MC-p_analytic`; shows absolute shape errors.
5. `fractional_residual`: `(p_MC-p_analytic)/p_analytic` where the analytical curve exceeds `10^-4` of its peak; avoids meaningless division in vanishing wings.
6. `counts_poisson`: unnormalized packet counts with `sqrt(N)` error bars; shows the actual Monte Carlo information content.

The machine-readable `spectrum_metrics.json` and `spectrum.csv` sit beside these figures.

## 8. Quantitative comparison

The principal statistics are:

- red and blue peak positions;
- peak separation;
- red/blue integrated packet-count ratio;
- symmetry fraction `|N_red-N_blue|/(N_red+N_blue)`;
- probability near line centre, `P(|x|<1)`;
- normalized L1 distance
  
  $$
  L_1=\sum_i|p_{{\rm MC},i}-p_{{\rm analytic},i}|\Delta x;
  $$

- RMS density difference;
- a chi-square-like statistic using Poisson errors where the analytical curve is appreciable.

The chi-square-like value is diagnostic rather than a formal goodness-of-fit probability because histogram bins are subject to normalization and finite-bin effects, and the analytical diffusion solution is itself approximate.

## 9. Physical understanding of the line shape

A line-centre photon in a high-column neutral sphere has an extremely short mean free path. It scatters repeatedly and performs a random walk in both position and frequency. Near `x=0`, the H I cross-section is largest, so spatial escape is inefficient. Thermal atomic motions gradually shift photons into either frequency wing, where the cross-section and optical depth are smaller. Once a photon reaches a sufficiently large `|x|`, it can make a long spatial excursion and escape.

This produces the characteristic result:

- suppression at line centre;
- two symmetric peaks in a static medium;
- increasing peak separation as `(a_v tau0)^(1/3)`;
- equal red and blue integrated flux in the absence of bulk motion, recoil, dust, or asymmetric geometry.

The finite `64^3` grid resolves the radius with 19.2 cells. Core skipping accelerates unimportant central scatterings but is documented as an approximation. Monte Carlo noise scales approximately as `N^(-1/2)`, which is why the 100,000-packet runs are smoke tests and the planned 1,000,000-packet runs are the final comparisons.

## 10. Completed results so far

### τ₀ = 10⁵, 100,000 photons

- analytical peak: `|x| = 7.2481`;
- RASCAS peaks: `x = -7.25` and `+6.75`;
- red/blue ratio: `1.00977`;
- symmetry fraction: `0.00486`;
- `P(|x|<1) = 7.2e-4`;
- `L1 = 0.11329`.

This passes as a diagnostic case. Its `a_v tau0 = 471.87` is below the conservative diffusion-limit criterion of roughly 1000, so it is not the strongest analytical test.

### τ₀ = 10⁶, 100,000 photons

- analytical peak: `|x| = 15.6156`;
- RASCAS peaks: `x = -15.25` and `+15.25`;
- red/blue ratio: `1.00337`;
- symmetry fraction: `0.00168`;
- `P(|x|<1) = 5e-5`;
- `L1 = 0.06492`;
- all 100,000 photons escaped successfully.

This is a strong PASS: it is highly symmetric, its two peak magnitudes differ from the analytical prediction by only about 2.3%, line centre is strongly suppressed, and its full-curve L1 error is well below the 0.15 PASS threshold.

## 11. Relevant files

- Physics: `analysis/physics.py`
- Binary IC validation: `analysis/validate_photons.py`
- Result decoding and comparison: `analysis/compare_spectrum.py`
- τ₀=10⁵ figures/metrics: `analysis/tau_1e05/smoke/`
- τ₀=10⁶ figures/metrics: `analysis/tau_1e06/smoke/`
- Domain verification: `analysis/<case>/domain/validation.json`

