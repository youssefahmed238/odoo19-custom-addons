#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <libnest2d/libnest2d.hpp>

#include "../tools/svgtools.hpp"

namespace py = pybind11;

using Box = libnest2d::Box;
using Item = libnest2d::Item;
using PackGroup = libnest2d::PackGroup;
using SVGWriter = libnest2d::svg::SVGWriter<libnest2d::PolygonImpl>;

// =======================================

// Geometries
void bind_point(py::module &m);

void bind_item(py::module &m);

void bind_box(py::module &m);

// =======================================

// Nester

//    Result
void bind_result(py::module &m);

//    Nest
void bind_nest(py::module &m);

// =======================================

// Configs

//    Main Config
void bind_config(py::module &m);

//    Selectors
void bind_djd_config(py::module &m);

//    Placers
void bind_bottom_left_config(py::module &m);

void bind_nfp_config(py::module &m);

// =======================================


PYBIND11_MODULE(nest2D, m) {
    m.doc() = "2D irregular bin packaging and nesting for python";

    // =======================================

    // Geometries
    bind_point(m);
    bind_item(m);
    bind_box(m);

    // =======================================

    // Nester

    //    Nest
    bind_nest(m);

    //    Result
    bind_result(m);

    // =======================================

    // Configs

    //    Main Config
    bind_config(m);

    //    Selectors
    bind_djd_config(m);

    //    Placers
    bind_bottom_left_config(m);
    bind_nfp_config(m);

    // =======================================

    py::class_<SVGWriter>(m, "SVGWriter", "SVGWriter tools to write pack_group to SVG.")
            .def(py::init([]() {
                SVGWriter::Config conf;
                conf.mm_in_coord_units = libnest2d::mm();
                return std::unique_ptr<SVGWriter>(new SVGWriter(conf));
            }))
            .def("write_packgroup", [](SVGWriter &sw, const PackGroup &pgrp) {
                sw.setSize(Box(libnest2d::mm(250), libnest2d::mm(210)));
                sw.writePackGroup(pgrp);
            })
            .def("save", [](SVGWriter &sw) {
                sw.save("out");
            })
            .def("__repr__",
                 [](const SVGWriter &sw) {
                     return std::string("SVGWriter()");
                 }
            );
}
