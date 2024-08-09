use pyo3::prelude::*;
use polars::prelude::*;
use std::path::Path;

#[pyfunction]
fn print_first_three_rows(file_path: &str) -> PyResult<()> {
    // Read the Parquet file
    let df = LazyFrame::scan_parquet(Path::new(file_path), ScanArgsParquet::default())
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?
        .collect()
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;

    // Get the first 3 rows
    let first_three = df.slice(0, 3);

    // Print the first 3 rows
    println!("{}", first_three);

    Ok(())
}

#[pymodule]
fn hestia(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(print_first_three_rows, m)?)?;
    Ok(())
}