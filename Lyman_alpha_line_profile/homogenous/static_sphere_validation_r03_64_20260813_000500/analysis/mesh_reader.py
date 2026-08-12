#!/usr/bin/env python3
"""Read current-format RASCAS sphere mesh dumps."""
from __future__ import annotations
import struct
from pathlib import Path
import numpy as np


def record(f):
    raw = f.read(4)
    if not raw: raise EOFError
    n = struct.unpack("<i", raw)[0]; payload = f.read(n); end = struct.unpack("<i", f.read(4))[0]
    if n != end: raise ValueError("Fortran record marker mismatch")
    return payload


def arr(payload, dtype): return np.frombuffer(payload, dtype=dtype).copy()


def read_mesh(path: Path) -> dict:
    with path.open("rb") as f:
        domain_type = record(f).decode("ascii").strip()
        center = arr(record(f), "<f8"); radius = float(arr(record(f), "<f8")[0])
        ncoarse, noct, ncell, nleaf = arr(record(f), "<i4")
        father = arr(record(f), "<i4"); son = arr(record(f), "<i4")
        nbor = arr(record(f), "<i4").reshape(6, noct).T
        octlevel = arr(record(f), "<i4"); xoct = arr(record(f), "<f8").reshape(3, noct).T
        velocity = arr(record(f), "<f8").reshape(nleaf, 3)
        nhi = arr(record(f), "<f8"); thermal = arr(record(f), "<f8")
        vturb = arr(record(f), "<f8"); ndust = arr(record(f), "<f8")
        box_size_cm = float(arr(record(f), "<f8")[0])
    offsets = np.array([[-.5,-.5,-.5],[.5,-.5,-.5],[-.5,.5,-.5],[.5,.5,-.5],[-.5,-.5,.5],[.5,-.5,.5],[-.5,.5,.5],[.5,.5,.5]])
    cells = np.where(son < 0)[0]; child = (cells - ncoarse) // noct; ioct = (cells - ncoarse) % noct
    levels = octlevel[ioct]; widths = 0.5**levels; positions = xoct[ioct] + offsets[child] * widths[:, None]
    gas_index = -son[cells] - 1
    return locals()

