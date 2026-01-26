#ifndef GEOMETRIES_BOX_HPP
#define GEOMETRIES_BOX_HPP
#pragma once

#include <libnest2d/libnest2d.hpp>

using Box = libnest2d::Box;

namespace box {
    Box *create(double width, double height);
}

#endif //GEOMETRIES_BOX_HPP
