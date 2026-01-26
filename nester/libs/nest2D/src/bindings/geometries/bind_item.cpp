#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "item.hpp"

namespace py = pybind11;


void bind_item(py::module &m) {
    py::class_<Item>(m, "Item", "An item to be placed on a sheet.")
            .def(py::init(&item::create), py::arg("points"))

            .def("get_points", &item::get_points)
            .def("area", &item::area)

            .def("__repr__", &item::repr);
}
