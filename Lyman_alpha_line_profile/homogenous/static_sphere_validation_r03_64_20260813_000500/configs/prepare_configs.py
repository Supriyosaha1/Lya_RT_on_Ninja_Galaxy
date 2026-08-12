#!/usr/bin/env python3
"""Create validation-owned converter, domain, photon, and transport configs."""
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = Path("/user1/supriyo/Lya_RT_on_Ninja_Galaxy")
CONVERTER = Path("/user1/supriyo/Gadget_to_Ramses_Converter")
SOURCE_CONFIG = CONVERTER / "converter/amr_header_config.json"
CASES = ("tau_1e05", "tau_1e06", "tau_1e07")

CDD = """[CreateDomDump]
  repository = {repository}
  snapnum = 1
  DomDumpDir = ./
  idealised_models = F
  comput_dom_type = sphere
  comput_dom_pos = 0.5 0.5 0.5
  comput_dom_rsp = 0.3
  decomp_dom_type = sphere
  decomp_dom_ndomain = 1
  decomp_dom_xc = 0.5
  decomp_dom_yc = 0.5
  decomp_dom_zc = 0.5
  decomp_dom_rsp = 0.3
  reading_method = hilbert

[gas_composition]
  atomic_data_dir = {atomic_dir}
  nscatterer = 1
  scatterer_names = HI-1216
  ignoreDust = T
  vturb_kms = 0.0

[ramses]
  self_shielding = T
  ramses_rt = T
  read_rt_variables = F
  verbose = T
  cosmo = F
  use_proper_time = T
  particle_families = T
  itemp = 5
  imetal = 6
  ihii = 8
  iheii = 0
  iheiii = 0
  deut2H_nb_ratio = 3.0e-05
  recompute_particle_initial_mass = F
"""

ATOM = """! Validation-owned parameter copy; RASCAS source is unchanged.
m_ion     = 1.008d0
name_ion  = HI
lambda_cm = 1215.67d-8
A         = 6.265d8
f         = 0.416d0
n_fluo    = 0
isotropic = T
recoil    = F
core_skip = T
xcritmax  = 3.0
lee_correction = F
"""

PPIC = """[PhotonsFromSourceModel]
  outputfile = {outputfile}
  source_type = pointlike
  source_pos = 0.5 0.5 0.5
  source_vel = 0.0 0.0 0.0
  spec_type = Mono
  spec_mono_l0_Ang = 1215.67
  nPhotonPackets = {nphot}
  ranseed = -20260813
  verbose = T
"""

CONT = """[gas_composition]
  atomic_data_dir = {atomic_dir}
  nscatterer = 1
  scatterer_names = HI-1216
  ignoreDust = T
  vturb_kms = 0.0

[ramses]
  self_shielding = T
  ramses_rt = T
  read_rt_variables = F
  verbose = T
  cosmo = F
  use_proper_time = T
  particle_families = T
  itemp = 5
  imetal = 6
  ihii = 8
  iheii = 0
  iheiii = 0
  deut2H_nb_ratio = 3.0e-05
  recompute_particle_initial_mass = F

[mock]
  nDirections = 0

[rascas]
  verbose = T
  DomDumpDir = {domain_dir}
  PhotonICFile = {photon_file}
  fileout = {result_file}
  nbundle = 34
"""


def write_new(path: Path, text: str) -> None:
    if path.exists():
        raise SystemExit(f"Refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def main() -> None:
    source = json.loads(SOURCE_CONFIG.read_text())
    atomic_dir = ROOT / "configs/ion_parameters_core_skip"
    write_new(atomic_dir / "HI-1216.dat", ATOM)

    for case in CASES:
        cfg = copy.deepcopy(source)
        cfg["header"].update({
            "ncpu": 1, "ndim": 3, "nx": 1, "ny": 1, "nz": 1,
            "nlevelmax": 6, "ngridmax": 262144, "nboundary": 0,
            "boxlen": 1.0, "nvector": 32,
            "base_path": str(ROOT / "cartesian_input" / case),
            "output_path": str(ROOT / "ramses_output" / case),
        })
        cfg["info_block"].update({
            "levelmin": 6,
            "unit_l": 3.085677581282e21,
            "unit_m": 1.989e42,
            "unit_v": 1.0e5,
            "boxlen_info": 1.0,
        })
        cfg["hydro"].update({
            "gamma": 5.0 / 3.0, "h0": 0.6736, "aexp": 0.125,
            "velocity_factor": 1.0, "internal_energy_factor": 1.0,
            "field_files": {
                "density": "density.npy", "velocity_x": "velocity_x.npy",
                "velocity_y": "velocity_y.npy", "velocity_z": "velocity_z.npy",
                "metallicity": "metallicity.npy", "internal_energy": "internal_energy.npy",
                "XHII": "scalar_01.npy",
            },
        })
        write_new(ROOT / "conversion" / case / "converter_config.json", json.dumps(cfg, indent=2) + "\n")
        repository = ROOT / "ramses_output" / case
        write_new(ROOT / "domain" / case / "CDD.cfg", CDD.format(repository=repository, atomic_dir=atomic_dir))

    for nphot, label in ((100000, "n1e5"), (1000000, "n1e6")):
        pdir = ROOT / "photons" / label
        write_new(pdir / "PPIC.cfg", PPIC.format(outputfile=pdir / "Cont.IC", nphot=nphot))

    for case in CASES:
        stages = ("smoke",) if case == "tau_1e05" else ("smoke", "final")
        for stage in stages:
            photon = ROOT / "photons" / ("n1e5" if stage == "smoke" else "n1e6") / "Cont.IC"
            run = ROOT / "rascas_run" / case / stage
            write_new(run / "Cont.cfg", CONT.format(
                atomic_dir=atomic_dir,
                domain_dir=ROOT / "domain" / case,
                photon_file=photon,
                result_file=run / "Cont.res",
            ))

    convergence = copy.deepcopy(source)
    convergence["header"].update({"nlevelmax": 7, "ngridmax": 2097152, "boxlen": 1.0})
    convergence["info_block"]["levelmin"] = 7
    write_new(ROOT / "configs/optional_128_config_template.json", json.dumps(convergence, indent=2) + "\n")
    print(f"Prepared configs under {ROOT}")


if __name__ == "__main__":
    main()

