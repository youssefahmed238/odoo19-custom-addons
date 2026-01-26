#include "item.hpp"
#include "point.hpp"

#include "../utils/converter.hpp"
#include <memory>

using Points = std::vector<Point>;

namespace item
{
    Item* create(const PyPoints& points)
    {
        Points lib_points;
        lib_points.reserve(points.size());
        for (const auto& [x, y] : points)
        {
            std::unique_ptr<Point> point(point::create(x, y));
            lib_points.emplace_back(*point);
        }
        return new Item(lib_points);
    }

    PyPoints get_points(const Item& item)
    {
        PyPoints points;

        auto& shape = item.transformedShape();
        const auto contour = libnest2d::shapelike::contour(shape);

        for (auto& vertex : contour)
        {
            points.emplace_back(Convertor::lib_to_mm(vertex.X),
                                Convertor::lib_to_mm(vertex.Y));
        }

        return points;
    }

    double area(const Item& item)
    {
        return Convertor::lib_to_mm(Convertor::lib_to_mm(item.area()));
    }

    std::string repr(const Item& item)
    {
        const auto binId = Convertor::cast<std::string>(item.binId());
        const auto area = Convertor::cast<std::string>(item::area(item));

        std::string points;
        for (const auto& [x, y]: get_points(item))
        {
            points += "(" + Convertor::cast<std::string>(x) + ", " + Convertor::cast<std::string>(y) + ")";
        }

        return "Item(area: " + area + ", bin_id: " + binId + ", points: " + points + ")";
    }
}
