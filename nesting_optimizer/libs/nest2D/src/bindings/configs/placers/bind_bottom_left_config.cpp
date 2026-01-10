#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "bottom_left_config.hpp"

namespace py = pybind11;


void bind_bottom_left_config(py::module &m) {
    py::class_<BottomLeftConfig>(m, "BottomLeftPlacerConfig",
                                 "Configuration for Bottom-Left Placer")
            .def(py::init())

            .def_property("spacing",
                          &BottomLeftConfig::get_min_obj_distance,
                          &BottomLeftConfig::set_min_obj_distance,
                          "Minimum distance between objects when placing.")

            .def_property("epsilon",
                          &BottomLeftConfig::get_epsilon,
                          &BottomLeftConfig::set_epsilon,
                          "Epsilon value for placement precision.")

            .def_property("allow_rotations",
                          &BottomLeftConfig::get_allow_rotations,
                          &BottomLeftConfig::set_allow_rotations,
                          "Whether to allow rotations of items during placement.")

            .def("reset", &BottomLeftConfig::reset,
                 "Reset configuration to default values.")

            .def("__str__", &BottomLeftConfig::str,
                 "String representation of the configuration.");
}
