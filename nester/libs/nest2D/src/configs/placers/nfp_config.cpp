#include <libnest2d/libnest2d.hpp>

#include "nfp_config.hpp"


NfpConfig::NfpConfig() {
    setupConfig();
    createDefaultObjectFunction();
}

void NfpConfig::setupConfig() {
    config.alignment = Alignment::BOTTOM_LEFT;
    config.starting_point = Alignment::BOTTOM_LEFT;

    config.accuracy = 0.85f;

    config.explore_holes = true;

    config.parallel = true;
}

void NfpConfig::reset() {
    setupConfig();
    createDefaultObjectFunction();
}

void NfpConfig::createDefaultObjectFunction() {
    config.object_function = [](const Item &item, const Shapes &merged_pile, const Box &box) -> double {
        // === DECLARATIONS ===
        auto item_bounding_box = item.boundingBox();
        const auto minCorner = item_bounding_box.minCorner();

        const auto min_x = static_cast<double>(minCorner.X);
        const auto min_y = static_cast<double>(minCorner.Y);

        const auto item_bounding_box_width = static_cast<double>(item_bounding_box.width());
        const auto item_bounding_box_height = static_cast<double>(item_bounding_box.height());

        const auto box_width = static_cast<double>(box.width());
        const auto box_height = static_cast<double>(box.height());

        const double box_area = box_width * box_height;
        const double item_box_area = item_bounding_box_width * item_bounding_box_height;


        // === INSIDE CHECK ===
        if (!isInside(item_bounding_box, box)) return 1e20;

        // Initialize score
        double score = 0.0;

        // === SCORING COMPONENTS ===

        // 1. BOTTOM-LEFT PRIORITY (Primary driver)
        score += positionScore(min_x, min_y);

        // 2. BOUNDING BOX MINIMIZATION (Compactness Penalty)
        score += compactnessPenalty(item_box_area, box_area);

        // 3. GAP AREA MINIMIZATION (Encourage tight packing)
        score += gapBetweenShapesPenalty(merged_pile, item, box_area);

        // 4. ASPECT RATIO CONTROL
        score += aspectPenalty(item_bounding_box_width, item_bounding_box_height);

        // 5. PROXIMITY TO EXISTING SHAPES (Fill gaps between shapes)
        score += proximityBonus(merged_pile, min_x, min_y);

        return score;
    };
}

// ===== Objective helpers =====

bool NfpConfig::isInside(const Box &item_bounding_box, const Box &box) {
    return libnest2d::sl::isInside(item_bounding_box, box);
}

double NfpConfig::positionScore(const double min_x, const double min_y) {
    return min_y * 10000.0 + min_x * 100.0;
}

double NfpConfig::compactnessPenalty(const double item_box_area, const double box_area) {
    return item_box_area / box_area * 5000.0;
}

double NfpConfig::gapBetweenShapesPenalty(const Shapes &merged_pile, const Item &item, const double box_area) {
    double gap_penalty = 0.0;

    if (!merged_pile.empty()) {
        try {
            // Create temporary pile with current item
            const auto &item_shape = item.transformedShape();
            auto temp_pile = merged_pile;
            temp_pile.push_back(item_shape);

            // Calculate convex hull (tight boundary around all shapes)
            const auto convex_hull = libnest2d::shapelike::convexHull(temp_pile);
            const double hull_area = std::abs(libnest2d::shapelike::area(convex_hull));

            // Calculate items area
            double items_area = std::abs(libnest2d::shapelike::area(item_shape));
            for (const auto &shape: merged_pile) {
                items_area += std::abs(libnest2d::shapelike::area(shape));
            }

            // Gap = Hull area - Items area
            // Positions that minimize this gap get better scores
            const double gap_area = std::max(0.0, hull_area - items_area);
            gap_penalty = gap_area / box_area * 8000.0;
            // High weight for gap minimization
        } catch (...) {
            // If convex hull calculation fails, use moderate penalty
            gap_penalty = 1000.0;
        }
    }

    return gap_penalty;
}

double NfpConfig::aspectPenalty(const double item_bounding_box_width, const double item_bounding_box_height) {
    const double aspect_ratio = item_bounding_box_width > item_bounding_box_height
                                    ? item_bounding_box_width / item_bounding_box_height
                                    : item_bounding_box_height / item_bounding_box_width;

    return std::pow(aspect_ratio - 1.0, 2.0) * 200.0;
}

double NfpConfig::proximityBonus(const Shapes &merged_pile, const double min_x, const double min_y) {
    double proximity_bonus = 0.0;

    if (!merged_pile.empty()) {
        try {
            // Get bounding box of existing pile
            if (const auto &pile_shapes_vec = merged_pile; !pile_shapes_vec.empty()) {
                auto pile_bb = libnest2d::shapelike::boundingBox(pile_shapes_vec[0]);

                for (size_t i = 1; i < pile_shapes_vec.size(); ++i) {
                    auto shape_bb = libnest2d::shapelike::boundingBox(pile_shapes_vec[i]);
                    pile_bb = libnest2d::shapelike::boundingBox(pile_bb, shape_bb);
                }

                // Calculate distances to pile boundaries
                const auto pile_right = static_cast<double>(pile_bb.maxCorner().X);
                const auto pile_top = static_cast<double>(pile_bb.maxCorner().Y);

                const double dist_to_pile_x = std::abs(min_x - pile_right);
                const double dist_to_pile_y = std::abs(min_y - pile_top);

                // Reward positions close to existing shapes
                const double min_dist = std::min(dist_to_pile_x, dist_to_pile_y);
                proximity_bonus = -std::min(min_dist * 0.5, 500.0); // Cap the bonus
            }
        } catch (...) {
            proximity_bonus = 0.0;
        }
    }
    return proximity_bonus;
}
