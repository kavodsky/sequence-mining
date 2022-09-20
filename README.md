# Sequence-mining

## Description

This package implements SPAM algorithm described in the paper 
[**Sequential PAttern Mining using A Bitmap Representation**](https://www.cs.cornell.edu/johannes/papers/2002/kdd2002-spam.pdf) by 
Jay Ayres, Johannes Gehrke, Tomi Yiu, and Jason Flannick.

This package mostly translates a SPAM implementation written in Java by **Philippe Fournier-Viger**, which can be found 
in the next repository [**spmf**](https://github.com/pommedeterresautee/spmf). For more information about **spmf** implementation,
please, read the Web page [**Mining Frequent Sequential Patterns Using The CM-SPAM Algorithm**](https://www.philippe-fournier-viger.com/spmf/CM-SPAM.php)


## Installation

```shell
pip3 install sequence-mining
```

## Usage

```python
from sequence_mining.spam import SpamAlgo

# Input: List[List[List[int]]] or Sequences [ Sequence [Transaction[ids] ]]
# ids in a transaction are expected to be lexicographically sorted
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
# print mined sequences
print(algo.frequent_items)
```