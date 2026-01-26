#include "bottom_left_config.hpp"
#include <sstream>

void BottomLeftConfig::reset() {
    config = BLConfig();
}

std::string BottomLeftConfig::str() const {
    std::ostringstream oss;
    oss << "BottomLeftConfig(\n";
    oss << "min_obj_distance=" << config.min_obj_distance << ", \n";
    oss << "epsilon=" << config.epsilon << ", \n";
    oss << "allow_rotations=" << (config.allow_rotations ? "true" : "false") << "\n";
    oss << ")";
    return oss.str();
}
