#include "item.hpp"
#include "../utils/converter.hpp"

namespace item {
    Item *create(const std::vector<std::pair<double, double> > &points) {
        std::vector<Point> lib_points;
        for (const auto &[x, y]: points) {
            lib_points.emplace_back(Convertor::mm_to_lib(x), Convertor::mm_to_lib(y));
        }
        return new Item(lib_points);
    }

    std::vector<std::pair<double, double> > get_points(const Item &item) {
        std::vector<std::pair<double, double> > points;

        auto &shape = item.transformedShape();
        const auto contour = libnest2d::shapelike::contour(shape);

        for (auto &vertex: contour) {
            points.emplace_back(Convertor::lib_to_mm(vertex.X),
                                Convertor::lib_to_mm(vertex.Y));
        }

        return points;
    }

    double area(const Item &item) {
        return Convertor::lib_to_mm(Convertor::lib_to_mm(item.area()));
    }

    std::string repr(const Item &item) {
        const auto binId = Convertor::cast<std::string>(item.binId());
        const auto area = Convertor::cast<std::string>(item::area(item));

        std::string points;
        for (const auto &[x, y]: get_points(item)) {
            points += "(" + Convertor::cast<std::string>(x) + ", " + Convertor::cast<std::string>(y) + ")";
        }

        return "Item(area: " + area + ", bin_id: " + binId + ", points: " + points + ")";
    }
}
