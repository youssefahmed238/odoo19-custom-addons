#include "result.hpp"

Result::Result(const size_t bins, Items &items) : bins(bins) {
    auto pack_group = PackGroup(bins);

    for (Item& item: items) {
        if (const int item_bin_id = item.binId(); item_bin_id >= 0) {
            pack_group[static_cast<size_t>(item_bin_id)].emplace_back(item);
        }
    }

    output.resize(bins);

    for (size_t b = 0; b < bins; b++) {
        output[b].reserve(pack_group[b].size());
        for (const auto& item_ref : pack_group[b]) {
            output[b].push_back(item_ref.get());
        }
    }
}