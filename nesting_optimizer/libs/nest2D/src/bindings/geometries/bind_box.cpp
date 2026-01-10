#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "box.hpp"

namespace py = pybind11;

void bind_box(py::module &m) {
    py::class_<Box>(m, "Box", "2D Box point pair")
            .def(py::init(&box::create), py::arg("width"), py::arg("height"));
}
