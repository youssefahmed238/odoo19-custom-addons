#ifndef NESTER_RESULT_HPP
#define NESTER_RESULT_HPP
#pragma once

#include <libnest2d/libnest2d.hpp>
#include <vector>

using PackGroup = libnest2d::PackGroup;

using Item = libnest2d::Item;
using Items = std::vector<Item>;

using Output = std::vector<std::vector<Item>>;


class Result {
public:
    size_t bins;
    Output output;

    explicit Result(size_t bins, Items &items);
};

#endif // NESTER_RESULT_HPP