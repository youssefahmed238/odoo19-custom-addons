#ifndef CONFIGS_BOTTOM_LEFT_CONFIG_H
#define CONFIGS_BOTTOM_LEFT_CONFIG_H

#include <libnest2d/libnest2d.hpp>
#include "../utils/converter.hpp"

using BLConfig = libnest2d::placers::BLConfig<libnest2d::PolygonImpl>;

class BottomLeftConfig {
public:
    BLConfig config;

    double get_min_obj_distance() const { return Convertor::lib_to_mm(config.min_obj_distance); }
    void set_min_obj_distance(const double val) { config.min_obj_distance = Convertor::mm_to_lib(val); }

    double get_epsilon() const { return config.epsilon; }
    void set_epsilon(const double val) { config.epsilon = val; }

    bool get_allow_rotations() const { return config.allow_rotations; }
    void set_allow_rotations(const bool val) { config.allow_rotations = val; }

    void reset();

    std::string str() const;
};

#endif // CONFIGS_BOTTOM_LEFT_CONFIG_H
