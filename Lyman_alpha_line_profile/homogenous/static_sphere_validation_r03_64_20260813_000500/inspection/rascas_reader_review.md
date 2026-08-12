# RASCAS Reader Review

- `module_ramses.f90:2655-2663` reads `unit_l`, `unit_d`, and `unit_t`; converts density with `XH/mp*unit_d`, velocity with `unit_l/unit_t`, and pressure/density with `mp/kB*(unit_l/unit_t)^2`.
- With `ramses_rt=T`, `module_ramses.f90:1317-1340` uses `nHI=rho*scale_nH*(1-xHII)` and `T=(P/rho)*scale_T2*mu`. For absent helium ion fields (`iheii=iheiii=0`), neutral primordial gas has `mu=1/(0.76+0.25*0.24)=1.2195121951`.
- `itemp=5`, `imetal=6`, and `ihii=8` match the converter's eight-field descriptor. Internal energy field 7 is not directly used by RASCAS; pressure field 5 is authoritative.
- `module_gas_composition.f90:103-165` stores box size, cgs velocity, nHI, temperature-derived thermal motion, dust proxy, and configured turbulent velocity in the mesh dump. The dump does not store xHII itself.
- `CreateDomDump.f90:89-125` constructs the exact spherical computational boundary. Lines 197-208 require it to be enclosed by the decomposition domain.
- `module_scatterer_model.f90:53-85` computes line optical depth using `delta_nu_D=sqrt(2kT/(amu*m_ion)+vturb^2)/lambda`, the configured Voigt approximation, and `sigma_factor=sqrt(pi)e^2 f/(m_e c)`.
- The validation atom file is a new copy of the reference settings: isotropic scattering, recoil off, core skipping on with `xcritmax=3`, Lee correction off. Dust is ignored and turbulent velocity is zero.
- Photon results store external-frame frequency in Hz (`module_photon.f90:712-728`); `jphot.py:72-106` confirms the Fortran-record order. The analysis uses frequency-sign convention `x=(nu-nu0)/delta_nu_D`.
- `cosmo=F` prevents cosmological expansion. The sphere, rather than Cartesian box faces, defines escape.

