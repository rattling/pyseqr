# PySeqr

PySeqr is a Python library for sequence search and analysis.

## Installation

```bash
pip install pyseqr
```

## Usage

### Basic Example

```python  
from pyseqr import find_in_list

# Basic: Find all occurrences of [1, 2] in a target list
occurrences = find_in_list([1, 2], [1, 3, 2, 1, 2])
print(occurrences)  
# Example output: [[0, 2], [3, 4]]

# Using flags for gap logic:
# occurrence_gap = "any" or "non-negative"
# element_gap = "any" or "non-negative"
occurrences_with_flags = find_in_list(
    sublist=[1, 2],
    target=[1, 3, 1, 7, 2],
    occurrence_gap="any",
    element_gap="non-negative"
)
print(occurrences_with_flags)
# Example output: [[0, 4], [2, 4]]

```



### Handling Unhashable Objects

```python

from pyseqr.core import find_in_list

# If your sublist contains lists or dictionaries (normally unhashable),
# enable the "ensure_hashable" flag to convert them internally:
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

```python

from pyseqr.core import find_in_list

# If you have floating-point numbers and want to match them at a certain precision:
sublist = [1.111, 2.222, 3.333]
target  = [1.1111, 2.2222, 3.3333]

occurrences = find_in_list(
    sublist, target,
    float_precision=3
)
print(occurrences)
# Example output: [[0, 1, 2]]

```


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


