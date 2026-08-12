#!/usr/bin/env python3
"""Compare escaped RASCAS photons to the normalized analytical static sphere."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import FortranFile
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"analysis"))
from physics import C,LAMBDA_CM,PI,case_values  # noqa:E402

def read_result(path):
 f=FortranFile(path,"r"); n=int(f.read_ints(np.int32)[0]); ids=f.read_ints(np.int32); status=f.read_ints(np.int32); pos=f.read_reals(np.float64).reshape(n,3); nu=f.read_reals(np.float64); direction=f.read_reals(np.float64).reshape(n,3); nscat=f.read_ints(np.int32); time=f.read_reals(np.float64); f.close(); return locals()
def analytic(x,a,tau):
 arg=np.sqrt(2*PI**3/27)*np.abs(x)**3/(a*tau); den=1+np.cosh(np.clip(arg,0,700)); j=np.sqrt(PI/6)/(4*a*tau)*x*x/den; j[arg>700]=0; return 4*PI*j
def save(fig,path): fig.tight_layout(); fig.savefig(path.with_suffix(".png"),dpi=200); fig.savefig(path.with_suffix(".pdf")); plt.close(fig)
def main():
 p=argparse.ArgumentParser();p.add_argument("case",choices=("tau_1e05","tau_1e06","tau_1e07"));p.add_argument("stage",choices=("smoke","final","n1e5","n1e6","n1e7","n1e8"));a=p.parse_args();tau={"tau_1e05":1e5,"tau_1e06":1e6,"tau_1e07":1e7}[a.case];v=case_values(tau)
 run=ROOT/"rascas_run"/a.case/a.stage; data=read_result(run/"Cont.res"); esc=data["status"]==1; nu=data["nu"][esc]
 if len(nu)==0: raise RuntimeError("No escaped photons")
 nu0=C/LAMBDA_CM; x=(nu-nu0)/v["delta_nu_d_hz"]
 edges=np.arange(-100,100.0001,.5); counts,edges=np.histogram(x,bins=edges); centers=(edges[:-1]+edges[1:])/2; dx=.5; pdf=counts/(len(x)*dx); err=np.sqrt(counts)/(len(x)*dx); model=analytic(centers,v["a_voigt"],tau); model/=np.trapz(model,centers)
 red=centers<0;blue=centers>0; rp=centers[red][np.argmax(pdf[red])];bp=centers[blue][np.argmax(pdf[blue])]; rf=counts[red].sum();bf=counts[blue].sum(); l1=float(np.sum(np.abs(pdf-model))*dx); rms=float(np.sqrt(np.mean((pdf-model)**2))); mask=model>model.max()*1e-4; frac=(pdf-model)/np.where(model>0,model,np.nan); chi=float(np.sum(((pdf[mask]-model[mask])/np.where(err[mask]>0,err[mask],np.inf))**2));
 metrics={"case":a.case,"stage":a.stage,"tau0":tau,"n_total":int(data["n"]),"n_escaped":int(esc.sum()),"status_counts":{str(int(k)):int(n) for k,n in zip(*np.unique(data["status"],return_counts=True))},"mc_normalization":float(np.sum(pdf)*dx),"analytic_normalization":float(np.sum(model)*dx),"red_peak_x":float(rp),"blue_peak_x":float(bp),"peak_separation_x":float(bp-rp),"analytic_peak_abs_x_approx":v["x_peak_approx"],"red_blue_count_ratio":float(rf/bf),"symmetry_fraction":float(abs(rf-bf)/(rf+bf)),"center_probability_abs_x_lt_1":float(counts[np.abs(centers)<1].sum()/len(x)),"l1_difference":l1,"rms_difference":rms,"chi_like":chi,"chi_bins":int(mask.sum()),"x_min":float(x.min()),"x_max":float(x.max()),"mean_scatterings":float(data["nscat"][esc].mean())}
 out=ROOT/"analysis"/a.case/a.stage;out.mkdir(parents=True,exist_ok=True);(out/"spectrum_metrics.json").write_text(json.dumps(metrics,indent=2,sort_keys=True)+"\n");np.savetxt(out/"spectrum.csv",np.c_[centers,counts,pdf,err,model,pdf-model,frac],delimiter=",",header="x,count,p_mc,poisson_error,p_analytic,residual,fractional_residual",comments="")
 plot_limit={"tau_1e05":25,"tau_1e06":55,"tau_1e07":100}[a.case]; title=rf"Static sphere: $\tau_0={tau:.0e}$, $N_\gamma={data['n']:,}$, all directions"
 fig,ax=plt.subplots();ax.step(centers,pdf,where="mid",label="RASCAS");ax.plot(centers,model,"k--",label="analytical");ax.axvline(0,color="crimson",ls=":",lw=1.6,label=r"input: monochromatic $x=0$");ax.set(xlabel="x",ylabel="unit-area p(x)",xlim=(-plot_limit,plot_limit),title=title);ax.legend();save(fig,out/"spectrum_linear")
 fig,ax=plt.subplots();ax.step(centers,np.maximum(pdf,1e-12),where="mid",label="RASCAS");ax.plot(centers,np.maximum(model,1e-12),"k--",label="analytical");ax.axvline(0,color="crimson",ls=":",lw=1.6,label=r"input: monochromatic $x=0$");ax.set_yscale("log");ax.set(xlabel="x",ylabel="p(x)",xlim=(-plot_limit,plot_limit),title=title);ax.legend();save(fig,out/"spectrum_log")
 fig,ax=plt.subplots();ax.plot(centers,pdf-model);ax.axhline(0,color="k",lw=.8);ax.set(xlabel="x",ylabel="MC - analytical");save(fig,out/"residual")
 fig,ax=plt.subplots();ax.plot(centers[mask],frac[mask]);ax.axhline(0,color="k",lw=.8);ax.set(xlabel="x",ylabel="fractional residual");save(fig,out/"fractional_residual")
 fig,ax=plt.subplots();ax.errorbar(centers,counts,yerr=np.sqrt(counts),fmt=".",ms=2);ax.set(xlabel="x",ylabel="photon counts");save(fig,out/"counts_poisson")
 positive=centers>0; folded_red=np.interp(centers[positive],-centers[red][::-1],pdf[red][::-1]);fig,ax=plt.subplots();ax.plot(centers[positive],pdf[positive],label="blue (+x)");ax.plot(centers[positive],folded_red,label="red folded");ax.set(xlabel="|x|",ylabel="p(x)");ax.legend();save(fig,out/"folded_halves")
 print(json.dumps(metrics,indent=2,sort_keys=True))
if __name__=="__main__":main()
