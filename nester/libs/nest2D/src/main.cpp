#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

// =======================================

// Geometries
void bind_point(py::module& m);
void bind_item(py::module& m);
void bind_box(py::module& m);

// =======================================

// Configs

//    Main Config
void bind_config(py::module& m);

//    Selectors
void bind_djd_config(py::module& m);

//    Placers
void bind_bottom_left_config(py::module& m);
void bind_nfp_config(py::module& m);

// =======================================

// Nester

//    Result
void bind_result(py::module& m);

//    Nest
void bind_nest(py::module& m);

// =======================================


PYBIND11_MODULE(nest2D, m)
{
    m.doc() = "2D irregular bin packaging and nesting for python";

    // =======================================

    // Geometries
    bind_point(m);
    bind_item(m);
    bind_box(m);

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

    // Nester

    //    Nest
    bind_nest(m);

    //    Result
    bind_result(m);

    // =======================================
}
