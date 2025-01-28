# PySeqr

PySeqr is a Python library for sequence search and analysis. It provides a simple and efficient way to find all occurrences of a sublist in a target list.

PySeqr supports unordered, ordered, overlapping and non-overlapping occurrences. It also allows you to specify the gap between occurrences and elements. PySeqr can handle custom objects and floating-point numbers with a specified precision.

Note that all sequence elements must be hashable for matching. Custom objects will match on their string representation. If you wish to match on a unhashable built-in Python data type (e.g. list, dictionary, set), you can set the `ensure_hashable` flag to `True`.

## Requirements

- Python 3.7+ (tested on 3.7, 3.8, 3.9, 3.10, 3.11)

## Performance

The `find_in_list` function operates with a time complexity of **O(m + n + k * m * log n)**, where:
- `m` is the length of the `sublist`.
- `n` is the length of the `target` list.
- `k` is the number of occurrences found.

While not strictly linear, the implementation is optimized for efficiency using hashing and binary search, making it performant for large datasets with reasonable `m` and `k`. i.e. it approaches O(n) for the common set of tasks where we look for a relatively small set of items, sparsely distributed in a larger list.



## Installation
```bash
pip install pyseqr
```
## Basic Usage
Find all occurrences of a sublist in a target list. By default un-ordered and overlapping occurrences are allowed.
```python  
from pyseqr import find_in_list

sublist = [1, 2]
target = [2, 2, 1, 2, 1]
occurrences = find_in_list(sublist, target)
print(occurrences)
# Example output: [[2,0], [4, 1]]
```


## Advanced Usage
### Ensure Occurrences Do Not Overlap

- **occurrence_gap="non-negative"**: Disallow overlapping occurrences, so no indices are reused between occurrences.

```python
sublist = [1, 2]
target = [2, 2, 1, 2, 1]
occurrences_with_flags = find_in_list(
    sublist=sublist,
    target=target,
    occurrence_gap="non-negative",
)
print(occurrences_with_flags)
# Example output: [[2,0], [4,3]]
```
### Ensure Elements Are Ordered

- **element_gap="non-negative"**: Enforce strict ascending index order for each element in `sublist`, so the second element is always found after the first in `target`.

```python
sublist = [1, 2]
target = [2, 2, 1, 2, 1]
occurrences_with_flags = find_in_list(
    sublist=sublist,
    target=target,
    occurrence_gap="non-negative",
    element_gap="non-negative",
)
print(occurrences_with_flags)
# Example output: [[2,3]]
```
### Make Elements Hashable for Matching
E.g. lists -> tuples, dictionaries -> frozensets, sets -> frozensets
```python
from pyseqr.core import find_in_list

sublist = [1, [2, 3], 4]
target  = [1, [2, 3], 4]
occurrences = find_in_list(
    sublist, target,
    ensure_hashable=True
)
print(occurrences)
# Example output: [[0, 1, 2]]
```
### Handling Custom Objects
Use the `use_custom_str` flag to compare objects based on their string representation.
```python
class CustomStrObject:
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return f"CustomStrObject({self.value})"

from pyseqr.core import find_in_list

obj1 = CustomStrObject(1)
obj2 = CustomStrObject(2)

result = find_in_list(
    sublist=[obj1, obj2],
    target=[obj1, obj2, obj1],
    use_custom_str=True
)
print(result)
# Example output: [[0, 1]]

```
### Float Precision Matching
If you have floating-point numbers and want to match them at a certain precision:
```python
from pyseqr.core import find_in_list

sublist = [1.111, 2.222, 3.333]
target  = [1.1111, 2.2222, 3.3333]

occurrences = find_in_list(
    sublist, target,
    float_precision=3
)
print(occurrences)
# Example output: [[0, 1, 2]]

```

For more usage examples and advanced cases, see [tests/test_core.py](https://github.com/your-username/pyseqr/blob/main/tests/test_core.py) in the repository.



## Development Setup
Use `pipenv` to install dependencies:
```bash
pipenv install --dev
pipenv shell
```
Then you can run tests using `pytest`:
```bash
pytest
```

## Contributing
1. Fork and clone this repository.
2. Create a feature branch for your changes.
3. Install dependencies using Pipenv.
4. Run tests (pytest) and ensure everything passes.
5. Submit a Pull Request describing your changes.

## License

PySeqr is licensed under the [Apache License 2.0](LICENSE).


