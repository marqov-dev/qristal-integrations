# Qiskit V1 adapter: public CPU qualification

QristalEstimator previously applied X/Y basis changes to the wrong qubit: Qiskit Pauli labels are written with qubit 0 at the right-hand end. For `IX` on a state with qubit 0 in |+>, the old code measured approximately zero instead of +1. The patch reverses label iteration when constructing measurement rotations. Counts-to-observable parity already uses the corresponding label ordering.

## Evidence

Sixteen small checks pass against real rebuilt Qristal Core sessions on **qpp and native CPU Aer**: deterministic X on either qubit; batched parameter binding; asymmetric IZ/ZI and IX/XI observables; and a Y eigenstate. Each session uses 4096 shots, seed 42, no placement/optimization and an explicitly empty remote backend database. Estimator tolerance is absolute 0.05; deterministic samples and shot totals are checked exactly. Before-fix failure and final results are retained under `evidence/2026-09-09` with checksums.

Sources: Integrations baseline `86aacff70844605dec5302d37f3f11cae718f805`; Core merged commit `55fa21f502e47dd486ac624514af0a7983db2cab`; public XACC `d1edaa7ae53edc7e335f46d33160f93d6020aaa3`; CPU qualification recipe at marqov-dev/qristal commit `f877262387cebc2f792dda5d722ba689e57d6fb7`. The locally qualified XACC also includes the public qpe plugin used by Decoder; no commercial libraries are present.

The environment is Ubuntu 22.04, Linux amd64 under emulation, GCC 11.4 and Python 3.10.12. The container has 2 CPUs, 4 GiB memory including swap, 256 PIDs and networking disabled for tests. Public pip acquisition is a separate step. The initial pip attempt exceeded the 256 MiB container tmpfs; retrying with a dedicated workspace temporary directory succeeded. No host dependencies were installed.

## Reproduce

First build the public Core CPU/noise workspace using the recipe above. In the same isolated workspace, install `requirements-cpu.txt` into a **separate Python target directory or clean environment**, not into Core's Qiskit 0.46 dependency environment. This adapter targets Qiskit **1.2.0** and its V1 primitives; the distinction matters.

For the recorded target-directory layout, the container environment is:

```text
PYTHONNOUSERSITE=1
PYTHONPATH=/work/python:/work/integration-deps:/work/qristal-integrations/qiskit_integration
OMP_NUM_THREADS=2
OPENBLAS_NUM_THREADS=2
```

`/work/python` exposes the rebuilt Core extension, and `/work/integration-deps` contains the packages in requirements-cpu.txt. Run `python3 -s -B /work/qristal-integrations/qualification/cpu_smoke.py`. The fixture assumes the CPU recipe's empty backend file at `/work/qristal/qualification/empty-backends.yaml` and its two Core transpiler plugins in the isolated XACC prefix. A Python exception or missing PASS line is a failure.

## Limits and bounded follow-ups

This qualifies the small sampler/estimator path with Qiskit 1.2, not the entire Integrations collection. Qiskit V2/current-version support, QAOA/VQE applications, concurrent calls on shared sessions, per-run shot options, mixed-width circuits and arbitrary classical measurement remapping need separate checks. IDE, Nextflow, remote/vQPU adapters, GPU, commercial Emulator and deployed platform execution are not exercised. The result is a build-tree runtime check, not a clean installed distribution or performance benchmark.
