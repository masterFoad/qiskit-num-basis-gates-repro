# num_basis_gates reproducers

Reproducers and suggested regression tests for Qiskit issue
https://github.com/Qiskit/qiskit/issues/17443.

`TwoQubitBasisDecomposer.num_basis_gates` disagrees with the CX count of the circuit the same
decomposer synthesizes, for some two-qubit unitaries whose `M^T M` (in the magic basis) has
repeated eigenvalues. Two examples:

| circuit | num_basis_gates | CX in the synthesis |
| --- | --- | --- |
| `swap(0, 1); h(0)` | 0 | 3 |
| `h(1); cx(0, 1); sx(0); sdg(1)` | 2 | 1 |

The cause is in `__weyl_coordinates`: faer's `Mat::eigenvalues()` returns zeros for a matrix
that is a multiple of the identity up to off-diagonal entries of about 1e-32, which gives wrong
Weyl coordinates. `TwoQubitWeylDecomposition` uses a different eigensolver path and gets the
right coordinates, so the synthesis itself is correct. The behaviour appeared in Qiskit 2.2.0,
when faer moved from 0.19.4 to 0.21.9 (https://github.com/Qiskit/qiskit/pull/14873), and is
present on main.

## Files

| File | What it shows |
| --- | --- |
| `reproduce.py` | the undercount, the overcount, the dependence on the last bits of the matrix (rounding the entries to 15 significant digits restores the count), and `weyl_coordinates` next to the full Weyl decomposition |
| `consolidate_blocks.py` | the effect on `ConsolidateBlocks`: a two-CX block that needs one CX is kept, and a minimal SWAP block is consolidated |
| `sweep.py` | 6,561 circuits per two-qubit gate (swap, iswap, dcx, cx, cz, ecr), each with one optional local gate before and after on each qubit; prints the number of disagreements (`--show N` prints failing circuits) |
| `test_num_basis_gates.py` | suggested regression tests; all three fail on Qiskit 2.2.0 to main |
| `faer-reproducer/` | standalone Rust program: `Mat::eigenvalues()` on the near-scalar 4x4 matrix returns four zeros |
| `weyl-probe/` | standalone Rust program that repeats the first steps of `__weyl_coordinates` (determinant scaling, magic basis, `M^T M`, eigenvalues) and prints the intermediate values for three unitaries |
| `OUTPUT.txt` | the output of every file above on Qiskit 2.7.0.dev0 (main) |

## Running

```
pip install -r requirements.txt
python reproduce.py
python consolidate_blocks.py
python sweep.py
python test_num_basis_gates.py

cd faer-reproducer && cargo run --release
cd weyl-probe && cargo run --release
```

Both Rust programs pin faer 0.24.4, the version in Qiskit's current `Cargo.lock`. Changing the
pin to `=0.21.9` gives the same zeros.

## Sweep result on main

| two-qubit gate | circuits | wrong count | wrong values |
| --- | --- | --- | --- |
| swap | 6561 | 373 | 0 instead of 3 (362), 2 instead of 3 (11) |
| iswap | 6561 | 4 | 0 instead of 2 (4) |
| dcx | 6561 | 66 | 0 instead of 2 (66) |
| cx | 6561 | 32 | 0 instead of 1 (12), 2 instead of 1 (20) |
| cz | 6561 | 35 | 0 instead of 1 (24), 2 instead of 1 (11) |
| ecr | 6561 | 48 | 0 instead of 1 (24), 2 instead of 1 (24) |

## Where the code is

Line numbers on main:

- `crates/synthesis/src/two_qubit_decompose/weyl_decomposition.rs`: `__weyl_coordinates`
  (line 194, the `.eigenvalues()` call at line 198) and `__num_basis_gates` (line 255).
  `TwoQubitWeylDecomposition::new_inner` (line 490) uses `self_adjoint_eigen` on a real
  combination of the real and imaginary parts of `M^T M` (lines 520-536).
- `crates/transpiler/src/passes/consolidate_blocks.rs`, lines 354-367: the
  `num_basis_gates < basis_count` decision.

## License

Apache License 2.0, see `LICENSE`.

## Credit

Created by Foad Abo Dahood (@masterFoad). If you copy, reuse or build on these reproducers or
tests, cite this repository (https://github.com/masterFoad/qiskit-num-basis-gates-repro) and credit
Foad Abo Dahood (@masterFoad). Under the Apache-2.0 license, keep the NOTICE file with any copy.
