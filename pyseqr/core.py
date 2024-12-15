from typing import List, Sequence, Any


def validate_inputs(sublist: Sequence[Any], target: Sequence[Any]) -> None:
    if not isinstance(sublist, (list, tuple)) or not isinstance(target, (list, tuple)):
        raise TypeError("Both sublist and target must be of type list or tuple.")
    if not sublist or not target:
        raise ValueError("Neither sublist nor target can be empty.")
    if len(sublist) > len(target):
        raise ValueError("Sublist cannot be longer than target.")


def make_hashable(element: Any, convert_unhashable, custom_objects) -> Any:
    """
    Convert certain unhashable elements to hashable types recursively.
    """
    if convert_unhashable:
        if isinstance(element, list):
            return tuple(make_hashable(e) for e in element)
        elif isinstance(element, dict):
            return frozenset((k, make_hashable(v)) for k, v in element.items())
        elif isinstance(element, set):
            return frozenset(make_hashable(e) for e in element)
    if custom_objects:
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


def find_in_list(
    sublist: Sequence[Any],
    target: Sequence[Any],
    convert_unhashable: bool = False,
    custom_objects: bool = False,
) -> List[List[int]]:
    """
    Find all occurrences of the `sublist` in the `target` in O(n) time where n is target list size.

    This function returns a list of occurrences where each occurrence is represented
    by a list of indices corresponding to the elements of the `sublist` in `target`.

    Parameters:
        sublist (List[int]): The list of elements to find in `target`.
        target (List[int]): The list of elements to search in.
        convert_unhashable (bool): If True, convert unhashable elements to hashable types.
        custom_objects (bool): If True, use the string representation of custom objects.
            NOTE: Objects with a default string representation that are not the same instance will not match.
            The user can define a custom string representation for their objects to ensure matches on equivalent instances.

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
    if convert_unhashable or custom_objects:
        sublist = [
            make_hashable(
                e, convert_unhashable=convert_unhashable, custom_objects=custom_objects
            )
            for e in sublist
        ]
        target = [
            make_hashable(
                e, convert_unhashable=convert_unhashable, custom_objects=custom_objects
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
    while True:
        current_occurrence = []
        for element in sublist:
            if index_map[element]:
                current_occurrence.append(index_map[element].pop(0))
            else:
                return occurrences
        occurrences.append(current_occurrence)
