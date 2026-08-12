# τ₀ = 10⁵ verification with 10⁶ photons

This comparison uses all 1,000,000 successfully escaped photon packets in the
RASCAS Fortran binary `Cont.res`; there is no viewing-direction cut. Frequencies
are converted to Doppler units using

\[
x=(\nu-\nu_\alpha)/\Delta\nu_D,
\]

and binned with \(\Delta x=0.5\). Both the Monte Carlo histogram and analytical
static-sphere solution are normalized to unit area before comparison.

## Results

- Escaped packets: 1,000,000 / 1,000,000; every status is 1.
- RASCAS peaks: \(x=-7.25\) and \(+7.25\).
- Analytical peak: \(|x|=7.2481\).
- Red/blue photon ratio: 0.999356.
- Red/blue asymmetry fraction: 0.000322.
- Normalized \(L_1\) difference: 0.112430.
- Monte Carlo and analytical normalizations: 1.0.

The peak locations and red/blue symmetry agree extremely well. The remaining
profile-shape difference is systematic rather than photon-count noise. This is
expected because \(a\tau_0\simeq472\) is below the strongest asymptotic diffusion
regime of the analytical expression, and the transport uses documented core
skipping. Therefore this is a successful lower-optical-depth diagnostic, while
the higher-\(a\tau_0\) cases remain the stronger analytical tests.

Primary plots are `spectrum_linear.png` and `spectrum_log.png`; residual, folded,
Poisson-count, CSV, and JSON diagnostics are stored in this directory.
