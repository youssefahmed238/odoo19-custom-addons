#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "config.hpp"

namespace py = pybind11;

void bind_config(py::module &m) {
    py::enum_<Placer>(m, "Placer", "Type of placer algorithm")
            .value("NFP", Placer::NFP)
            .value("BottomLeft", Placer::BottomLeft)
            .export_values();

    py::enum_<Selector>(m, "Selector", "Type of selector algorithm")
            .value("FirstFit", Selector::FirstFit)
            // .value("Filler", Selector::Filler)
            .value("DJD", Selector::DJD)
            .export_values();

    py::class_<Config>(m, "Config", "Configuration for nesting algorithms.")
            .def(py::init<>(), "Create a default Config with NFP Placer and FirstFit Selector.")
            .def(py::init<const Placer, const Selector>(),
                 py::arg("placer") = Placer::NFP,
                 py::arg("selector") = Selector::FirstFit,
                 "Create a Config with specified Placer and Selector types.")

            .def_readwrite("nfp_config", &Config::nfp_config, "NFP placer configuration.")
            .def_readwrite("bottom_left_config", &Config::bottom_left_config, "Bottom-left placer configuration.")

            .def_readwrite("djd_config", &Config::djd_config, "DJD selector configuration.");
}
