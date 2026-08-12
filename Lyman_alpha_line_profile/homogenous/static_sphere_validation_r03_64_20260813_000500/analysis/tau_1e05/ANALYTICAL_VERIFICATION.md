# Analytical Verification — τ₀ = 10⁵

Parameters are taken from the installed RASCAS atom/Voigt definitions and the validated 100 K mesh:

- `a_v = 0.0047187295446605125`
- `a_v tau0 = 471.8729544660512`
- `sigma0 = 5.864298336730396e-13 cm²`
- measured centre-to-surface `tau0 = 100000.0`

The evaluated unit-area sphere solution is

\[
p(x)=4\pi\sqrt{\frac{\pi}{6}}\frac{x^2}{4a_v\tau_0\left[1+\cosh\left(\sqrt{\frac{2\pi^3}{27}}\frac{|x|^3}{a_v\tau_0}\right)\right]}.
\]

A dense numerical integration on `[-100,100]` gives normalization `1.0000000000000002`, peak position `|x|=7.2480`, and peak density `0.0889352`.

The 100,000-packet RASCAS smoke result has:

- normalization `1.0`;
- red peak `x=-7.25`;
- blue peak `x=+6.75` (6.9% below the analytical magnitude and one 0.5-wide histogram bin from `+7.25`);
- red/blue integrated-count ratio `1.00977`;
- symmetry fraction `0.00486`;
- line-centre probability for `|x|<1` of `0.00072`;
- normalized L1 difference `0.11329`.

Conclusion: **PASS for the requested diagnostic role**. The result is normalized, symmetric, double-peaked, centre-suppressed, and within the stated peak/L1 tolerances. Because `a_v tau0 = 471.9` is below the conservative diffusion threshold of roughly `10^3`, this case is not used as the strongest analytical validation; τ₀=10⁶ and 10⁷ remain decisive.

