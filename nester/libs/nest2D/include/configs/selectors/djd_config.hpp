#ifndef CONFIGS_DJD_CONFIG_H
#define CONFIGS_DJD_CONFIG_H
#pragma once

#include <libnest2d/libnest2d.hpp>

using DJD = libnest2d::DJDHeuristic;
using DjdConfig = DJD::Config;

class DJDConfig {
public:
    DjdConfig config;

    DJDConfig();

    bool get_try_reverse_order() const { return config.try_reverse_order; }
    void set_try_reverse_order(const bool val) { config.try_reverse_order = val; }


    bool get_try_pairs() const { return config.try_pairs; }
    void set_try_pairs(const bool val) { config.try_pairs = val; }


    bool get_try_triplets() const { return config.try_triplets; }
    void set_try_triplets(const bool val) { config.try_triplets = val; }


    double get_initial_fill_proportion() const { return config.initial_fill_proportion; }
    void set_initial_fill_proportion(const double val) { config.initial_fill_proportion = val; }


    double get_waste_increment() const { return config.waste_increment; }
    void set_waste_increment(const double val) { config.waste_increment = val; }


    bool get_allow_parallel() const { return config.allow_parallel; }
    void set_allow_parallel(const bool val) { config.allow_parallel = val; }


    bool get_force_parallel() const { return config.force_parallel; }
    void set_force_parallel(const bool val) { config.force_parallel = val; }


    void reset();

    std::string str() const;

private:
    void setupConfig();
};


#endif //CONFIGS_DJD_CONFIG_H
