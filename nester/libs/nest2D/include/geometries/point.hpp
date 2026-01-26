#ifndef GEOMETRIES_POINT_HPP
#define GEOMETRIES_POINT_HPP
#pragma once

#include <libnest2d/libnest2d.hpp>
#include <string>

using namespace std;

using Point = libnest2d::Point;


namespace point {
    Point *create(double x, double y);

    double get_x(const Point &p);

    double get_y(const Point &p);

    string repr(const Point &p);

    bool eq(const Point &p, const Point &q);
}


#endif //GEOMETRIES_POINT_HPP
