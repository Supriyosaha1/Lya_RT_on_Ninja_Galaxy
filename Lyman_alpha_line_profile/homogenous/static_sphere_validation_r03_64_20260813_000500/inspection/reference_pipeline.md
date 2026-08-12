# Reference Pipeline Reconstruction

The read-only reference uses:

1. RAMSES-like single-CPU AMR/hydro output at level 6.
2. `CreateDomDump CDD.cfg`, producing `compute_domain.dom`, `domain_1.dom`, `domain_1.mesh`, and `domain_decomposition_params.dat`.
3. `PhotonsFromSourceModel PPIC.cfg`, producing `Cont.IC` for a point source.
4. MPI `rascas Cont.cfg`, producing `Cont.res` and mock files.
5. Python `rascas/py/jphot.py` and `mocks.py` for photon-list/mock spectra.

The suffix `n1e5` means 100,000 photon packets (`PPIC.cfg: nPhotonPackets=100000`), not optical depth.

LEAP uses PBS (`/opt/pbs/bin/qsub`, `/opt/pbs/bin/qstat`), queue `serial` for domain/photon generation and `mpi` for transport. The RASCAS binary is Intel-MPI linked and becomes fully resolvable after `module load gcc_7`. Reference large jobs use 8 nodes × 32 ranks, 72 hours; smaller MPI jobs use 3 × 32, 12 hours.

The historical corrected domain is not a scientific baseline: its dump is 10,000 K with `nHI≈7146 cm^-3`. Recent historical transport attempts produced no completed `Cont.res`; their configurations are used only for syntax/resource conventions.

