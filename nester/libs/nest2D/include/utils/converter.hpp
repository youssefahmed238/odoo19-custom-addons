#ifndef NEST2D_CONVERTER_HPP
#define NEST2D_CONVERTER_HPP
#pragma once

#include <libnest2d/libnest2d.hpp>

using Coord = libnest2d::Coord;

class Convertor {
public:
    // ==========================================
    // Unit conversion between millimeters and libnest2d coordinate units
    // ==========================================

    // Convert millimeter value to libnest2d coordinate units
    template<class T = double>
    static Coord mm_to_lib(T value = T(1)) {
        return libnest2d::mm(value);
    }

    // Convert libnest2d coordinate units to millimeter value
    template<class T = double, class U = Coord>
    static T lib_to_mm(const U &value) {
        auto coord = static_cast<Coord>(value);
        return static_cast<T>(coord) / static_cast<T>(libnest2d::mm()) ;
    }

    // ==========================================
    // Generic type casting using boost::lexical_cast
    // ==========================================

    // Cast value of type U to type T
    template<class T, class U>
    static T cast(const U &value) {
        return boost::lexical_cast<T>(value);
    }
};

#endif //NEST2D_CONVERTER_HPP