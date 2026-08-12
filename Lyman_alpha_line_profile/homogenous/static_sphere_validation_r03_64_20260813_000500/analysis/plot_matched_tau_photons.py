#!/usr/bin/env python3
"""Overlay the three existing 100,000-photon optical-depth spectra."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import FortranFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
from physics import C, LAMBDA_CM, PI, case_values  # noqa: E402

CASES = (
    ("tau_1e05", "smoke", 1.0e5, 100_000, "#1f77b4"),
    ("tau_1e06", "smoke", 1.0e6, 100_000, "#ff7f0e"),
    ("tau_1e07", "smoke", 1.0e7, 100_000, "#2ca02c"),
)


def analytic(x, a_voigt, tau0):
    argument = np.sqrt(2.0 * PI**3 / 27.0) * np.abs(x) ** 3 / (a_voigt * tau0)
    denominator = 1.0 + np.cosh(np.clip(argument, 0.0, 700.0))
    profile = np.sqrt(PI / 6.0) / (4.0 * a_voigt * tau0) * x * x / denominator
    profile[argument > 700.0] = 0.0
    return 4.0 * PI * profile


def escaped_frequencies(path):
    file = FortranFile(path, "r")
    n = int(file.read_ints(np.int32)[0])
    file.read_ints(np.int32)
    status = file.read_ints(np.int32)
    file.read_reals(np.float64)
    frequency = file.read_reals(np.float64)
    file.read_reals(np.float64)
    file.read_ints(np.int32)
    file.read_reals(np.float64)
    file.close()
    return n, status, frequency[status == 1]


def main():
    out = ROOT / "analysis" / "existing_tau_overlay"
    out.mkdir(parents=True, exist_ok=True)
    edges = np.arange(-100.0, 100.0001, 0.5)
    centers = 0.5 * (edges[:-1] + edges[1:])
    dx = float(edges[1] - edges[0])
    rows = []
    metrics = {"bin_width_x": dx, "input_x": 0.0, "photons_per_case": 100_000, "cases": {}}

    fig, axis = plt.subplots(figsize=(10.0, 6.2))
    for case, label, tau0, expected, color in CASES:
        result = ROOT / "rascas_run" / case / label / "Cont.res"
        if not result.exists():
            raise FileNotFoundError(f"Required matched result is missing: {result}")
        n, status, frequency = escaped_frequencies(result)
        if n != expected or frequency.size != expected or not np.all(status == 1):
            raise RuntimeError(f"{case}/{label}: packet count or terminal status failed")
        values = case_values(tau0)
        x = (frequency - C / LAMBDA_CM) / values["delta_nu_d_hz"]
        counts, _ = np.histogram(x, bins=edges)
        pdf = counts / (frequency.size * dx)
        model = analytic(centers, values["a_voigt"], tau0)
        model /= np.sum(model) * dx
        axis.step(
            centers, pdf, where="mid", color=color, linewidth=1.3,
            label=rf"RASCAS: $\tau_0=10^{{{int(np.log10(tau0))}}}$",
        )
        axis.plot(
            centers, model, color=color, linestyle="--", linewidth=1.5,
            label=rf"analytical: $\tau_0=10^{{{int(np.log10(tau0))}}}$",
        )
        metrics["cases"][case] = {
            "photon_label": label,
            "n_total": n,
            "n_escaped": int(frequency.size),
            "normalization": float(np.sum(pdf) * dx),
            "l1_difference": float(np.sum(np.abs(pdf - model)) * dx),
            "analytic_peak_abs_x_approx": values["x_peak_approx"],
        }
        for i in range(centers.size):
            rows.append((case, label, tau0, expected, centers[i], counts[i], pdf[i], model[i]))

    axis.axvline(0.0, color="crimson", linestyle=":", linewidth=1.8,
                 label=r"input: monochromatic $x=0$")
    axis.set_xlim(-85.0, 85.0)
    axis.set_ylim(bottom=0.0)
    axis.set_xlabel(r"Doppler frequency $x=(\nu-\nu_\alpha)/\Delta\nu_D$")
    axis.set_ylabel(r"Unit-area probability density $p(x)$")
    axis.set_title(r"Existing static-sphere spectra: $N_\gamma=10^5$ per optical depth")
    axis.grid(alpha=0.18)
    axis.legend(frameon=False, ncol=2, fontsize=9)
    fig.tight_layout()
    fig.savefig(out / "three_tau_existing_linear.png", dpi=240)
    fig.savefig(out / "three_tau_existing_linear.pdf")
    plt.close(fig)

    with (out / "three_tau_existing.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("case", "photon_label", "tau0", "requested_photons", "x", "count", "pdf", "analytic_pdf"))
        writer.writerows(rows)
    (out / "three_tau_existing_metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
