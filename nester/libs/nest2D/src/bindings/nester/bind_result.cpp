#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "result.hpp"

namespace py = pybind11;

void bind_result(py::module &m) {
    py::class_<Result>(m, "Result", "Result of a nesting operation")
            .def_readonly("bins", &Result::bins)
            .def_readonly("output", &Result::output);
}
