#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "nfp_config.hpp"

namespace py = pybind11;

using Alignment = NfpConfig::Alignment;

void bind_nfp_config(py::module &m) {
    py::enum_<Alignment>(m, "Alignment", "Alignment options for NFP Placer")
            .value("CENTER", Alignment::CENTER)
            .value("BOTTOM_LEFT", Alignment::BOTTOM_LEFT)
            .value("BOTTOM_RIGHT", Alignment::BOTTOM_RIGHT)
            .value("TOP_LEFT", Alignment::TOP_LEFT)
            .value("TOP_RIGHT", Alignment::TOP_RIGHT)
            .value("DONT_ALIGN", Alignment::DONT_ALIGN)
            .export_values();

    py::class_<NfpConfig>(m, "NfpConfig", "Configuration for NFP Placer")
            .def(py::init<>())

            .def_property("alignment",
                          &NfpConfig::getAlignment,
                          &NfpConfig::setAlignment,
                          "Get or set the alignment option for NFP Placer")

            .def_property("starting_point",
                          &NfpConfig::getStartingPoint,
                          &NfpConfig::setStartingPoint,
                          "Get or set the starting point option for NFP Placer")

            .def_property("rotations",
                          &NfpConfig::getRotations,
                          &NfpConfig::setRotations,
                          "Get or set the rotation angles for NFP Placer")

            .def_property("accuracy",
                          &NfpConfig::getAccuracy,
                          &NfpConfig::setAccuracy,
                          "Get or set the accuracy for NFP Placer")

            .def_property("explore_holes",
                          &NfpConfig::getExploreHoles,
                          &NfpConfig::setExploreHoles,
                          "Get or set whether to explore holes for NFP Placer")

            .def_property("parallel",
                          &NfpConfig::getParallel,
                          &NfpConfig::setParallel,
                          "Get or set whether to use parallel processing for NFP Placer")

            .def("reset", &NfpConfig::reset);
}
