#include <pybind11/stl.h>

#include "nester.hpp"

void bind_nest(py::module &m) {
    m.def("nest", Nester::nest,
          py::arg("items"),
          py::arg("box"),
          py::arg("spacing") = 0.0,
          py::arg("config") = Config(),
          "Nest and pack items according to the provided configuration."
    );
}
