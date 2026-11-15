"""Cases where TwoQubitBasisDecomposer.num_basis_gates disagrees with the synthesis.

Run with any Qiskit >= 2.2.0. Each case prints num_basis_gates, the number of CX gates in the
synthesized circuit, and the coordinates from weyl_coordinates and from the full Weyl
decomposition.
"""

import numpy as np

from qiskit import QuantumCircuit
from qiskit.circuit.library import CXGate
from qiskit.quantum_info import Operator
from qiskit.synthesis import TwoQubitBasisDecomposer, TwoQubitWeylDecomposition
from qiskit._accelerate.two_qubit_decompose import weyl_coordinates

DECOMPOSER = TwoQubitBasisDecomposer(CXGate(), basis_fidelity=1.0)


def report(label, unitary):
    weyl = TwoQubitWeylDecomposition(unitary)
    print(label)
    print("  num_basis_gates:     ", DECOMPOSER.num_basis_gates(unitary))
    print("  CX in the synthesis: ", DECOMPOSER(unitary).count_ops().get("cx", 0))
    print("  weyl_coordinates:    ", np.round(weyl_coordinates(unitary), 6))
    print("  Weyl decomposition:  ", np.round([weyl.a, weyl.b, weyl.c], 6))


# 1. Undercount: a SWAP-class unitary counted as 0 (expected 3).
undercount = QuantumCircuit(2)
undercount.swap(0, 1)
undercount.h(0)
report("swap(0, 1); h(0)", Operator(undercount).data)

# 2. Overcount: a CX-class unitary counted as 2 (expected 1).
overcount = QuantumCircuit(2)
overcount.h(1)
overcount.cx(0, 1)
overcount.sx(0)
overcount.sdg(1)
report("h(1); cx(0, 1); sx(0); sdg(1)", Operator(overcount).data)

# 3. The result depends on the last bits of the matrix: rounding the entries of case 1 to 15
# significant digits (0.7071067811865475 -> 0.707106781186548) restores the count.
rounded = np.vectorize(lambda z: complex(float(f"{z.real:.15g}"), float(f"{z.imag:.15g}")))
report("swap(0, 1); h(0), rounded to 15 significant digits", rounded(Operator(undercount).data))

# 4. SWAP alone is counted correctly.
swap = QuantumCircuit(2)
swap.swap(0, 1)
report("swap(0, 1)", Operator(swap).data)
