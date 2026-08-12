#!/usr/bin/env python3
"""Shared physical constants and exact RASCAS-compatible Ly-alpha scalings."""
from __future__ import annotations

import math

PI = 3.1415926535898
SQRT_PI = 1.77245387556703
C = 2.99792458e10
KB = 1.380649e-16
MP = 1.67262192369e-24
ME = 9.1093837015e-28
AMU = 1.66053906660e-24
E_CH = 4.80320471e-10
XH = 0.76

LAMBDA_CM = 1215.67e-8
M_ION = 1.008
A21 = 6.265e8
FOSC = 0.416

UNIT_L = 3.085677581282e21
UNIT_D = 6.7699139342702e-23
UNIT_V = 1.0e5
UNIT_T = UNIT_L / UNIT_V
BOX_LEN = 1.0
RADIUS = 0.3
TEMPERATURE = 100.0
GAMMA = 5.0 / 3.0
H0_CONVERTER = 0.6736
AEXP_CONVERTER = 0.125
DENSITY_FACTOR = H0_CONVERTER**2 / AEXP_CONVERTER**3


def colt_h0(a: float) -> float:
    """COLT approximation H(a,0), matching module_voigt.f90."""
    a0, a1, a2 = 15.75328153963877, 286.9341762324778, 19.05706700907019
    a3, a4, a5, a6 = 28.22644017233441, 9.526399802414186, 35.29217026286130, 0.8681020834678775
    return 1.0 - a * (a0 + a1 / (-a2 + a3 / (-a4 + a5 / (-a6))))


def derived(temperature: float = TEMPERATURE, radius: float = RADIUS) -> dict[str, float]:
    vth = math.sqrt(2.0 * KB * temperature / (AMU * M_ION))
    delta_nu_d = vth / LAMBDA_CM
    a_voigt = A21 / (4.0 * PI * delta_nu_d)
    sigma_factor = SQRT_PI * E_CH**2 * FOSC / (ME * C)
    sigma0 = sigma_factor / delta_nu_d * colt_h0(a_voigt)
    mu_neutral = 1.0 / (XH + 0.25 * (1.0 - XH))
    scale_t2 = MP / KB * UNIT_V**2
    pressure_over_density = temperature / (mu_neutral * scale_t2)
    internal_energy = pressure_over_density / (GAMMA - 1.0)
    return {
        "vth_cm_s": vth,
        "delta_nu_d_hz": delta_nu_d,
        "a_voigt": a_voigt,
        "sigma0_cm2": sigma0,
        "mu_neutral": mu_neutral,
        "scale_T2_K": scale_t2,
        "pressure_over_density": pressure_over_density,
        "internal_energy": internal_energy,
        "radius_cm": radius * UNIT_L,
    }


def case_values(tau0: float, temperature: float = TEMPERATURE, radius: float = RADIUS) -> dict[str, float]:
    p = derived(temperature, radius)
    nhi = tau0 / (p["sigma0_cm2"] * p["radius_cm"])
    density_ramses = nhi * MP / (XH * UNIT_D)
    density_cartesian = density_ramses / DENSITY_FACTOR
    return {
        **p,
        "tau0": tau0,
        "nhi_cm3": nhi,
        "nhi_column_cm2": tau0 / p["sigma0_cm2"],
        "density_cartesian": density_cartesian,
        "density_ramses": density_ramses,
        "pressure_ramses": density_ramses * p["pressure_over_density"],
        "pressure_cartesian_diagnostic": density_cartesian * p["pressure_over_density"],
        "x_peak_approx": 0.931 * (p["a_voigt"] * tau0) ** (1.0 / 3.0),
    }

