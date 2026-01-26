#include "config.hpp"

size_t Config::nest(Items &items, const Box &box, const double spacing, const Config &config) {
    Coord dist = Convertor::mm_to_lib(spacing);

    switch (config.placer) {
        case Placer::NFP: {
            switch (config.selector) {
                case Selector::FirstFit: {
                    libnest2d::NestConfig<> nfp_first_fit_config;
                    nfp_first_fit_config.placer_config = config.nfp_config.config;
                    return libnest2d::nest<NFP, FirstFit>(items, box, dist, nfp_first_fit_config);
                }
                // case Selector::Filler: {
                //     libnest2d::NestConfig<NFP, Filler> nfp_fill_config;
                //     nfp_fill_config.placer_config = config.nfp_config.config;
                //     return libnest2d::nest<NFP, Filler>(items, box, dist, nfp_fill_config);
                // }
                case Selector::DJD: {
                    libnest2d::NestConfig<NFP, DJD> nfp_djd_config;
                    nfp_djd_config.placer_config = config.nfp_config.config;
                    nfp_djd_config.selector_config = config.djd_config.config;
                    return libnest2d::nest<NFP, DJD>(items, box, dist, nfp_djd_config);
                }
            }
            break;
        }
        case Placer::BottomLeft: {
            switch (config.selector) {
                case Selector::FirstFit: {
                    libnest2d::NestConfig<BottomLeft> bottom_left_first_fit_config;
                    bottom_left_first_fit_config.placer_config = config.bottom_left_config.config;
                    return libnest2d::nest<BottomLeft, FirstFit>(items, box, dist, bottom_left_first_fit_config);
                }
                // case Selector::Filler: {
                //     libnest2d::NestConfig<BottomLeft, Filler> bottom_left_fill_config;
                //     bottom_left_fill_config.placer_config = config.bottom_left_config.config;
                //     return libnest2d::nest<BottomLeft, Filler>(items, box, dist, bottom_left_fill_config);
                // }
                case Selector::DJD: {
                    libnest2d::NestConfig<BottomLeft, DJD> bottom_left_djd_config;
                    bottom_left_djd_config.placer_config = config.bottom_left_config.config;
                    bottom_left_djd_config.selector_config = config.djd_config.config;
                    return libnest2d::nest<BottomLeft, DJD>(items, box, dist, bottom_left_djd_config);
                }
            }
            break;
        }
    }

    return 0;
}
