#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "point.hpp"

namespace py = pybind11;


void bind_point(py::module &m) {
    py::class_<Point>(m, "Point", "2D Point")

            .def(py::init(&point::create), py::arg("x"), py::arg("y"))

            .def_property_readonly("x", &point::get_x)
            .def_property_readonly("y", &point::get_y)

            .def("__repr__", &point::repr)
            .def("__eq__", &point::eq);
}
