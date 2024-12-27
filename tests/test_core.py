import pytest

from pyseqr.core import find_in_list

# Test cases for non-strategy-based function
basic_test_cases = [
    ([2, 3, 2], [1, 2, 3, 2, 4], [[1, 2, 3]]),  # Simple case
    ([2, 3, 2], [3, 2, 6, 2, 4], [[1, 0, 3]]),  # Non-contiguous matches
    ([1], [3, 1, 1, 5], [[1], [2]]),  # Single element repeating
    ([7, 9, 5], [1, 2, 3, 4], []),  # No matches
    ([1], [1, 1, 1, 1], [[0], [1], [2], [3]]),  # Single element repeating
    ([1, 2], [1, 1, 1, 2], [[0, 3]]),  # Non-contiguous matches
    ([1, 2, 1], [1, 2, 1, 1, 2, 1], [[0, 1, 2], [3, 4, 5]]),  # Repeating patterns
    (["abc", "gor", "c"], ["abc", "b", "gor", "d", "c"], [[0, 2, 4]]),  # Simple case
    (
        ["abc", "gor", "c"],
        ["abc", "b", "gor", "d", "c", "abc", "gor", "c"],
        [[0, 2, 4], [5, 6, 7]],
    ),  # Repeating patterns
    (
        ["abc", "gor", "c"],
        ["abc", "b", "gor", "d", "abc", "gor", "abc", "gor", "abc", "gor"],
        [],
    ),  # No match
]

exception_test_cases = [
    (None, [1, 2, 3], TypeError),  # Non-sequence sublist
    ([1, 2], "abx", TypeError),  # Non-sequence target
    ([1, 2], [1], ValueError),  # Sublist larger than target
    ([], [1, 2, 3], ValueError),  # Empty sublist
    ([1], [], ValueError),  # Empty target
]


# Custom class with a string representation
class CustomStrObject:
    def __init__(self, value):
        self.value = value

    # def __eq__(self, other):
    #     return isinstance(other, CustomStrObject) and self.value == other.value

    def __str__(self):
        return f"CustomStrObject({self.value})"


# Custom class without a string representation (they will just use default __str__ method)
class NoStrObject:
    def __init__(self, value):
        self.value = value


# Test cases
custom_object_test_cases = [
    # Custom objects with string representations
    (
        [CustomStrObject(1), CustomStrObject(2)],
        [CustomStrObject(1), CustomStrObject(2), CustomStrObject(1)],
        [[0, 1]],
    ),
    # Custom objects without string representations
    (
        [NoStrObject(1), NoStrObject(2)],
        [NoStrObject(1), NoStrObject(2), NoStrObject(1)],
        [],  # using default __str__ method, objects are different instances and will not match
    ),
]

# unhashable_test_cases, e.g. lists, dictionaries etc. that we will attempt to convert to hashable types and proceed with the function
unhashable_test_cases = [
    ([1, [2, 3], 4], [1, [2, 3], 4], [[0]]),  # Nested list
    ([1, {2: 3}, 4], [1, {2: 3}, 4], [[0]]),  # Dictionary
]

# Test cases for float_precision
float_precision_test_cases = [
    (
        [1.111, 2.222, 3.333],
        [1.1111, 2.2222, 3.3333],
        [],
        None,
    ),  # Default precision
    ([1.111, 2.222, 3.333], [1.1111, 2.2222, 3.3333], [[0, 1, 2]], 3),  # Precision 3
    ([1.111, 2.222, 3.333], [1.1111, 2.2222, 3.3333], [], 4),  # Precision 4
]


@pytest.mark.parametrize("sublist, target, expected", basic_test_cases)
def test_find_in_list(sublist, target, expected):
    result = find_in_list(sublist, target)
    assert result == expected


@pytest.mark.parametrize("sublist, target, expected_exception", exception_test_cases)
def test_find_in_list_exceptions(sublist, target, expected_exception):
    with pytest.raises(expected_exception):
        find_in_list(sublist, target)


@pytest.mark.parametrize("sublist, target, expected", custom_object_test_cases)
def test_find_in_list_custom_objects(sublist, target, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        # Ensure 'expected' is a valid exception type
        with pytest.raises(expected):
            find_in_list(sublist, target, custom_objects=True)
    else:
        # Test the function output normally
        result = find_in_list(
            sublist,
            target,
            custom_objects_flag=True,
            float_precision=None,
        )
        assert result == expected


@pytest.mark.parametrize(
    "sublist, target, expected, precision", float_precision_test_cases
)
def test_find_in_list_float_precision(sublist, target, expected, precision):
    result = find_in_list(sublist, target, float_precision=precision)
    assert result == expected


flag_test_cases = [
    (
        [1, 2],
        [2, 2, 2, 3, 2, 1, 1, 1, 7, 1, 2],
        "any",
        "any",
        [[5, 0], [6, 1], [7, 2], [9, 4]],
    ),  #  any occurrence gap, any element gap
    (
        [1, 2],
        [2, 2, 2, 3, 2, 1, 1, 1, 7, 1, 2],
        "non-negative",
        "any",
        [[5, 0], [6, 10]],
    ),  #  no negative occurrence gap (overlap), any element gap
    (
        [1, 2],
        [1, 3, 1, 7, 2, 8, 2, 9, 1, 2],
        "any",
        "non-negative",
        [[0, 4], [2, 6], [8, 9]],
    ),  #  any occurrence gap, no negative element gap (i.e ordered)
    (
        [1, 2],
        [1, 3, 1, 7, 2, 8, 2, 9, 1, 2],
        "non-negative",
        "non-negative",
        [[0, 4], [8, 9]],
    ),  #  no negative occurrence gap (overlap),, no negative element gap (i.e ordered)
]


@pytest.mark.parametrize(
    "sublist, target, occurrence_gap_flag, element_gap_flag, expected", flag_test_cases
)
def test_find_in_list_flags(
    sublist, target, occurrence_gap_flag, element_gap_flag, expected
):
    result = find_in_list(
        sublist,
        target,
        occurrence_gap_flag=occurrence_gap_flag,
        element_gap_flag=element_gap_flag,
    )
    assert result == expected
