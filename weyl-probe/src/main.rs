// Probe of the first steps of __weyl_coordinates (Qiskit, crates/synthesis/src/two_qubit_decompose/
// weyl_decomposition.rs) with faer 0.24.4: determinant, scaling, magic-basis transform, M^T M and
// its eigenvalues, for three two-qubit unitaries.
use faer::{c64, Mat, Scale};

fn probe(name: &str, rows: [[c64; 4]; 4]) {
    let z = c64::new(0.0, 0.0);
    let o = c64::new(1.0, 0.0);
    let i = c64::new(0.0, 1.0);
    let h = c64::new(0.5, 0.0);
    let hi = c64::new(0.0, 0.5);
    // B_NON_NORMALIZED and B_NON_NORMALIZED_DAGGER of the Qiskit source
    let b = [[o, i, z, z], [z, z, i, o], [z, z, i, -o], [o, -i, z, z]];
    let bd = [[h, z, z, h], [-hi, z, z, hi], [z, -hi, -hi, z], [z, h, -h, z]];
    let u = Mat::<c64>::from_fn(4, 4, |r, c| rows[r][c]);
    let det = u.determinant();
    let scaled = Scale(o / det.powf(0.25)) * &u;
    let uup = Mat::<c64>::from_fn(4, 4, |r, c| bd[r][c]) * &scaled * Mat::<c64>::from_fn(4, 4, |r, c| b[r][c]);
    let m2 = uup.transpose() * &uup;
    println!("{name}: determinant = ({:e}, {:e})", det.re, det.im);
    for r in 0..4 {
        let row: Vec<String> = (0..4).map(|c| format!("({:.3e}, {:.3e})", m2[(r, c)].re, m2[(r, c)].im)).collect();
        println!("  M^T M row {r}: {}", row.join(" "));
    }
    let ev = m2.eigenvalues().unwrap();
    let shown: Vec<String> = ev.iter().map(|x| format!("({:.6}, {:.6})", x.re, x.im)).collect();
    println!("  faer eigenvalues: {}", shown.join(" "));
    println!("  moduli: {:?}", ev.iter().map(|x| (x.re * x.re + x.im * x.im).sqrt()).collect::<Vec<_>>());
}

fn main() {
    probe("swap(0, 1)", SWAP);
    probe("swap(0, 1); h(0)", SWAP_H);
    probe("h(1); cx(0, 1); sx(0); sdg(1)", CX_DRESSED);
}

const SWAP: [[c64; 4]; 4] = [[c64 { re: 1.0, im: 0.0 }, c64 { re: 0.0, im: 0.0 }, c64 { re: 0.0, im: 0.0 }, c64 { re: 0.0, im: 0.0 }], [c64 { re: 0.0, im: 0.0 }, c64 { re: 0.0, im: 0.0 }, c64 { re: 1.0, im: 0.0 }, c64 { re: 0.0, im: 0.0 }], [c64 { re: 0.0, im: 0.0 }, c64 { re: 1.0, im: 0.0 }, c64 { re: 0.0, im: 0.0 }, c64 { re: 0.0, im: 0.0 }], [c64 { re: 0.0, im: 0.0 }, c64 { re: 0.0, im: 0.0 }, c64 { re: 0.0, im: 0.0 }, c64 { re: 1.0, im: 0.0 }]];
const SWAP_H: [[c64; 4]; 4] = [[c64 { re: 0.7071067811865475, im: 0.0 }, c64 { re: 0.0, im: 0.0 }, c64 { re: 0.7071067811865475, im: 0.0 }, c64 { re: 0.0, im: 0.0 }], [c64 { re: 0.7071067811865475, im: 0.0 }, c64 { re: 0.0, im: 0.0 }, c64 { re: -0.7071067811865475, im: 0.0 }, c64 { re: 0.0, im: 0.0 }], [c64 { re: 0.0, im: 0.0 }, c64 { re: 0.7071067811865475, im: 0.0 }, c64 { re: 0.0, im: 0.0 }, c64 { re: 0.7071067811865475, im: 0.0 }], [c64 { re: 0.0, im: 0.0 }, c64 { re: 0.7071067811865475, im: 0.0 }, c64 { re: 0.0, im: 0.0 }, c64 { re: -0.7071067811865475, im: 0.0 }]];
const CX_DRESSED: [[c64; 4]; 4] = [[c64 { re: 0.35355339059327373, im: 0.35355339059327373 }, c64 { re: 0.35355339059327373, im: -0.35355339059327373 }, c64 { re: 0.35355339059327373, im: 0.35355339059327373 }, c64 { re: -0.35355339059327373, im: 0.35355339059327373 }], [c64 { re: 0.35355339059327373, im: -0.35355339059327373 }, c64 { re: 0.35355339059327373, im: 0.35355339059327373 }, c64 { re: 0.35355339059327373, im: -0.35355339059327373 }, c64 { re: -0.35355339059327373, im: -0.35355339059327373 }], [c64 { re: 0.35355339059327373, im: -0.35355339059327373 }, c64 { re: -0.35355339059327373, im: -0.35355339059327373 }, c64 { re: -0.35355339059327373, im: 0.35355339059327373 }, c64 { re: -0.35355339059327373, im: -0.35355339059327373 }], [c64 { re: -0.35355339059327373, im: -0.35355339059327373 }, c64 { re: 0.35355339059327373, im: -0.35355339059327373 }, c64 { re: 0.35355339059327373, im: 0.35355339059327373 }, c64 { re: 0.35355339059327373, im: -0.35355339059327373 }]];
