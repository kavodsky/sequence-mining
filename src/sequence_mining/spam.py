import sys
from math import ceil
from random import randint

from sequence_mining.prefix import Prefix
from sequence_mining.bitmap import Bitmap

"""
Vocabulary:
CID - customer id
SID - sequence id
TID - transaction id

Expected input:
{ list of itemsets sorted by tid}
items in itemsets are supposed to be sorted

List[List[int]] e.g. [[1], [2,4,9], [1,2], [2,3]]]

"""
from typing import List, Dict


class SpamAlgo:

    def __init__(self, min_sup_rel):
        self.vertical_db = {}
        self.last_bit_index = None
        self.sequences_size = None
        # relational minimal support
        self.min_sup_rel = min_sup_rel
        self.maximum_patter_length = sys.maxsize
        self.frequent_items = []

    def spam(self, sequences: List[List[List[int]]]):
        # Go through all sequences and calculate sequences sizes
        self.last_bit_index, self.sequences_size = self.calculate_sequences_sizes(sequences)
        self.build_vertical_db(sequences)
        self.min_sup = self.calculate_min_support()
        self.remove_not_frequent_items()
        self.recursive_dfs()

    def calculate_sequences_sizes(self, sequences: List[List[List[int]]]):
        bit_index = 0
        sequences_sizes = [bit_index]
        for sequence in sequences:
            bit_index += len(sequence)
            if sequence != sequences[-1]:
                sequences_sizes.append(bit_index)
        last_bit_index = bit_index - 1
        return last_bit_index, sequences_sizes

    def build_vertical_db(self, sequences: List[List[List[int]]]):
        for sid, sequence in enumerate(sequences):
            for tid, itemset in enumerate(sequence):
                for idx, item in enumerate(itemset):
                    bitmap_item = self.vertical_db.get(item)
                    if not bitmap_item:
                        bitmap_item = Bitmap(self.last_bit_index)
                        self.vertical_db[item] = bitmap_item
                    bitmap_item.register_bit(sid, tid, self.sequences_size)

    def calculate_min_support(self):
        min_sup = ceil(self.min_sup_rel * len(self.sequences_size))
        if not min_sup:
            min_sup = 1
        print(f'Min support {min_sup}')
        return min_sup

    def remove_not_frequent_items(self):
        keys = list(self.vertical_db.keys())
        for k in keys:
            if self.vertical_db[k].support < self.min_sup:
                del self.vertical_db[k]
        self.frequent_items.extend([k] for k in self.vertical_db.keys())

    def recursive_dfs(self):
        keys = list(self.vertical_db.keys())
        for k in keys:
            prefix = Prefix([k])
            self.dfs_pruning(prefix=prefix,
                             prefix_bitmap=self.vertical_db[k],
                             search_s_items=list(self.vertical_db.keys()),
                             search_i_items=list(self.vertical_db.keys()),
                             has_to_be_greater_than_for_i_step=k,
                             m=2)

    def dfs_pruning(self, prefix: Prefix, prefix_bitmap: Bitmap, search_s_items: List[int],
                    search_i_items: List[int], has_to_be_greater_than_for_i_step: int, m: int):
        s_temp, s_temp_bitmaps = self.perform_s_step(prefix, prefix_bitmap, search_s_items)
        for idx, item in enumerate(s_temp):
            prefix_s_step = prefix.clone_sequence()
            prefix_s_step.add_item_set([item])
            new_bitmap = s_temp_bitmaps[idx]
            # FIX: maximum_patter_length
            self.frequent_items.append(prefix_s_step.itemsets)
            if self.maximum_patter_length > m:
                self.dfs_pruning(prefix_s_step, new_bitmap, s_temp, s_temp, item, m + 1)

        i_temp, i_temp_bitmaps = self.perform_i_step(prefix,
                                                     prefix_bitmap,
                                                     search_i_items,
                                                     has_to_be_greater_than_for_i_step)
        for idx, item in enumerate(i_temp):
            # create the new prefix
            prefix_i_step = prefix.clone_sequence()
            prefix_i_step.itemsets[len(prefix_i_step) - 1].append(item)
            # create new Bitmap
            new_bitmap = i_temp_bitmaps[idx]
            if self.maximum_patter_length > m:
                self.dfs_pruning(prefix_i_step, new_bitmap, s_temp, i_temp, item, m + 1)

    def perform_s_step(self, prefix, prefix_bitmap, frequent_items):
        s_temp: List[int] = []
        s_temp_bitmaps: List[Bitmap] = []
        for i, k in enumerate(frequent_items):
            # print(f'searching combination {prefix.itemsets} + {k}')
            new_bitmap = prefix_bitmap.create_new_bitmap_s_step(bitmap=self.vertical_db[k],
                                                                sequences_size=self.sequences_size,
                                                                last_bit_index=self.last_bit_index)
            # print(f'new bitmap support {new_bitmap.support}')
            if new_bitmap.support >= self.min_sup:
                s_temp.append(k)
                s_temp_bitmaps.append(new_bitmap)
        return s_temp, s_temp_bitmaps

    def perform_i_step(self, prefix, prefix_bitmap, frequent_items: List[int], has_to_be_greater_than_for_i_step: int):
        i_temp: List[int] = []
        i_temp_bitmaps: List[Bitmap] = []
        for item in frequent_items:
            if item > has_to_be_greater_than_for_i_step:
                new_bitmap = prefix_bitmap.create_new_bitmap_i_step(self.vertical_db[item],
                                                                    self.sequences_size,
                                                                    self.last_bit_index)
                if new_bitmap.support >= self.min_sup:
                    i_temp.append(item)
                    i_temp_bitmaps.append(new_bitmap)
        return i_temp, i_temp_bitmaps


def generate_sequence():
    itemsets_in_sequence = randint(3, 10)
    sequence = [[] for _ in range(itemsets_in_sequence)]
    for i in range(itemsets_in_sequence):
        items_in_itemset = randint(1, 10)
        # generate items
        itemset = sequence[i]
        for j in range(items_in_itemset):
            item = randint(0, 20)
            if item not in itemset:
                itemset.append(item)
        itemset.sort()
    return sequence


if __name__ == '__main__':
    # sequence = generate_sequence()
    # SpamAlgo().create_bitmap(sequence)
    # l = [generate_sequence() for _ in range(4)]
    sequences = [
        [[0, 2, 10, 13, 14, 15, 18, 20], [2, 7, 12, 15, 17, 19], [6, 12, 19], [0, 3, 4, 6, 15], [1, 3, 10, 13, 15],
         [8, 10], [4, 8, 9, 10]],
        [[9, 10, 17], [4], [0, 1, 2, 3, 4, 5, 12, 13, 19], [0, 1, 5, 10, 17, 18], [4, 7, 12], [2, 8, 9, 13, 15, 16, 19],
         [3, 5, 6, 9, 11, 13, 18, 19], [2, 5, 9, 10, 13, 16, 20], [2, 3, 6]],
        [[0, 9, 10, 13, 14, 19, 20], [0, 1, 9, 15, 17], [1, 7, 11, 12, 15, 20], [7, 9, 10, 11, 14, 18], [0, 10],
         [5, 13, 15], [1, 5, 9, 15], [1, 5, 7, 8, 19], [2, 6, 11, 14, 16], [3, 10, 11, 12]],
        [[15], [6, 9, 10, 12, 13, 15, 16], [13, 16]]
    ]
    algo = SpamAlgo(0.7)
    algo.spam(sequences)
    print(algo.frequent_items)
