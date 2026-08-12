#!/usr/bin/env python3
"""Overlay all-direction tau0=1e5 spectra at three photon counts."""
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

TAU0 = 1.0e5
LABELS = ("n1e5", "n1e6", "n1e7")
REQUESTED = {"n1e5": 100_000, "n1e6": 1_000_000, "n1e7": 10_000_000}
COLORS = {"n1e5": "#1f77b4", "n1e6": "#ff7f0e", "n1e7": "#2ca02c"}


def analytic(x, a_voigt, tau0):
    argument = np.sqrt(2.0 * PI**3 / 27.0) * np.abs(x) ** 3 / (a_voigt * tau0)
    denominator = 1.0 + np.cosh(np.clip(argument, 0.0, 700.0))
    profile = np.sqrt(PI / 6.0) / (4.0 * a_voigt * tau0) * x * x / denominator
    profile[argument > 700.0] = 0.0
    return 4.0 * PI * profile


def read_escaped_frequency(path):
    file = FortranFile(path, "r")
    n_total = int(file.read_ints(np.int32)[0])
    file.read_ints(np.int32)  # IDs
    status = file.read_ints(np.int32)
    file.read_reals(np.float64)  # final positions
    frequency = file.read_reals(np.float64)
    file.read_reals(np.float64)  # final directions
    scatterings = file.read_ints(np.int32)
    file.read_reals(np.float64)  # travel times
    file.close()
    escaped = status == 1
    return n_total, status, frequency[escaped], scatterings[escaped]


def main():
    values = case_values(TAU0)
    nu0 = C / LAMBDA_CM
    edges = np.arange(-30.0, 30.0001, 0.25)
    centers = 0.5 * (edges[:-1] + edges[1:])
    dx = float(edges[1] - edges[0])
    model = analytic(centers, values["a_voigt"], TAU0)
    model /= np.sum(model) * dx
    out = ROOT / "analysis" / "tau_1e05" / "photon_count_comparison"
    out.mkdir(parents=True, exist_ok=True)

    metrics = {
        "tau0": TAU0,
        "temperature_K": 100.0,
        "spectrum": "all successfully escaped directions; no angular selection",
        "bin_width_x": dx,
        "analytic_peak_abs_x_approx": values["x_peak_approx"],
        "runs": {},
    }
    rows = []
    fig, axis = plt.subplots(figsize=(8.2, 5.3))
    axis.plot(centers, model, color="black", linestyle="--", linewidth=2.0,
              label="Analytical static sphere")

    for label in LABELS:
        path = ROOT / "rascas_run" / "tau_1e05" / label / "Cont.res"
        n_total, status, frequency, scatterings = read_escaped_frequency(path)
        if n_total != REQUESTED[label]:
            raise RuntimeError(f"{label}: expected {REQUESTED[label]} packets, found {n_total}")
        if frequency.size != n_total or not np.all(status == 1):
            raise RuntimeError(f"{label}: not every packet escaped with status 1")
        x = (frequency - nu0) / values["delta_nu_d_hz"]
        counts, _ = np.histogram(x, bins=edges)
        pdf = counts / (frequency.size * dx)
        red = centers < 0.0
        blue = centers > 0.0
        red_peak = float(centers[red][np.argmax(pdf[red])])
        blue_peak = float(centers[blue][np.argmax(pdf[blue])])
        red_count = int(np.count_nonzero(x < 0.0))
        blue_count = int(np.count_nonzero(x > 0.0))
        run_metrics = {
            "requested_photons": REQUESTED[label],
            "total_photons": n_total,
            "escaped_photons": int(frequency.size),
            "status_counts": {
                str(int(key)): int(count)
                for key, count in zip(*np.unique(status, return_counts=True))
            },
            "normalization": float(np.sum(pdf) * dx),
            "l1_difference": float(np.sum(np.abs(pdf - model)) * dx),
            "red_peak_x": red_peak,
            "blue_peak_x": blue_peak,
            "red_blue_count_ratio": float(red_count / blue_count),
            "symmetry_fraction": float(abs(red_count - blue_count) / n_total),
            "mean_scatterings": float(scatterings.mean()),
            "x_min": float(x.min()),
            "x_max": float(x.max()),
        }
        metrics["runs"][label] = run_metrics
        axis.step(centers, pdf, where="mid", linewidth=1.1, alpha=0.9,
                  color=COLORS[label], label=f"RASCAS {REQUESTED[label]:,} photons")
        for index in range(centers.size):
            rows.append((label, REQUESTED[label], centers[index], counts[index], pdf[index], model[index]))

    axis.set_xlim(-22.0, 22.0)
    axis.set_xlabel(r"Doppler frequency $x=(\nu-\nu_\alpha)/\Delta\nu_D$")
    axis.set_ylabel("Unit-area probability density")
    axis.set_title(r"Static sphere: $\tau_0=10^5$, all escaped directions")
    axis.grid(alpha=0.2)
    axis.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out / "all_directions_overlay.png", dpi=240)
    fig.savefig(out / "all_directions_overlay.pdf")
    plt.close(fig)

    with (out / "spectra.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("run", "requested_photons", "x", "count", "pdf", "analytic_pdf"))
        writer.writerows(rows)
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
