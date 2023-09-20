// mod go_board;
// mod go_stone;

// use pyo3::prelude::*;

// #[pyfunction]
// pub fn my_add(left: usize, right: usize) -> usize {
//     left + right
// }

// #[pyclass]
// struct ClassTest {
//     #[pyo3(get, set)]
//     size: i32,
//     #[pyo3(get, set)]
//     block_liberty: Vec<i32>,
// }

// #[pymethods]
// impl ClassTest {
//     #[new]
//     fn new(a: i32, v: Vec<i32>) -> PyResult<ClassTest> {
//         Ok(ClassTest {
//             size: a,
//             block_liberty: v,
//         })
//     }

//     // #[classmethod]
//     fn change_size(&mut self, a: i32) {
//         self.size = a;
//     }

//     fn change_liberty(&mut self, v: Vec<i32>) {
//         self.block_liberty = v;
//     }
// }

// #[pymodule]
// fn rotax_infrastructure(_py: Python<'_>, module: &PyModule) -> PyResult<()> {
//     module.add_function(wrap_pyfunction!(my_add, module)?)?;
//     module.add_class::<ClassTest>()?;
//     // module.add_function(wrap_pyfunction!(new, module)?)?;

//     Ok(())
// }

// #[cfg(test)]
// mod tests {
//     use super::*;

//     #[test]
//     fn it_works() {
//         let result = my_add(2, 2);
//         assert_eq!(result, 4);
//     }
// }
