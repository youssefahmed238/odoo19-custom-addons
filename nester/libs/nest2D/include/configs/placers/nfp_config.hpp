#ifndef CONFIGS_NFP_CONFIG_HPP
#define CONFIGS_NFP_CONFIG_HPP

#include <libnest2d/libnest2d.hpp>

using PolygonImpl = libnest2d::PolygonImpl;
using Radians = libnest2d::Radians;
using Item = libnest2d::Item;
using Box = libnest2d::Box;
using Shapes = libnest2d::nfp::Shapes<libnest2d::PolygonImpl>;

using NFPConfig = libnest2d::placers::NfpPConfig<PolygonImpl>;

class NfpConfig {
public:
    NFPConfig config;

    using Alignment = NFPConfig::Alignment;

    NfpConfig();

    [[nodiscard]] Alignment getAlignment() const { return config.alignment; }
    void setAlignment(const Alignment alignment) { config.alignment = alignment; }

    [[nodiscard]] Alignment getStartingPoint() const { return config.starting_point; }
    void setStartingPoint(const Alignment starting_point) { config.starting_point = starting_point; }

    [[nodiscard]] std::vector<Radians> getRotations() const { return config.rotations; }
    void setRotations(const std::vector<Radians> &rotations) { config.rotations = rotations; }

    [[nodiscard]] float getAccuracy() const { return config.accuracy; }
    void setAccuracy(const float accuracy) { config.accuracy = accuracy; }

    [[nodiscard]] bool getExploreHoles() const { return config.explore_holes; }
    void setExploreHoles(const bool explore_holes) { config.explore_holes = explore_holes; }

    [[nodiscard]] bool getParallel() const { return config.parallel; }
    void setParallel(const bool parallel) { config.parallel = parallel; }

    void reset();

private:
    void setupConfig();

    void createDefaultObjectFunction();

    // ===== Objective helpers =====

    static bool isInside(const Box &item_bounding_box, const Box &box);

    static double positionScore(double min_x, double min_y);

    static double compactnessPenalty(double item_box_area, double box_area);

    static double gapBetweenShapesPenalty(const Shapes &merged_pile, const Item &item, double box_area);

    static double aspectPenalty(double item_bounding_box_width, double item_bounding_box_height);

    static double proximityBonus(const Shapes &merged_pile, double min_x, double min_y);
};

#endif // CONFIGS_NFP_CONFIG_HPP
