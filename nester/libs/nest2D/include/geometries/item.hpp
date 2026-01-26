#ifndef GEOMETRIES_ITEM_HPP
#define GEOMETRIES_ITEM_HPP
#pragma once

#include <libnest2d/libnest2d.hpp>

using Point = libnest2d::Point;
using Item = libnest2d::Item;
using PyPoints = std::vector<std::pair<double, double>>;


namespace item
{
    Item* create(const PyPoints& points);

    PyPoints get_points(const Item& item);

    double area(const Item& item);

    std::string repr(const Item& item);
}

#endif //GEOMETRIES_ITEM_HPP
