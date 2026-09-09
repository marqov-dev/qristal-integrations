"""Small offline Qiskit V1 primitive checks against real rebuilt Core CPU sessions."""
import signal
signal.alarm(120)
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import SparsePauliOp
import qristal.core as q
from qristal_primitives import QristalSampler, QristalEstimator

passed = []
for backend in ("qpp", "aer"):
    session = q.session()
    session.acc = backend
    session.remote_backend_database_path = "/work/qristal/qualification/empty-backends.yaml"
    session.qn = 2
    session.sn = 4096
    session.seed = 42
    session.noplacement = True
    session.nooptimise = True
    sampler = QristalSampler(session)
    for bit in (0, 1):
        c = QuantumCircuit(2); c.x(bit); c.measure_all()
        result = sampler.run(c).result()
        assert dict(result.quasi_dists[0]) == {1 << bit: 1.0}, (backend, bit, result)
        assert result.metadata[0]["shots"] == 4096
        passed.append(f"{backend}:sample_x{bit}")
    theta = Parameter("theta")
    c = QuantumCircuit(2); c.ry(theta, 0); c.measure_all()
    result = sampler.run([c, c], [[0], [np.pi]]).result()
    assert [dict(d) for d in result.quasi_dists] == [{0: 1.0}, {1: 1.0}]
    passed.append(f"{backend}:parameter_batch")
    estimator = QristalEstimator(sampler)
    for label, prep, expected in [("IZ", "x0", -1), ("ZI", "x0", 1), ("IX", "h0", 1), ("XI", "h0", 0), ("IY", "y0", 1)]:
        c = QuantumCircuit(2)
        if prep == "x0": c.x(0)
        elif prep == "h0": c.h(0)
        else: c.h(0); c.s(0)
        value = estimator.run(c, SparsePauliOp(label)).result().values[0]
        assert abs(value - expected) < .05, (backend, label, value, expected)
        passed.append(f"{backend}:estimate_{label}")
print("PASS:", passed)
