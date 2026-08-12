#!/usr/bin/env python3
"""Generate and independently reload homogeneous Cartesian validation fields."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
from physics import DENSITY_FACTOR, GAMMA, TEMPERATURE, case_values  # noqa: E402

FIELDS = ("density", "velocity_x", "velocity_y", "velocity_z", "metallicity", "internal_energy", "scalar_01", "pressure")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tau0", type=float, required=True, choices=(1e5, 1e6, 1e7))
    parser.add_argument("--resolution", type=int, default=64)
    parser.add_argument("--temperature", type=float, default=TEMPERATURE)
    parser.add_argument("--radius", type=float, default=0.3)
    parser.add_argument("--output-root", type=Path, default=ROOT / "cartesian_input")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.resolution != 64:
        raise SystemExit("Primary validation requires resolution=64")
    label = f"tau_{args.tau0:.0e}".replace("+", "")
    out = args.output_root.resolve() / label
    if out.exists():
        raise SystemExit(f"Refusing to overwrite existing directory: {out}")
    out.mkdir(parents=True)

    vals = case_values(args.tau0, args.temperature, args.radius)
    shape = (args.resolution,) * 3
    arrays = {
        "density": np.full(shape, vals["density_cartesian"], dtype=np.float64, order="C"),
        "velocity_x": np.zeros(shape, dtype=np.float64),
        "velocity_y": np.zeros(shape, dtype=np.float64),
        "velocity_z": np.zeros(shape, dtype=np.float64),
        "metallicity": np.zeros(shape, dtype=np.float64),
        "internal_energy": np.full(shape, vals["internal_energy"], dtype=np.float64, order="C"),
        "scalar_01": np.zeros(shape, dtype=np.float64),
        "pressure": np.full(shape, vals["pressure_cartesian_diagnostic"], dtype=np.float64, order="C"),
    }
    for name, array in arrays.items():
        np.save(out / f"{name}.npy", array, allow_pickle=False)

    summary = {
        "case": label,
        "shape": list(shape),
        "dtype": "float64",
        "axis_order": "array[x,y,z] sampled by converter as field[ix,iy,iz]",
        "c_contiguous": True,
        "full_cube_homogeneous": True,
        "converter_density_factor": DENSITY_FACTOR,
        "gamma": GAMMA,
        "pressure_npy_used_by_converter": False,
        "physics": vals,
        "fields": {},
    }
    for name in FIELDS:
        disk = np.load(out / f"{name}.npy", mmap_mode="r", allow_pickle=False)
        expected = arrays[name].flat[0]
        checks = {
            "shape_ok": disk.shape == shape,
            "dtype_ok": disk.dtype == np.dtype("float64"),
            "c_contiguous": bool(disk.flags.c_contiguous),
            "finite": bool(np.isfinite(disk).all()),
            "homogeneous": bool(np.all(disk == expected)),
            "min": float(disk.min()), "max": float(disk.max()), "mean": float(disk.mean()),
        }
        if not all(checks[k] for k in ("shape_ok", "dtype_ok", "c_contiguous", "finite", "homogeneous")):
            raise RuntimeError(f"Disk validation failed for {name}: {checks}")
        summary["fields"][name] = checks
        print(name, disk.shape, disk.dtype, checks["min"], checks["max"], checks["mean"])

    if summary["fields"]["density"]["min"] <= 0 or summary["fields"]["internal_energy"]["min"] <= 0:
        raise RuntimeError("Density and internal energy must be positive")
    for zero in ("velocity_x", "velocity_y", "velocity_z", "metallicity", "scalar_01"):
        if summary["fields"][zero]["min"] != 0.0 or summary["fields"][zero]["max"] != 0.0:
            raise RuntimeError(f"{zero} is not exactly zero")

    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    fig, axes = plt.subplots(2, 4, figsize=(14, 7), constrained_layout=True)
    for ax, name in zip(axes.flat, FIELDS):
        image = arrays[name][:, :, args.resolution // 2]
        shown = ax.imshow(image.T, origin="lower", interpolation="nearest")
        ax.set_title(name)
        fig.colorbar(shown, ax=ax, shrink=0.8)
    fig.suptitle(f"Homogeneous Cartesian fields: {label}")
    fig.savefig(out / "central_slices.png", dpi=180)
    fig.savefig(out / "central_slices.pdf")
    plt.close(fig)
    print(json.dumps(vals, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
