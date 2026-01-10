#include "djd_config.hpp"
#include <sstream>

DJDConfig::DJDConfig() {
    setupConfig();
}

void DJDConfig::setupConfig() {
    config.try_pairs = true;
    config.try_triplets = true;
    config.initial_fill_proportion = 0.35;
    config.waste_increment = 0.05;
}

void DJDConfig::reset() {
    config.try_reverse_order = false;
    config.try_pairs = true;
    config.try_triplets = true;
    config.initial_fill_proportion = 0.35;
    config.waste_increment = 0.05;
    config.allow_parallel = true;
    config.force_parallel = false;
}

std::string DJDConfig::str() const {
    std::ostringstream oss;
    oss << "DJDConfig(\n";
    oss << "try_reverse_order=" << (config.try_reverse_order ? "true" : "false") << ", \n";
    oss << "try_pairs=" << (config.try_pairs ? "true" : "false") << ", \n";
    oss << "try_triplets=" << (config.try_triplets ? "true" : "false") << ", \n";
    oss << "initial_fill_proportion=" << config.initial_fill_proportion << ", \n";
    oss << "waste_increment=" << config.waste_increment << ", ";
    oss << "allow_parallel=" << (config.allow_parallel ? "true" : "false") << ", \n";
    oss << "force_parallel=" << (config.force_parallel ? "true" : "false") << "\n";
    oss << ")";
    return oss.str();
}
