#!/usr/bin/env python3
"""Validate generated RASCAS point-source photon IC records."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
from scipy.io import FortranFile
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(); p.add_argument("label",choices=("n1e5","n1e6")); a=p.parse_args(); expected={"n1e5":100000,"n1e6":1000000}[a.label]
 path=ROOT/"photons"/a.label/"Cont.IC"; f=FortranFile(path,"r"); n=int(f.read_ints(np.int32)[0]); real=float(f.read_reals(np.float64)[0]); seed=int(f.read_ints(np.int32)[0]); ids=f.read_ints(np.int32); nu=f.read_reals(np.float64); pos=f.read_reals(np.float64).reshape(n,3); direction=f.read_reals(np.float64).reshape(n,3); seeds=f.read_ints(np.int32); vel=f.read_reals(np.float64).reshape(n,3); f.close()
 checks={"n_requested":expected,"n_file":n,"real_photon_rate":real,"seed":seed,"ids_unique":len(np.unique(ids))==n,"finite_frequency":bool(np.isfinite(nu).all()),"frequency_min":float(nu.min()),"frequency_max":float(nu.max()),"position_min":pos.min(axis=0).tolist(),"position_max":pos.max(axis=0).tolist(),"velocity_min":vel.min(axis=0).tolist(),"velocity_max":vel.max(axis=0).tolist(),"direction_norm_min":float(np.linalg.norm(direction,axis=1).min()),"direction_norm_max":float(np.linalg.norm(direction,axis=1).max()),"packet_seed_count":len(seeds)}
 if n!=expected or len(ids)!=n or not checks["ids_unique"] or not checks["finite_frequency"] or not np.all(pos==.5) or not np.all(vel==0) or not np.allclose(nu,nu[0],rtol=0,atol=0): raise RuntimeError(checks)
 checks["status"]="PASSED"; (path.parent/"validation.json").write_text(json.dumps(checks,indent=2,sort_keys=True)+"\n"); print(json.dumps(checks,indent=2,sort_keys=True))
if __name__=="__main__":main()
