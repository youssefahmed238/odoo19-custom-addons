#include "box.hpp"
#include "../utils/converter.hpp"

namespace box {
    Box *create(const double width, const double height) {
        const double center_x = width / 2.0;
        const double center_y = height / 2.0;

        return new Box(Convertor::mm_to_lib(width), Convertor::mm_to_lib(height),
                       {Convertor::mm_to_lib(center_x), Convertor::mm_to_lib(center_y)});
    }
}
