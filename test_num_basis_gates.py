"""Suggested regression tests: num_basis_gates must match the synthesized CX count.

All three tests fail on Qiskit 2.2.0 to main (2.7.0.dev0) and are expected to pass after a fix.
"""

import itertools
import unittest

from qiskit import QuantumCircuit
from qiskit.circuit.library import CXGate
from qiskit.quantum_info import Operator
from qiskit.synthesis import TwoQubitBasisDecomposer


def count(circuit):
    """num_basis_gates and the synthesized CX count of a circuit's unitary."""
    decomposer = TwoQubitBasisDecomposer(CXGate(), basis_fidelity=1.0)
    unitary = Operator(circuit).data
    return decomposer.num_basis_gates(unitary), decomposer(unitary).count_ops().get("cx", 0)


class TestNumBasisGates(unittest.TestCase):
    """num_basis_gates for unitaries whose M^T M has repeated eigenvalues."""

    def test_swap_class_undercount(self):
        """A SWAP with a local gate needs 3 CX gates (num_basis_gates returned 0)."""
        circuit = QuantumCircuit(2)
        circuit.swap(0, 1)
        circuit.h(0)
        self.assertEqual(count(circuit), (3, 3))

    def test_cx_class_overcount(self):
        """A CX with local gates needs 1 CX gate (num_basis_gates returned 2)."""
        circuit = QuantumCircuit(2)
        circuit.h(1)
        circuit.cx(0, 1)
        circuit.sx(0)
        circuit.sdg(1)
        self.assertEqual(count(circuit), (1, 1))

    def test_agrees_with_synthesis_around_common_gates(self):
        """One optional local gate before and after a two-qubit gate on each qubit."""
        local = [None, "h", "s", "sdg", "x", "y", "z", "sx", "t"]
        for gate in ("swap", "iswap", "dcx", "cx", "cz", "ecr"):
            for before0, before1, after0, after1 in itertools.product(local, repeat=4):
                circuit = QuantumCircuit(2)
                for name, qubit in ((before0, 0), (before1, 1)):
                    if name:
                        getattr(circuit, name)(qubit)
                getattr(circuit, gate)(0, 1)
                for name, qubit in ((after0, 0), (after1, 1)):
                    if name:
                        getattr(circuit, name)(qubit)
                estimate, actual = count(circuit)
                with self.subTest(gate=gate, local=(before0, before1, after0, after1)):
                    self.assertEqual(estimate, actual)


if __name__ == "__main__":
    unittest.main()
