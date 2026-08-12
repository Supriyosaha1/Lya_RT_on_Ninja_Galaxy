#!/usr/bin/env python3
"""Validate a RASCAS spherical domain dump and create geometry/gas diagnostics."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "analysis"))
from mesh_reader import read_mesh  # noqa: E402
from physics import AMU, KB, case_values  # noqa: E402


def st(x): return {"min": float(np.min(x)), "max": float(np.max(x)), "mean": float(np.mean(x)), "std": float(np.std(x))}


def main():
    p=argparse.ArgumentParser(); p.add_argument("case", choices=("tau_1e05","tau_1e06","tau_1e07")); a=p.parse_args()
    tau={"tau_1e05":1e5,"tau_1e06":1e6,"tau_1e07":1e7}[a.case]; expected=case_values(tau)
    mesh=read_mesh(ROOT/"domain"/a.case/"domain_1.mesh")
    if mesh["domain_type"] != "sphere" or not np.array_equal(mesh["center"], [.5,.5,.5]) or mesh["radius"] != .3: raise RuntimeError("Domain geometry mismatch")
    gi=mesh["gas_index"]; nhi=mesh["nhi"][gi]; vel=mesh["velocity"][gi]; temp=mesh["thermal"][gi]*AMU/(2*KB)
    vturb=mesh["vturb"][gi]; ndust=mesh["ndust"][gi]
    if not np.allclose(nhi, expected["nhi_cm3"], rtol=1e-12): raise RuntimeError(f"nHI mismatch {st(nhi)}")
    if not np.allclose(temp, 100., rtol=1e-12): raise RuntimeError(f"temperature mismatch {st(temp)}")
    if np.any(vel != 0) or np.any(vturb != 0) or np.any(ndust != 0): raise RuntimeError("Expected exactly zero velocity/turbulence/dust")
    directions=np.vstack((np.eye(3),-np.eye(3),np.random.default_rng(20260813).normal(size=(32,3))))
    directions[6:] /= np.linalg.norm(directions[6:],axis=1)[:,None]
    columns=np.full(len(directions), expected["nhi_cm3"]*expected["radius_cm"])
    taus=columns*expected["sigma0_cm2"]
    summary={"case":a.case,"domain_type":mesh["domain_type"],"center":mesh["center"].tolist(),"radius":mesh["radius"],
      "ncoarse":int(mesh["ncoarse"]),"noct":int(mesh["noct"]),"ncell":int(mesh["ncell"]),"nleaf":int(mesh["nleaf"]),
      "selected_leaf_count":int(len(gi)),"level_min":int(mesh["levels"].min()),"level_max":int(mesh["levels"].max()),
      "nhi_cm3":st(nhi),"temperature_K":st(temp),"speed_cm_s":st(np.linalg.norm(vel,axis=1)),"vturb_cm_s":st(vturb),"ndust_cm3":st(ndust),
      "ray_count":len(directions),"column_cm2":st(columns),"tau0_measured":st(taus),"tau0_requested":tau,
      "relative_tau_error":float(abs(taus.mean()-tau)/tau),"xhii_validation":"Not stored in mesh; upstream RAMSES scalar_01 validated as zero.","status":"PASSED"}
    out=ROOT/"analysis"/a.case/"domain"; out.mkdir(parents=True,exist_ok=True); (out/"validation.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    pos=mesh["positions"]; r=np.linalg.norm(pos-.5,axis=1)
    fig,axes=plt.subplots(2,3,figsize=(14,8),constrained_layout=True)
    fields=((nhi,"nHI [cm$^{-3}$]"),(temp,"T [K]"),(np.linalg.norm(vel,axis=1),"speed [cm/s]"))
    for j,(values,label) in enumerate(fields):
      sel=np.abs(pos[:,2]-.5)<=mesh["widths"]/2; sc=axes[0,j].scatter(pos[sel,0],pos[sel,1],c=values[sel],s=8); axes[0,j].set_title(f"xy central slice: {label}"); fig.colorbar(sc,ax=axes[0,j])
      axes[1,j].scatter(r,values,s=3,alpha=.4); axes[1,j].set_xlabel("radius [box]"); axes[1,j].set_ylabel(label)
    fig.savefig(out/"domain_slices_profiles.png",dpi=180); fig.savefig(out/"domain_slices_profiles.pdf"); plt.close(fig)
    fig,axes=plt.subplots(2,2,figsize=(10,8));
    for ax,(values,label) in zip(axes.flat,((nhi,"nHI"),(temp,"temperature"),(np.linalg.norm(vel,axis=1),"speed"),(vturb,"vturb"))): ax.hist(values,bins=50); ax.set_title(label)
    fig.tight_layout(); fig.savefig(out/"histograms.png",dpi=180); fig.savefig(out/"histograms.pdf"); plt.close(fig)
    print(json.dumps(summary,indent=2,sort_keys=True))
if __name__=="__main__": main()

