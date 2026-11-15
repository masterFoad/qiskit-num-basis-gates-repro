"""Compare num_basis_gates with the synthesized CX count around common two-qubit gates.

For each two-qubit gate, put one optional gate from {h, s, sdg, x, y, z, sx, t} before and after
it on each qubit: 9**4 = 6,561 circuits per gate. Prints the number of circuits where the two
counts disagree and the wrong values seen. Pass --show N to print the first N failing circuits.
"""

import argparse
import itertools
from collections import Counter

from qiskit import QuantumCircuit
from qiskit.circuit.library import CXGate
from qiskit.quantum_info import Operator
from qiskit.synthesis import TwoQubitBasisDecomposer

LOCAL = [None, "h", "s", "sdg", "x", "y", "z", "sx", "t"]
TWO_QUBIT = ["swap", "iswap", "dcx", "cx", "cz", "ecr"]


def circuit_for(gate, before0, before1, after0, after1):
    circuit = QuantumCircuit(2)
    for name, qubit in ((before0, 0), (before1, 1)):
        if name:
            getattr(circuit, name)(qubit)
    getattr(circuit, gate)(0, 1)
    for name, qubit in ((after0, 0), (after1, 1)):
        if name:
            getattr(circuit, name)(qubit)
    return circuit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--show", type=int, default=0)
    args = parser.parse_args()
    decomposer = TwoQubitBasisDecomposer(CXGate(), basis_fidelity=1.0)
    print(f"{'gate':6} {'circuits':>8} {'wrong':>6}  wrong values (count: times)")
    for gate in TWO_QUBIT:
        wrong = Counter()
        shown = 0
        total = 0
        for locals_ in itertools.product(LOCAL, repeat=4):
            circuit = circuit_for(gate, *locals_)
            unitary = Operator(circuit).data
            estimate = decomposer.num_basis_gates(unitary)
            actual = decomposer(unitary).count_ops().get("cx", 0)
            total += 1
            if estimate != actual:
                wrong[(estimate, actual)] += 1
                if shown < args.show:
                    shown += 1
                    ops = [(i.operation.name, [circuit.find_bit(q).index for q in i.qubits])
                           for i in circuit.data]
                    print(f"  {gate}: {ops} num_basis_gates={estimate} synthesis={actual}")
        values = ", ".join(f"{e} instead of {a}: {n}" for (e, a), n in sorted(wrong.items()))
        print(f"{gate:6} {total:8} {sum(wrong.values()):6}  {values}")


if __name__ == "__main__":
    main()
