import pytest

from pyseqr.core import find_in_list, ElementGap, OccurrenceGap


# Test cases for non-strategy-based function
basic_test_cases = [
    ([2, 3, 2], [1, 2, 3, 2, 4], [[1, 2, 3]]),  # Simple case
    ([1, 2, 3], [1, 2, 3], [[0, 1, 2]]),  # Sublist = target
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

gap_test_cases = [
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

mixed_param_test_cases = [
    # (sublist,             target,               ensure_hashable, use_custom_str, float_precision, occurrence_gap,        element_gap,        expected)
    # 1) Using unhashable data (set), ensuring hashable => single match
    (
        [1, {2, 3}, 4],
        [1, {2, 3}, 4],
        True,  # ensure_hashable
        False,  # use_custom_str
        None,  # float_precision
        "any",  # occurrence_gap
        "any",  # element_gap
        [[0, 1, 2]],  # expected match of indices [0,1,2]
    ),
    # 2) Using custom objects with string representation => must be in ascending index order
    (
        [CustomStrObject(1), CustomStrObject(2)],
        [CustomStrObject(1), CustomStrObject(2), CustomStrObject(1)],
        False,  # ensure_hashable
        True,  # use_custom_str
        None,  # float_precision
        OccurrenceGap.NON_NEGATIVE,  # enum usage
        ElementGap.NON_NEGATIVE,  # enum usage
        [[0, 1]],  # only the first two match in order => indices [0,1]
    ),
    # 3) Floats with precision => single contiguous match
    (
        [1.111, 2.222, 3.333],
        [1.1111, 2.2222, 3.3333],
        False,  # ensure_hashable
        False,  # use_custom_str
        3,  # float_precision
        "any",  # occurrence_gap
        "any",  # element_gap
        [[0, 1, 2]],
    ),
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
def test_find_in_list_use_custom_str(sublist, target, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        # Ensure 'expected' is a valid exception type
        with pytest.raises(expected):
            find_in_list(sublist, target, use_custom_str=True)
    else:
        # Test the function output normally
        result = find_in_list(
            sublist,
            target,
            use_custom_str=True,
            float_precision=None,
        )
        assert result == expected


@pytest.mark.parametrize(
    "sublist, target, expected, precision", float_precision_test_cases
)
def test_find_in_list_float_precision(sublist, target, expected, precision):
    result = find_in_list(sublist, target, float_precision=precision)
    assert result == expected


@pytest.mark.parametrize(
    "sublist, target, occurrence_gap, element_gap, expected", gap_test_cases
)
def test_find_in_list_gaps(sublist, target, occurrence_gap, element_gap, expected):
    result = find_in_list(
        sublist,
        target,
        occurrence_gap=occurrence_gap,
        element_gap=element_gap,
    )
    assert result == expected


def test_invalid_gap_args():
    with pytest.raises(ValueError):
        find_in_list([1], [1, 2], occurrence_gap="invalid-gap")
    with pytest.raises(ValueError):
        find_in_list([1], [1, 2], element_gap="also-invalid")


# A simple custom class with a string representation
class CustomStrObject:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"CustomStrObject({self.value})"


@pytest.mark.parametrize(
    "sublist, target, ensure_hashable, use_custom_str, float_precision, occurrence_gap, element_gap, expected",
    mixed_param_test_cases,
)
def test_find_in_list_mixed_params(
    sublist,
    target,
    ensure_hashable,
    use_custom_str,
    float_precision,
    occurrence_gap,
    element_gap,
    expected,
):
    """
    Test find_in_list with various combinations of parameters:
    - ensure_hashable (bool)
    - use_custom_str (bool)
    - float_precision (int or None)
    - occurrence_gap (OccurrenceGap enum or str)
    - element_gap (ElementGap enum or str)
    """
    result = find_in_list(
        sublist=sublist,
        target=target,
        ensure_hashable=ensure_hashable,
        use_custom_str=use_custom_str,
        float_precision=float_precision,
        occurrence_gap=occurrence_gap,
        element_gap=element_gap,
    )
    assert result == expected
