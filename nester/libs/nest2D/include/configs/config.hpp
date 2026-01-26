#ifndef CONFIGS_MAIN_CONFIG_HPP
#define CONFIGS_MAIN_CONFIG_HPP

#include <libnest2d/libnest2d.hpp>
#include <vector>

#include "nfp_config.hpp"
#include "bottom_left_config.hpp"

#include "djd_config.hpp"

using Items = std::vector<libnest2d::Item>;

using NFP = libnest2d::NfpPlacer;
using BottomLeft = libnest2d::BottomLeftPlacer;

using FirstFit = libnest2d::FirstFitSelection;
// using Filler = libnest2d::FillerSelection;
using DJD = libnest2d::DJDHeuristic;

enum class Placer {
    NFP,
    BottomLeft,
};

enum class Selector {
    FirstFit,
    // Filler,
    DJD
};


class Config {
public:
    Placer placer;
    Selector selector;

    NfpConfig nfp_config;
    BottomLeftConfig bottom_left_config;

    DJDConfig djd_config;

    Config() : placer{Placer::NFP}, selector{Selector::DJD} {
    }

    explicit Config(const Placer placer, const Selector selector)
        : placer{placer}, selector{selector} {
    }

    static size_t nest(Items &items, const Box &box, double spacing, const Config &config);
};


#endif // CONFIGS_MAIN_CONFIG_HPP
