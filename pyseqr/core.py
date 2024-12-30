from typing import List, Sequence, Any, Optional
from decimal import Decimal, getcontext, InvalidOperation, ROUND_HALF_UP
import bisect
from abc import ABC, abstractmethod
from enum import Enum


class OccurrenceGap(Enum):
    ANY = "any"
    NON_NEGATIVE = "non-negative"


class ElementGap(Enum):
    ANY = "any"
    NON_NEGATIVE = "non-negative"


class OccurrenceGapStrategy(ABC):
    """Abstract base class for occurrence gap strategies."""

    @abstractmethod
    def filter_indices(self, indices: List[int], last_occurrence_max: int) -> List[int]:
        """
        Given a list of candidate indices for an element and
        the maximum index used in the previous occurrence,
        return the filtered list of valid indices.

        Args:
            indices (List[int]): The list of candidate indices.
            last_occurrence_max (int): The maximum index used in the previous occurrence.

        Returns:
            List[int]: The filtered list of valid indices.
        """
        pass


class AnyOccurrenceGapStrategy(OccurrenceGapStrategy):
    def filter_indices(self, indices, last_occurrence_max):
        """Return the indices unmodified (any overlap is allowed)"""
        return indices


class NonNegativeOccurrenceGapStrategy(OccurrenceGapStrategy):
    def filter_indices(self, indices, last_occurrence_max):
        """If "non-negative", remove all indices <= last_occurrence_max."""
        # If "non-negative", remove all indices <= last_occurrence_max
        # (i.e., no overlap with previous occurrence)
        pos = bisect.bisect_right(indices, last_occurrence_max)
        return indices[pos:]


class ElementGapStrategy(ABC):
    """Abstract base class for element gap strategies."""

    @abstractmethod
    def pick_index(
        self, indices: List[int], current_occurrence: List[int]
    ) -> Optional[int]:
        """
        Given a list of candidate indices and the current_occurrence so far,
        pick and remove (pop) one valid index to match the sublist element.

        Returns the picked index or None if no valid index exists.

        Args:
            indices (List[int]): The list of candidate indices.
            current_occurrence (List[int]): The current occurrence so far.

        Returns:
            Optional[int]: The picked index or None if no valid index exists.
        """
        pass


class AnyOrderElementGapStrategy(ElementGapStrategy):
    def pick_index(self, indices, current_occurrence):
        """Order is unimportant, we pick the first index element is found."""
        return indices.pop(0) if indices else None


class OrderedElementGapStrategy(ElementGapStrategy):
    def pick_index(self, indices, current_occurrence):
        """Enforces strictly ordered elements for each occurrence."""
        last_index = current_occurrence[-1] if current_occurrence else -1
        # We need the first index in `indices` that is > last_index
        pos = bisect.bisect_right(indices, last_index)
        if pos < len(indices):
            return indices.pop(pos)
        else:
            return None


OCCURRENCE_GAP_STRATEGIES = {
    OccurrenceGap.ANY: AnyOccurrenceGapStrategy(),
    OccurrenceGap.NON_NEGATIVE: NonNegativeOccurrenceGapStrategy(),
}

ELEMENT_GAP_STRATEGIES = {
    ElementGap.ANY: AnyOrderElementGapStrategy(),
    ElementGap.NON_NEGATIVE: OrderedElementGapStrategy(),
}


def validate_inputs(sublist: Sequence[Any], target: Sequence[Any]) -> None:
    """Validate the input lists for find_in_list function.

    Args:
        sublist (Sequence[Any]): The sublist to search for.
        target (Sequence[Any]): The target list to search within.

    Raises:
        TypeError: If either sublist or target is not a list or tuple.
        ValueError: If either sublist or target is empty, or if sublist is longer than target.
    """
    if not isinstance(sublist, (list, tuple)) or not isinstance(target, (list, tuple)):
        raise TypeError("Both sublist and target must be of type list or tuple.")
    if not sublist or not target:
        raise ValueError("Neither sublist nor target can be empty.")
    if len(sublist) > len(target):
        raise ValueError("Sublist cannot be longer than target.")


def round_as_decimal(num, decimal_places=2):
    """Round a number to a specified number of decimal places.

    Args:
        num (float): The number to round.
        decimal_places (int, optional): The number of decimal places to round to. Defaults to 2.

    Returns:
        Decimal: The rounded number as a Decimal object.

    Raises:
        InvalidOperation: If the rounding operation is invalid.

    https://stackoverflow.com/questions/8868985/problems-with-rounding-decimals-python solution by kamalgill
    """
    getcontext().prec = decimal_places + 1
    precision = "1.{places}".format(places="0" * decimal_places)
    return Decimal(str(num)).quantize(Decimal(precision), rounding=ROUND_HALF_UP)


def make_hashable(
    element: Any, ensure_hashable, use_custom_str, float_precision=None
) -> Any:
    # write docstring in google format for this function:
    """Convert an element to a hashable type.

    Args:
        element (Any): The element to convert.
        ensure_hashable (bool): Whether to ensure the element is hashable.
        use_custom_str (bool): Whether to use a custom string representation for the element.
        float_precision (int, optional): The number of decimal places to round floats to. Defaults to None.

    Returns:
        Any: The hashable version of the element.
    """

    def _process(sub_element: Any) -> Any:
        """Helper to avoid repeating the same arguments for recursive calls."""
        return make_hashable(
            sub_element, ensure_hashable, use_custom_str, float_precision
        )

    if float_precision and isinstance(element, float):
        try:
            getcontext().prec = float_precision
            return round_as_decimal(element, float_precision)
        except (InvalidOperation, ValueError):
            raise ValueError("Invalid float precision.")

    if ensure_hashable:
        if isinstance(element, list):
            return tuple(_process(e) for e in element)
        elif isinstance(element, dict):
            return frozenset((k, make_hashable(v)) for k, v in element.items())
        elif isinstance(element, set):
            return frozenset(_process(e) for e in element)

    if use_custom_str:
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
    """Remove all indices <= max_index from the list.

    Args:
        indices (List[int]): The list of indices to filter.
        max_index (int): The maximum index allowed.

    Returns:
        List[int]: The filtered list of indices.

    Examples:
        >>> remove_overlaps([1, 2, 3, 4, 5], 3)
        [4, 5]

        >>> remove_overlaps([1, 2, 3, 4, 5], 5)
        []
    """
    # Find the first index where the value is greater than max_index
    pos = bisect.bisect_right(indices, max_index)
    return indices[pos:]


def find_in_list(
    sublist: Sequence[Any],
    target: Sequence[Any],
    ensure_hashable: bool = False,
    use_custom_str: bool = False,
    float_precision: int = None,
    occurrence_gap: OccurrenceGap = OccurrenceGap.ANY,
    element_gap: ElementGap = ElementGap.ANY,
) -> List[List[int]]:
    """
    Finds all occurrences of a sublist in a target list with specified gaps.
    Each occurrence is a list of indices in `target` that map to the elements in `sublist`.

    Args:
        sublist (Sequence[Any]): The sublist to look for.
        target (Sequence[Any]): The list to search in.
        ensure_hashable (bool): Convert unhashable elements to hashable.
        use_custom_str (bool): Use a custom string representation for custom objects.
        float_precision (int, optional): Round floats to this number of decimal places.
        occurrence_gap (OccurrenceGap): Strategy for how occurrences may overlap.
        element_gap (ElementGap): Strategy for how elements must appear (ordered or any).

    Returns:
        List[List[int]]: A list of index-lists for each matching occurrence. Empty list if none.


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
    if ensure_hashable or use_custom_str or float_precision:
        sublist = [
            make_hashable(
                e,
                ensure_hashable=ensure_hashable,
                use_custom_str=use_custom_str,
                float_precision=float_precision,
            )
            for e in sublist
        ]
        target = [
            make_hashable(
                e,
                ensure_hashable=ensure_hashable,
                use_custom_str=use_custom_str,
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

    # Build the strategies

    def get_occurrence_gap_strategy(flag: OccurrenceGap | str) -> OccurrenceGapStrategy:
        """
        Convert the given flag (either an OccurrenceGap enum member or a string)
        into the appropriate OccurrenceGapStrategy.
        """
        if isinstance(flag, str):
            # Convert string to enum (this will raise ValueError if the string is invalid)
            flag = OccurrenceGap(flag)
            # e.g. OccurrenceGap("any") -> OccurrenceGap.ANY
            #     OccurrenceGap("non-negative") -> OccurrenceGap.NON_NEGATIVE

        # Now 'flag' is guaranteed to be an OccurrenceGap enum
        return OCCURRENCE_GAP_STRATEGIES[flag]

    def get_element_gap_strategy(flag: ElementGap | str) -> ElementGapStrategy:
        """
        Convert the given flag (either an ElementGap enum or a string)
        into the appropriate ElementGapStrategy.
        """
        if isinstance(flag, str):
            flag = ElementGap(flag)
        return ELEMENT_GAP_STRATEGIES[flag]

    occ_strategy = get_occurrence_gap_strategy(occurrence_gap)
    elem_strategy = get_element_gap_strategy(element_gap)

    occurrences = []
    last_occurrence_max = -1

    while True:
        current_occurrence = []
        for element in sublist:
            # 1) Filter indices for occurrence gaps
            # This ensures we skip all indices that would violate the "overlap" rule
            index_map[element] = occ_strategy.filter_indices(
                index_map[element], last_occurrence_max
            )
            # 2) Pick the next index for the element based on the "ordered" or "any" logic
            found_index = elem_strategy.pick_index(
                index_map[element], current_occurrence
            )

            if found_index is None:
                return occurrences  # no more valid matches
            current_occurrence.append(found_index)

        occurrences.append(current_occurrence)
        last_occurrence_max = max(current_occurrence)
