#include "point.hpp"
#include "../utils/converter.hpp"

namespace point {

    Point* create(const double x, const double y) {
        return new Point(
            Convertor::mm_to_lib(x),
            Convertor::mm_to_lib(y)
        );
    }

    double get_x(const Point& p) {
        return Convertor::lib_to_mm(p.X);
    }

    double get_y(const Point& p) {
        return Convertor::lib_to_mm(p.Y);
    }

    std::string repr(const Point& p) {
        return "Point(" +
            std::to_string(get_x(p)) + ", " +
            std::to_string(get_y(p)) + ")";
    }

    bool eq(const Point& p, const Point& q) {
        return p == q;
    }

}
