#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <cmath>

#include <libnest2d/libnest2d.hpp>

#include "../tools/printer_parts.hpp"
#include "../tools/svgtools.hpp"

namespace py = pybind11;
namespace pl = libnest2d::pointlike;

using Point = libnest2d::Point;
using Box = libnest2d::Box;
using Item = libnest2d::Item;
using PackGroup = libnest2d::PackGroup;
using SVGWriter = libnest2d::svg::SVGWriter<libnest2d::PolygonImpl>;

// placers
using NfpPlacer = libnest2d::NfpPlacer;
using BottomLeftPlacer = libnest2d::BottomLeftPlacer;

// selectors
using FirstFitSelection = libnest2d::FirstFitSelection;
using DJDHeuristic  = libnest2d::DJDHeuristic;

// Create custom enums
enum class PlacerType {
    NFP,
    BottomLeft
};

enum class SelectorType {
    FirstFit,
    DJDHeuristic
};

PYBIND11_MODULE(nest2D, m)
{
    m.doc() = "2D irregular bin packaging and nesting for python";

    py::enum_<PlacerType>(m, "PlacerType", "Type of placer algorithm")
        .value("NFP", PlacerType::NFP)
        .value("BottomLeft", PlacerType::BottomLeft)
        .export_values();

    py::enum_<SelectorType>(m, "SelectorType", "Type of selector algorithm")
        .value("FirstFit", SelectorType::FirstFit)
        .value("DJDHeuristic", SelectorType::DJDHeuristic)
        .export_values();

    py::class_<Point>(m, "Point", "2D Point")
        .def(py::init<int, int>(),  py::arg("x"), py::arg("y"))
        .def_property_readonly("x", [](const Point &p) { return p.X; })
        .def_property_readonly("y", [](const Point &p) { return p.Y; })
        .def("__repr__",
             [](const Point &p) {
                 std::string r("Point(");
                 r += boost::lexical_cast<std::string>(p.X);
                 r += ", ";
                 r += boost::lexical_cast<std::string>(p.Y);
                 r += ")";
                 return r;
             }
        )
        .def("__eq__",
            [](const Point &p, const Point & q) {
                return p == q;
            }
        );

    py::class_<Box>(m, "Box", "2D Box point pair")
        .def(py::init([](int x, int y) {
            return std::unique_ptr<Box>(new Box(x, y, {x/2, y/2}));
        }))
        ;

    py::class_<Item>(m, "Item", "An item to be placed on a bin.")
        .def(py::init<std::vector<Point>>())
        .def("__repr__",
             [](const Item &i) {
                 std::string r("Item(area: ");
                 r += boost::lexical_cast<std::string>(i.area());
                 r += ", bin_id: ";
                 r += boost::lexical_cast<std::string>(i.binId());
                 r += ", vertices: ";
                 r += boost::lexical_cast<std::string>(i.vertexCount());
                 r += ")";
                 return r;
             }
        )
        .def("area",
             [](const Item &i) {
                 return i.area();
             }
        )
        .def("get_vertices",
             [](const Item &i) {
                 std::vector<Point> vertices;
                 auto& shape = i.transformedShape();
                 auto contour = libnest2d::shapelike::contour(shape);
                 for(auto& vertex : contour) {
                     vertices.push_back(vertex);
                 }
                 return vertices;
             }
        )
        ;

    m.def("nest", [](std::vector<Item>& input, const Box& box,
                     PlacerType placer_type,
                     SelectorType selector_type,
                     double spacing) -> py::object {

        PackGroup pgrp;
        size_t bins = 0;

        auto distance = libnest2d::mm(spacing);

        // SORT ITEMS BY SIZE (largest first) for better packing
        std::sort(input.begin(), input.end(), [](const Item& a, const Item& b) {
            return a.area() > b.area();
        });

        if (placer_type == PlacerType::NFP) {
            if (selector_type == SelectorType::FirstFit) {
                libnest2d::NestConfig<NfpPlacer, FirstFitSelection> config;

                // CRITICAL: Set starting point to BOTTOM_LEFT
                config.placer_config.starting_point = NfpPlacer::Config::Alignment::BOTTOM_LEFT;
                config.placer_config.alignment = NfpPlacer::Config::Alignment::BOTTOM_LEFT;

                // Test only 0° rotation for most predictable results
                // Add 90° if you need rotated shapes
                for (int i = 0; i <= 0; i += 90) {
                    config.placer_config.rotations.push_back(i);
                }

                // MAXIMUM accuracy for cleanest placement
                config.placer_config.accuracy = 0.85f;  // Maximum precision
                config.placer_config.parallel = false;  // Sequential for consistency
                config.placer_config.explore_holes = true;

                // ADVANCED OBJECTIVE FUNCTION WITH PILE CONTEXT
                // This goes in your pybind_main.cpp for NFP + FirstFit config

               // USE THE NEW PILE-AWARE OBJECTIVE FUNCTION ⭐
                config.placer_config.object_function_with_pile =
                    [&box](const Item& item, const libnest2d::nfp::Shapes<libnest2d::PolygonImpl>& merged_pile) -> double {

                    auto ibb = item.boundingBox();
                    auto minCorner = ibb.minCorner();
                    auto maxCorner = ibb.maxCorner();

                    double x = static_cast<double>(minCorner.X);
                    double y = static_cast<double>(minCorner.Y);

                    // Boundary enforcement
                    if (x < 0 || y < 0 || maxCorner.X > box.width() || maxCorner.Y > box.height()) {
                        return 1e20;
                    }

                    // === SCORING COMPONENTS ===

                    // 1. BOTTOM-LEFT PRIORITY (Primary driver)
                    double position_score = y * 10000.0 + x * 100.0;

                    // 2. BOUNDING BOX MINIMIZATION
                    double bb_width = static_cast<double>(maxCorner.X);
                    double bb_height = static_cast<double>(maxCorner.Y);
                    double bb_area = bb_width * bb_height;
                    double box_area = static_cast<double>(box.width()) * static_cast<double>(box.height());
                    double compactness_penalty = (bb_area / box_area) * 5000.0;

                    // 3. GAP AREA MINIMIZATION ⭐ KEY FEATURE
                    // Calculates wasted space using convex hull method
                    double gap_penalty = 0.0;

                    if (!merged_pile.empty()) {
                        try {
                            // Create temporary pile with current item
                            auto item_shape = item.transformedShape();
                            auto temp_pile = merged_pile;
                            temp_pile.push_back(item_shape);

                            // Calculate convex hull (tight boundary around all shapes)
                            auto convex_hull = libnest2d::shapelike::convexHull(temp_pile);
                            double hull_area = std::abs(libnest2d::shapelike::area(convex_hull));

                            // Calculate actual occupied area
                            double occupied_area = std::abs(libnest2d::shapelike::area(item_shape));
                            for (const auto& shape : merged_pile) {
                                occupied_area += std::abs(libnest2d::shapelike::area(shape));
                            }

                            // Gap = Hull area - Occupied area
                            // Positions that minimize this gap get better scores
                            double gap_area = std::max(0.0, hull_area - occupied_area);
                            gap_penalty = (gap_area / box_area) * 8000.0;  // High weight for gap minimization

                        } catch (...) {
                            // If convex hull calculation fails, use moderate penalty
                            gap_penalty = 1000.0;
                        }
                    }

                    // 4. ASPECT RATIO CONTROL
                    double aspect_ratio = bb_width > bb_height ?
                                         bb_width / bb_height :
                                         bb_height / bb_width;
                    double aspect_penalty = std::pow(aspect_ratio - 1.0, 2.0) * 200.0;

                    // 5. PROXIMITY TO EXISTING SHAPES (Fill gaps between shapes)
                    double proximity_bonus = 0.0;

                    if (!merged_pile.empty()) {
                        try {
                            // Get bounding box of existing pile
                            auto pile_shapes_vec = merged_pile;
                            if (!pile_shapes_vec.empty()) {
                                auto pile_bb = libnest2d::shapelike::boundingBox(pile_shapes_vec[0]);

                                for (size_t i = 1; i < pile_shapes_vec.size(); ++i) {
                                    auto shape_bb = libnest2d::shapelike::boundingBox(pile_shapes_vec[i]);
                                    pile_bb = libnest2d::shapelike::boundingBox(pile_bb, shape_bb);
                                }

                                // Calculate distances to pile boundaries
                                double pile_right = static_cast<double>(pile_bb.maxCorner().X);
                                double pile_top = static_cast<double>(pile_bb.maxCorner().Y);

                                double dist_to_pile_x = std::abs(x - pile_right);
                                double dist_to_pile_y = std::abs(y - pile_top);

                                // Reward positions close to existing shapes
                                double min_dist = std::min(dist_to_pile_x, dist_to_pile_y);
                                proximity_bonus = -std::min(min_dist * 0.5, 500.0);  // Cap the bonus
                            }
                        } catch (...) {
                            proximity_bonus = 0.0;
                        }
                    }

                    // FINAL SCORE
                    // Lower = Better
                    double final_score = position_score + compactness_penalty + gap_penalty +
                                        aspect_penalty + proximity_bonus;

                    return final_score;
                };


                // ULTRA-STRICT BOTTOM-LEFT OBJECTIVE FUNCTION FOR SCALED INPUTS
                // This function enforces aggressive bottom-left row-by-row placement
//                config.placer_config.object_function = [&box](const Item& item) -> double {
//                    auto ibb = item.boundingBox();
//                    auto minCorner = ibb.minCorner();
//                    auto maxCorner = ibb.maxCorner();
//
//                    double x = static_cast<double>(minCorner.X);
//                    double y = static_cast<double>(minCorner.Y);
//
//                    // ABSOLUTE BOUNDARY ENFORCEMENT
//                    if (x < 0 || y < 0 || maxCorner.X > box.width() || maxCorner.Y > box.height()) {
//                        return 1e20;  // Massive penalty for out-of-bounds
//                    }
//
//                    // ULTRA-AGGRESSIVE ROW-BY-ROW SCORING
//                    // Y coordinate gets EXTREME dominance to force strict bottom-to-top filling
//                    double row_score = y * 100000.0;  // 100,000x weight on Y coordinate
//
//                    // X coordinate gets small weight for left-to-right within same row
//                    double col_score = x * 0.01;      // Tiny weight for column priority
//
//                    // MILLIMETER GRID SNAPPING BONUS
//                    double MM = 1000000.0;
//                    double x_mm = x / MM;
//                    double y_mm = y / MM;
//                    double x_frac = x_mm - std::floor(x_mm);
//                    double y_frac = y_mm - std::floor(y_mm);
//                    double snap_bonus = -(1.0 - x_frac) * 0.001 - (1.0 - y_frac) * 0.001;
//
//                    // Final score: Y dominates everything, X breaks ties, snapping cleans up
//                    return row_score + col_score + snap_bonus;
//                };



                bins = libnest2d::nest<NfpPlacer, FirstFitSelection>(
                    input, box, distance, config);

            } else if (selector_type == SelectorType::DJDHeuristic) {
                libnest2d::NestConfig<NfpPlacer, DJDHeuristic> config;

                // CRITICAL: Set starting point to BOTTOM_LEFT
                config.placer_config.starting_point = NfpPlacer::Config::Alignment::BOTTOM_LEFT;
                config.placer_config.alignment = NfpPlacer::Config::Alignment::BOTTOM_LEFT;

                for (int i = 0; i <= 0; i += 90) {
                    config.placer_config.rotations.push_back(i);
                }

                // MAXIMUM accuracy for cleanest placement
                config.placer_config.accuracy = 0.85f;  // Maximum precision
                config.placer_config.parallel = false;  // Sequential for consistency
                config.placer_config.explore_holes = true;

                // ADVANCED OBJECTIVE FUNCTION WITH PILE CONTEXT
                // This goes in your pybind_main.cpp for NFP + FirstFit config

               // USE THE NEW PILE-AWARE OBJECTIVE FUNCTION ⭐
                config.placer_config.object_function_with_pile =
                    [&box](const Item& item, const libnest2d::nfp::Shapes<libnest2d::PolygonImpl>& merged_pile) -> double {

                    auto ibb = item.boundingBox();
                    auto minCorner = ibb.minCorner();
                    auto maxCorner = ibb.maxCorner();

                    double x = static_cast<double>(minCorner.X);
                    double y = static_cast<double>(minCorner.Y);

                    // Boundary enforcement
                    if (x < 0 || y < 0 || maxCorner.X > box.width() || maxCorner.Y > box.height()) {
                        return 1e20;
                    }

                    // === SCORING COMPONENTS ===

                    // 1. BOTTOM-LEFT PRIORITY (Primary driver)
                    double position_score = y * 10000.0 + x * 100.0;

                    // 2. BOUNDING BOX MINIMIZATION
                    double bb_width = static_cast<double>(maxCorner.X);
                    double bb_height = static_cast<double>(maxCorner.Y);
                    double bb_area = bb_width * bb_height;
                    double box_area = static_cast<double>(box.width()) * static_cast<double>(box.height());
                    double compactness_penalty = (bb_area / box_area) * 5000.0;

                    // 3. GAP AREA MINIMIZATION ⭐ KEY FEATURE
                    // Calculates wasted space using convex hull method
                    double gap_penalty = 0.0;

                    if (!merged_pile.empty()) {
                        try {
                            // Create temporary pile with current item
                            auto item_shape = item.transformedShape();
                            auto temp_pile = merged_pile;
                            temp_pile.push_back(item_shape);

                            // Calculate convex hull (tight boundary around all shapes)
                            auto convex_hull = libnest2d::shapelike::convexHull(temp_pile);
                            double hull_area = std::abs(libnest2d::shapelike::area(convex_hull));

                            // Calculate actual occupied area
                            double occupied_area = std::abs(libnest2d::shapelike::area(item_shape));
                            for (const auto& shape : merged_pile) {
                                occupied_area += std::abs(libnest2d::shapelike::area(shape));
                            }

                            // Gap = Hull area - Occupied area
                            // Positions that minimize this gap get better scores
                            double gap_area = std::max(0.0, hull_area - occupied_area);
                            gap_penalty = (gap_area / box_area) * 8000.0;  // High weight for gap minimization

                        } catch (...) {
                            // If convex hull calculation fails, use moderate penalty
                            gap_penalty = 1000.0;
                        }
                    }

                    // 4. ASPECT RATIO CONTROL
                    double aspect_ratio = bb_width > bb_height ?
                                         bb_width / bb_height :
                                         bb_height / bb_width;
                    double aspect_penalty = std::pow(aspect_ratio - 1.0, 2.0) * 200.0;

                    // 5. PROXIMITY TO EXISTING SHAPES (Fill gaps between shapes)
                    double proximity_bonus = 0.0;

                    if (!merged_pile.empty()) {
                        try {
                            // Get bounding box of existing pile
                            auto pile_shapes_vec = merged_pile;
                            if (!pile_shapes_vec.empty()) {
                                auto pile_bb = libnest2d::shapelike::boundingBox(pile_shapes_vec[0]);

                                for (size_t i = 1; i < pile_shapes_vec.size(); ++i) {
                                    auto shape_bb = libnest2d::shapelike::boundingBox(pile_shapes_vec[i]);
                                    pile_bb = libnest2d::shapelike::boundingBox(pile_bb, shape_bb);
                                }

                                // Calculate distances to pile boundaries
                                double pile_right = static_cast<double>(pile_bb.maxCorner().X);
                                double pile_top = static_cast<double>(pile_bb.maxCorner().Y);

                                double dist_to_pile_x = std::abs(x - pile_right);
                                double dist_to_pile_y = std::abs(y - pile_top);

                                // Reward positions close to existing shapes
                                double min_dist = std::min(dist_to_pile_x, dist_to_pile_y);
                                proximity_bonus = -std::min(min_dist * 0.5, 500.0);  // Cap the bonus
                            }
                        } catch (...) {
                            proximity_bonus = 0.0;
                        }
                    }

                    // FINAL SCORE
                    // Lower = Better
                    double final_score = position_score + compactness_penalty + gap_penalty +
                                        aspect_penalty + proximity_bonus;

                    return final_score;
                };

                bins = libnest2d::nest<NfpPlacer, DJDHeuristic>(
                    input, box, distance, config);
            }
        } else if (placer_type == PlacerType::BottomLeft) {
            if (selector_type == SelectorType::FirstFit) {
                libnest2d::NestConfig<BottomLeftPlacer, FirstFitSelection> config;
                bins = libnest2d::nest<BottomLeftPlacer, FirstFitSelection>(
                    input, box, distance, config);

            } else if (selector_type == SelectorType::DJDHeuristic) {
                libnest2d::NestConfig<BottomLeftPlacer, DJDHeuristic> config;
                config.selector_config.try_pairs = true;
                config.selector_config.try_triplets = true;
                config.selector_config.initial_fill_proportion = 0.35;
                config.selector_config.waste_increment = 0.05;

                bins = libnest2d::nest<BottomLeftPlacer, DJDHeuristic>(
                    input, box, distance, config);
            }
        }

        pgrp = PackGroup(bins);
        for (Item &itm : input) {
            if (itm.binId() >= 0) pgrp[size_t(itm.binId())].emplace_back(itm);
        }

        return py::cast(pgrp);
    },
    py::arg("input"),
    py::arg("box"),
    py::arg("placer_type") = PlacerType::NFP,
    py::arg("selector_type") = SelectorType::FirstFit,
    py::arg("spacing") = 0.0,
    "Nest and pack items with strict bottom-left corner priority."
    );

    py::class_<SVGWriter>(m, "SVGWriter", "SVGWriter tools to write pack_group to SVG.")
        .def(py::init([]() {
            SVGWriter::Config conf;
            conf.mm_in_coord_units = libnest2d::mm();
            return std::unique_ptr<SVGWriter>(new SVGWriter(conf));
        }))
        .def("write_packgroup", [](SVGWriter & sw, const PackGroup & pgrp) {
            sw.setSize(Box(libnest2d::mm(250), libnest2d::mm(210)));
            sw.writePackGroup(pgrp);
        })
        .def("save", [](SVGWriter & sw) {
            sw.save("out");
        })
        .def("__repr__",
             [](const SVGWriter &sw) {
                 return std::string("SVGWriter()");
             }
        );
}