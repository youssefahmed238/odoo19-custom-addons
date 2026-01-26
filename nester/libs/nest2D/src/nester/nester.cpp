#include "nester.hpp"

Result Nester::nest(Items &items, const Box &box, const double spacing, const Config &config) {
    const size_t bins = config.nest(items, box, spacing, config);

    return Result(bins, items);
}
