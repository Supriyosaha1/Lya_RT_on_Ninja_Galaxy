#!/usr/bin/env python3
"""Validate RASCAS point-source photon IC records, including records >2 GiB."""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
COUNTS = {
    "n1e5": 100_000,
    "n1e6": 1_000_000,
    "n1e7": 10_000_000,
    "n1e8": 100_000_000,
}
BLOCK_BYTES = 64 * 1024 * 1024


class FortranRecords:
    """Read gfortran/ifort 4-byte record markers and chained >2-GiB subrecords."""

    def __init__(self, path: Path):
        self.file = path.open("rb")

    def chunks(self):
        while True:
            raw = self.file.read(4)
            if len(raw) != 4:
                raise EOFError("missing Fortran leading record marker")
            leading = struct.unpack("=i", raw)[0]
            remaining = abs(leading)
            while remaining:
                data = self.file.read(min(remaining, BLOCK_BYTES))
                if not data:
                    raise EOFError("truncated Fortran record payload")
                remaining -= len(data)
                yield data
            trailing_raw = self.file.read(4)
            if len(trailing_raw) != 4:
                raise EOFError("missing Fortran trailing record marker")
            trailing = struct.unpack("=i", trailing_raw)[0]
            if abs(trailing) != abs(leading):
                raise ValueError("inconsistent Fortran record markers")
            if leading >= 0:
                break

    def small_record(self) -> bytes:
        return b"".join(self.chunks())

    def close_and_check_eof(self):
        if self.file.read(1):
            raise ValueError("unexpected data after final photon record")
        self.file.close()


def arrays(chunks, dtype):
    """Yield aligned NumPy views even when a scalar spans an I/O chunk."""
    size = np.dtype(dtype).itemsize
    carry = b""
    for chunk in chunks:
        data = carry + chunk
        usable = len(data) - len(data) % size
        if usable:
            yield np.frombuffer(data[:usable], dtype=dtype)
        carry = data[usable:]
    if carry:
        raise ValueError("record byte count is not aligned to its dtype")


def validate_scalar_stream(reader, dtype, expected_count, predicate, stats=None):
    count = 0
    for values in arrays(reader.chunks(), dtype):
        if not predicate(values, count):
            raise ValueError("photon record invariant failed")
        if stats is not None:
            stats(values)
        count += values.size
    if count != expected_count:
        raise ValueError(f"expected {expected_count} values, found {count}")


def validate_vector_stream(reader, expected_count, predicate, stats=None):
    count = 0
    carry = np.empty(0, dtype=np.float64)
    for values in arrays(reader.chunks(), np.float64):
        if carry.size:
            values = np.concatenate((carry, values))
        usable = values.size - values.size % 3
        vectors = values[:usable].reshape(-1, 3)
        carry = values[usable:].copy()
        if vectors.size and not predicate(vectors):
            raise ValueError("photon vector-record invariant failed")
        if vectors.size and stats is not None:
            stats(vectors)
        count += vectors.shape[0]
    if carry.size or count != expected_count:
        raise ValueError(f"expected {expected_count} vectors, found {count}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("label", choices=tuple(COUNTS))
    args = parser.parse_args()
    expected = COUNTS[args.label]
    path = ROOT / "photons" / args.label / "Cont.IC"
    reader = FortranRecords(path)

    n = int(np.frombuffer(reader.small_record(), dtype=np.int32)[0])
    real_photon_rate = float(np.frombuffer(reader.small_record(), dtype=np.float64)[0])
    seed = int(np.frombuffer(reader.small_record(), dtype=np.int32)[0])
    if n != expected:
        raise ValueError(f"requested {expected} packets but file declares {n}")

    validate_scalar_stream(
        reader, np.int32, n,
        lambda values, offset: np.array_equal(
            values, np.arange(offset + 1, offset + 1 + values.size, dtype=np.int32)
        ),
    )
    frequency_min = np.inf
    frequency_max = -np.inf

    def frequency_stats(values):
        nonlocal frequency_min, frequency_max
        frequency_min = min(frequency_min, float(values.min()))
        frequency_max = max(frequency_max, float(values.max()))

    validate_scalar_stream(
        reader, np.float64, n,
        lambda values, offset: bool(np.isfinite(values).all()), frequency_stats,
    )
    if frequency_min != frequency_max:
        raise ValueError("photon frequencies are not monochromatic")

    validate_vector_stream(reader, n, lambda values: bool(np.all(values == 0.5)))
    norm_min = np.inf
    norm_max = -np.inf

    def direction_stats(values):
        nonlocal norm_min, norm_max
        norms = np.sqrt(np.einsum("ij,ij->i", values, values))
        norm_min = min(norm_min, float(norms.min()))
        norm_max = max(norm_max, float(norms.max()))

    validate_vector_stream(
        reader, n,
        lambda values: bool(np.isfinite(values).all()), direction_stats,
    )
    if not (np.isclose(norm_min, 1.0, atol=1e-12) and np.isclose(norm_max, 1.0, atol=1e-12)):
        raise ValueError("photon directions are not unit vectors")

    validate_scalar_stream(reader, np.int32, n, lambda values, offset: True)
    validate_vector_stream(reader, n, lambda values: bool(np.all(values == 0.0)))
    reader.close_and_check_eof()

    checks = {
        "direction_norm_max": norm_max,
        "direction_norm_min": norm_min,
        "finite_frequency": True,
        "frequency_max": frequency_max,
        "frequency_min": frequency_min,
        "ids_sequential_and_unique": True,
        "n_file": n,
        "n_requested": expected,
        "packet_seed_count": n,
        "positions_central": True,
        "real_photon_rate": real_photon_rate,
        "seed": seed,
        "status": "PASSED",
        "velocities_zero": True,
    }
    output = path.parent / "validation.json"
    output.write_text(json.dumps(checks, indent=2, sort_keys=True) + "\n")
    print(json.dumps(checks, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
