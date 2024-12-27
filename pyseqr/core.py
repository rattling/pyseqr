from typing import List, Sequence, Any
from decimal import Decimal, getcontext, InvalidOperation, ROUND_HALF_UP
import bisect


def validate_inputs(sublist: Sequence[Any], target: Sequence[Any]) -> None:
    if not isinstance(sublist, (list, tuple)) or not isinstance(target, (list, tuple)):
        raise TypeError("Both sublist and target must be of type list or tuple.")
    if not sublist or not target:
        raise ValueError("Neither sublist nor target can be empty.")
    if len(sublist) > len(target):
        raise ValueError("Sublist cannot be longer than target.")


def round_as_decimal(num, decimal_places=2):
    """Round a number to a given precision and return as a Decimal

    Arguments:
    :param num: number
    :type num: int, float, decimal, or str
    :returns: Rounded Decimal
    :rtype: decimal.Decimal

    https://stackoverflow.com/questions/8868985/problems-with-rounding-decimals-python solution by kamalgill
    """

    getcontext().prec = decimal_places + 1
    precision = "1.{places}".format(places="0" * decimal_places)
    return Decimal(str(num)).quantize(Decimal(precision), rounding=ROUND_HALF_UP)


def make_hashable(
    element: Any, convert_unhashable_flag, custom_objects_flag, float_precision=None
) -> Any:
    """
    Convert certain unhashable elements to hashable types recursively.
    """
    if float_precision and isinstance(element, float):
        try:
            getcontext().prec = float_precision
            return round_as_decimal(element, float_precision)
        except (InvalidOperation, ValueError):
            raise ValueError("Invalid float precision.")

    if convert_unhashable_flag:
        if isinstance(element, list):
            return tuple(make_hashable(e) for e in element)
        elif isinstance(element, dict):
            return frozenset((k, make_hashable(v)) for k, v in element.items())
        elif isinstance(element, set):
            return frozenset(make_hashable(e) for e in element)

    if custom_objects_flag:
        # Check if the element is a custom object (i.e., not a built-in type)
        if type(element).__module__ != "builtins":
            # Ensure the custom object has a string representation
            if hasattr(element, "__str__") and callable(getattr(element, "__str__")):
                return str(element)
            else:
                raise TypeError(
                    f"Custom object of type {type(element).__name__} lacks a string representation."
                )

    return element


def remove_overlaps(indices, max_index):
    # Find the first index where the value is greater than max_index
    pos = bisect.bisect_right(indices, max_index)
    return indices[pos:]


def find_ordered_element(indices, max_index):
    # Find the first index where the value is greater than max_index
    pos = bisect.bisect_right(indices, max_index)
    # pop the value at pos and return it
    if pos < len(indices):
        return indices.pop(pos)
    else:
        return None


def find_in_list(
    sublist: Sequence[Any],
    target: Sequence[Any],
    convert_unhashable_flag: bool = False,
    custom_objects_flag: bool = False,
    float_precision: int = None,
    occurrence_gap_flag: str = "any",
    element_gap_flag: str = "any",
) -> List[List[int]]:
    """
    Find all occurrences of the `sublist` in the `target` in O(n) time where n is target list size.

    This function returns a list of occurrences where each occurrence is represented
    by a list of indices corresponding to the elements of the `sublist` in `target`.

    Parameters:
        sublist (List[int]): The list of elements to find in `target`.
        target (List[int]): The list of elements to search in.
        convert_unhashable_flag (bool): If True, convert unhashable elements to hashable types.
        custom_objects_flag (bool): If True, use the string representation of custom objects.
            NOTE: Objects with a default string representation that are not the same instance will not match.
            The user can define a custom string representation for their objects to ensure matches on equivalent instances.
        float_precision (int): If provided, round floating-point numbers to this precision for better matching.
        occurrence_gap_flag (str): If "any", allow occurrences of the sublist to overlap.
            If "non-negative", ensure that there is no overlap
        element_gap_flag (str): If "any", allow elements of the sublist to be in any order.
            If "non-negative", ensure that the elements are in the same order as the sublist.

    Returns:
        List[List[int]]: A list of lists, where each sublist represents the indices of
        one occurrence of the `sublist` in `target`. Returns an empty list if any
        element of `sublist` is not found in `target` or if no occurrences exist.

    Examples:
        >>> find_in_list([2, 3, 2], [1, 2, 3, 2, 4])
        [[1, 2, 3]]

        >>> find_in_list([2, 3, 2], [3, 2, 6, 2, 4])
        []

        >>> find_in_list([1], [3, 1, 1, 5])
        [[1], [2]]

        >>> find_in_list([2, 3, 2], [1, 2, 3, 2, 4, 2, 3, 2])
        [[1, 2, 3], [5, 6, 7]]
    """

    validate_inputs(sublist, target)

    # Convert elements to hashable types
    if convert_unhashable_flag or custom_objects_flag or float_precision:
        sublist = [
            make_hashable(
                e,
                convert_unhashable_flag=convert_unhashable_flag,
                custom_objects_flag=custom_objects_flag,
                float_precision=float_precision,
            )
            for e in sublist
        ]
        target = [
            make_hashable(
                e,
                convert_unhashable_flag=convert_unhashable_flag,
                custom_objects_flag=custom_objects_flag,
                float_precision=float_precision,
            )
            for e in target
        ]

    try:
        # Attempt to create the index_map
        index_map = {element: [] for element in set(sublist)}
    except TypeError as e:
        raise ValueError("All elements in sublist must be hashable.") from e

    # Populate the index_map with indices of matching elements in the target
    for index, value in enumerate(target):
        if value in index_map:
            index_map[value].append(index)

    # Check if any element in the sublist has no matches in the target
    if any(not indices for indices in index_map.values()):
        return []

    occurrences = []
    max_index = -1
    while True:
        current_occurrence = []
        for element in sublist:
            found_index = None
            if index_map[element]:
                if occurrence_gap_flag == "non-negative":  # overlap logic
                    index_map[element] = remove_overlaps(
                        index_map[element], max_index
                    )  # overlap logic
                if element_gap_flag == "non-negative":
                    found_index = find_ordered_element(
                        index_map[element],
                        current_occurrence[-1] if current_occurrence else -1,
                    )
                else:
                    found_index = (
                        index_map[element].pop(0) if index_map[element] else None
                    )
            if found_index is not None:
                current_occurrence.append(found_index)
            else:
                return occurrences
        occurrences.append(current_occurrence)
        max_index = max(current_occurrence)
