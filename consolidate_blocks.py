"""Effect on ConsolidateBlocks, which replaces a block only if num_basis_gates is lower."""

from qiskit import QuantumCircuit
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import ConsolidateBlocks, UnitarySynthesis

# Overcount: a two-CX block whose unitary needs one CX is kept as it is.
circuit = QuantumCircuit(2)
circuit.sdg(1)
circuit.cx(0, 1)
circuit.h(0)
circuit.cx(0, 1)
circuit.sdg(0)
circuit.sx(1)

gates = ["cx", "h", "s", "sdg", "x", "sx", "t", "z", "rz"]
synthesis = UnitarySynthesis(basis_gates=["cx", "rz", "sx", "x"])
kept = PassManager([ConsolidateBlocks(basis_gates=gates), synthesis]).run(circuit)
forced = PassManager(
    [ConsolidateBlocks(basis_gates=gates, force_consolidate=True), synthesis]
).run(circuit)
print("CX after ConsolidateBlocks:       ", kept.count_ops().get("cx", 0))  # 2
print("CX with force_consolidate=True:   ", forced.count_ops().get("cx", 0))  # 1


# Undercount: a minimal three-CX SWAP block is consolidated because the count is 0.
def block(with_h):
    swap = QuantumCircuit(2)
    swap.cx(0, 1)
    swap.cx(1, 0)
    swap.cx(0, 1)
    if with_h:
        swap.h(0)
    return swap


consolidate = PassManager([ConsolidateBlocks(basis_gates=["cx", "h", "rz", "sx", "x"])])
print("SWAP block:      ", dict(consolidate.run(block(False)).count_ops()))  # {'cx': 3}
print("SWAP block + h:  ", dict(consolidate.run(block(True)).count_ops()))  # {'unitary': 1}
