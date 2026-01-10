#include <pybind11/pybind11.h>

#include "djd_config.hpp"

namespace py = pybind11;

void bind_djd_config(py::module &m) {
    py::class_<DJDConfig>(
                m, "DJDConfig", "Configuration for the DJD heuristic selector")
            .def(py::init<>())
            .def_property("try_reverse_order",
                          &DJDConfig::get_try_reverse_order,
                          &DJDConfig::set_try_reverse_order,
                          "If true, the algorithm will try to place pair and triplets in "
                          "all possible order. It will have a hugely negative impact on "
                          "performance.")

            .def_property("try_pairs",
                          &DJDConfig::get_try_pairs,
                          &DJDConfig::set_try_pairs,
                          "Whether to try pairs of items to pack. It will add a "
                          "quadratic component to the complexity.")

            .def_property("try_triplets",
                          &DJDConfig::get_try_triplets,
                          &DJDConfig::set_try_triplets,
                          "Whether to try groups of 3 items to pack. This could be very "
                          "slow for large number of items (>100) as it adds a cubic "
                          "component to the complexity.")

            .def_property("initial_fill_proportion",
                          &DJDConfig::get_initial_fill_proportion,
                          &DJDConfig::set_initial_fill_proportion,
                          "The initial fill proportion of the bin area that will be "
                          "filled before trying items one by one, or pairs or triplets.")

            .def_property("waste_increment",
                          &DJDConfig::get_waste_increment,
                          &DJDConfig::set_waste_increment,
                          "How much is the acceptable waste incremented at each iteration.")

            .def_property("allow_parallel",
                          &DJDConfig::get_allow_parallel,
                          &DJDConfig::set_allow_parallel,
                          "Allow parallel jobs for filling multiple bins. This will "
                          "decrease the solution quality but can greatly boost up "
                          "performance for large number of items.")

            .def_property("force_parallel",
                          &DJDConfig::get_force_parallel,
                          &DJDConfig::set_force_parallel,
                          "Always use parallel processing if the items don't fit into "
                          "one bin.")

            .def("reset", &DJDConfig::reset, "Reset configuration to default values.")

            .def("__str__", &DJDConfig::str, "String representation of the configuration.");
}
