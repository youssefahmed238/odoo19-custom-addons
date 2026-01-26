#ifndef NESTER_NESTER_HPP
#define NESTER_NESTER_HPP

#include <pybind11/pybind11.h>

#include "config.hpp"
#include "result.hpp"

namespace py = pybind11;

class Nester {
public:
    static Result nest(Items &items, const Box &box, double spacing, const Config &config);
};

#endif // NESTER_NESTER_HPP
