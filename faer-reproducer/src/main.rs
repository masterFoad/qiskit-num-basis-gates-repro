// faer returns four zero eigenvalues for a 4x4 complex matrix that is a multiple of the identity
// up to tiny symmetric anti-diagonal entries.  The exact eigenvalues are d +- e (each twice).
use faer::{c64, Mat};

fn main() {
    let d = c64::new(-2.220446049250313e-16, 1.0000000000000002);
    let e = 1.232595164407831e-32;
    let zero = c64::new(0.0, 0.0);
    let matrix = Mat::<c64>::from_fn(4, 4, |r, c| match (r, c) {
        (0, 0) | (1, 1) | (2, 2) | (3, 3) => d,
        (0, 3) | (3, 0) => c64::new(-e, 0.0),
        (1, 2) | (2, 1) => c64::new(e, 0.0),
        _ => zero,
    });
    println!("{:?}", matrix.eigenvalues().unwrap());
}
