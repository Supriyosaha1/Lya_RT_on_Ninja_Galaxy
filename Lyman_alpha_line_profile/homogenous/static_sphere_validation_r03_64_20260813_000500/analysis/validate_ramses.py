#!/usr/bin/env python3
"""Validate converted RAMSES-like output with yt and expected converter scalings."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
from physics import DENSITY_FACTOR, case_values  # noqa: E402


def stats(a) -> dict[str, float]:
    x = np.asarray(a, dtype=float)
    return {"min": float(x.min()), "max": float(x.max()), "mean": float(x.mean()), "size": int(x.size)}


def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("case", choices=("tau_1e05", "tau_1e06", "tau_1e07")); args = p.parse_args()
    tau0 = {"tau_1e05": 1e5, "tau_1e06": 1e6, "tau_1e07": 1e7}[args.case]
    expected = case_values(tau0)
    output = ROOT / "ramses_output" / args.case / "output_00001"
    info = (output / "info_00001.txt").read_text()
    required_text = ("ncpu        =          1", "ndim        =          3", "levelmin    =          6", "levelmax    =          6")
    if not all(item in info for item in required_text):
        raise RuntimeError("RAMSES info header does not have required ncpu/ndim/levels")
    descriptor = (output / "hydro_file_descriptor.txt").read_text()
    order = ["density", "velocity_x", "velocity_y", "velocity_z", "pressure", "metallicity", "internal_energy", "scalar_01"]
    if not all(f"{i:2d}, {name}, d" in descriptor for i, name in enumerate(order, 1)):
        raise RuntimeError("Hydro descriptor field order mismatch")

    ds = yt.load(str(output))
    ad = ds.all_data()
    candidates = {str(f): f for f in ds.field_list}
    def field_by_fragment(fragment: str):
        hits = [f for f in ds.field_list if fragment.lower() in str(f).lower()]
        if len(hits) != 1:
            raise RuntimeError(f"Expected one field containing {fragment!r}, got {hits}; fields={candidates}")
        return hits[0]
    fields = {
        "density": field_by_fragment("Density"),
        "velocity_x": field_by_fragment("x-velocity"),
        "velocity_y": field_by_fragment("y-velocity"),
        "velocity_z": field_by_fragment("z-velocity"),
        "pressure": field_by_fragment("Pressure"),
        "metallicity": field_by_fragment("Metallicity"),
        "internal_energy": field_by_fragment("internal_energy"),
        "scalar_01": field_by_fragment("scalar_01"),
    }
    arrays = {name: np.asarray(ad[f]) for name, f in fields.items()}
    nleaf = arrays["density"].size
    if nleaf != 64**3:
        raise RuntimeError(f"Expected 262144 leaves, got {nleaf}")
    checks = {
        "density": expected["density_ramses"], "pressure": expected["pressure_ramses"],
        "internal_energy": expected["internal_energy"], "velocity_x": 0.0, "velocity_y": 0.0,
        "velocity_z": 0.0, "metallicity": 0.0, "scalar_01": 0.0,
    }
    for name, target in checks.items():
        if not np.allclose(arrays[name], target, rtol=1e-12, atol=0.0 if target else 1e-15):
            raise RuntimeError(f"{name} mismatch: {stats(arrays[name])}, target={target}")
    temperature = arrays["pressure"] / arrays["density"] * expected["scale_T2_K"] * expected["mu_neutral"]
    if not np.allclose(temperature, 100.0, rtol=1e-12):
        raise RuntimeError(f"Temperature mismatch: {stats(temperature)}")

    summary = {
        "case": args.case, "tau0": tau0, "dataset": str(output), "nleaf": nleaf,
        "domain_dimensions": [int(x) for x in ds.domain_dimensions], "fields": {k: stats(v) for k, v in arrays.items()},
        "temperature_K": stats(temperature), "expected_density_factor": DENSITY_FACTOR,
        "yt_field_mapping": {k: str(v) for k, v in fields.items()}, "status": "PASSED",
    }
    out = ROOT / "analysis" / args.case / "ramses"
    out.mkdir(parents=True, exist_ok=True)
    (out / "validation.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    fig, axes = plt.subplots(2, 4, figsize=(14, 7), constrained_layout=True)
    for ax, (name, array) in zip(axes.flat, arrays.items()):
        # Uniform level-6 data are homogeneous, so reshape is valid for a diagnostic central slice.
        image = array.reshape(64, 64, 64)[:, :, 32]
        im = ax.imshow(image.T, origin="lower"); ax.set_title(name); fig.colorbar(im, ax=ax, shrink=0.8)
    fig.savefig(out / "central_slices.png", dpi=180); fig.savefig(out / "central_slices.pdf"); plt.close(fig)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__": main()
