import logging
from bisect import bisect
from typing import List

from bitarray import bitarray


logger = logging.getLogger()


class Bitmap:

    def __init__(self, last_bit_index):
        self.bitmap = None
        self.support = 0
        # For calculating the support more efficiently
        # we keep some information:
        # the sid of the last sequence inserted in that bitmap that contains a bit set to 1
        self.last_sid = -1
        self.set_bit_array(last_bit_index + 1)

    def set_bit_array(self, last_bit_index):
        self.bitmap = bitarray(last_bit_index)
        self.bitmap.setall(0)

    def set_bit(self, index):
        # print(f'Setting index: {index} on bitmap {self.bitmap} with length: {len(self.bitmap)}')
        self.bitmap[index] = True

    def register_bit(self, sid: int, tid: int, sequences_sizes: List[int]):
        '''
        Determins right index in bitmap and sets bit to 1
        :param sid: sequence id
        :param tid: itemset id
        :param sequences_sizes: List[int] list of cumulative sequences sizes
        :return: None
        '''
        # Get itemset index
        pos: int = sequences_sizes[sid] + tid
        self.bitmap[pos] = True

        if sid != self.last_sid:
            self.support += 1

        self.last_sid = sid

    def create_new_bitmap_s_step(self, bitmap: 'Bitmap', sequences_size, last_bit_index):
        new_bitmap = Bitmap(last_bit_index)
        # get set bits on this bimap
        set_bits = self.bitmap.search(1)
        set_bits_candidate = bitmap.bitmap.search(1)
        # must be only on first bits of every sequence
        first_bits = self.get_first_set_bits_of_every_sequence(set_bits, sequences_size, last_bit_index)
        for set_bit in first_bits:
            idx = bisect(set_bits_candidate, set_bit) - 1
            sid: int = self.bit_to_sid(set_bit, sequences_size)
            last_bit_of_sid: int = self.last_bit_of_sid(sid, sequences_size, last_bit_index)
            # Get only sequence (SID) bits
            sequence_bits = [bit for bit in set_bits_candidate[idx+1:] if bit <= last_bit_of_sid]
            match = False
            for next_bit in sequence_bits:
                new_bitmap.set_bit(next_bit)
                match = True

            if match:
                if sid != last_bit_of_sid:
                    new_bitmap.support += 1
        return new_bitmap

    def create_new_bitmap_i_step(self, bitmap: 'Bitmap', sequences_size, last_bit_index):
        new_bitmap = Bitmap(last_bit_index)
        set_bits = self.bitmap.search(1)
        # if both bits are TRUE
        for bit_idx in set_bits:
            if bitmap.bitmap[bit_idx]:
                new_bitmap.bitmap[bit_idx] = True

                sid: int = self.bit_to_sid(bit_idx, sequences_size)
                if sid != new_bitmap.last_sid:
                    new_bitmap.support += 1
                new_bitmap.last_sid = sid
        #  logical AND
        new_bitmap.bitmap = new_bitmap.bitmap & bitmap.bitmap

        return new_bitmap

    def bit_to_sid(self, bit, sequences_size):
        # Bisect starts from index 1
        index = bisect(sequences_size, bit) - 1
        if index < 0:
            index = 0
        return index

    def last_bit_of_sid(self, sid, sequence_size, last_bit_index):
        if sid + 1 >= len(sequence_size):
            return last_bit_index
        return sequence_size[sid + 1] - 1

    def get_first_set_bits_of_every_sequence(self, set_bits, sequences_size, last_bit_index):
        sid: int = -1
        first_bits = []
        for idx, bit in enumerate(set_bits):
            bit_sid = self.bit_to_sid(bit, sequences_size)
            if bit_sid != sid:
                first_bits.append(bit)
                sid = bit_sid
        return first_bits

    def __str__(self):
        return str(self.bitmap.tolist())

