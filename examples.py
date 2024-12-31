from pyseqr import find_in_list

#  Find all occurrences of [1, 2] in a target list
sublist = [1, 2]
target = [2, 2, 1, 2, 1]
occurrences = find_in_list(sublist, target)
print(occurrences)
# Example output: [[2,0], [4, 1]]
# Note that the occurrences can be overlapping and the elements in any order

# If we set occurrence_gap to non-negative, we rule out overlapping occurrences
occurrences_with_flags = find_in_list(
    sublist=sublist,
    target=target,
    occurrence_gap="non-negative",
)
print(occurrences_with_flags)
# Example output: [[2,0], [4,3]]

# If we also set element gap to non-negative, we ensure strict ascending order
occurrences_with_flags = find_in_list(
    sublist=sublist,
    target=target,
    occurrence_gap="non-negative",
    element_gap="non-negative",
)
print(occurrences_with_flags)
# Example output: [[2,3]]

# We can use any hashable type as elements and elements can be nested
occurrences_with_flags = find_in_list(
    sublist=["foo", ("bar", "baz"), (1, 2)],
    target=["foo", ("bar", "baz"), (1, 2), "foo", ("bar", "baz"), (1, 2)],
)
print(occurrences_with_flags)
# Example output: [[0, 1,2], [3, 4,5]]

# We can attempt to hash unhashable types such as a list by converting them to hashables (tuple in this case)
occurrences_with_flags = find_in_list(
    sublist=["foo", ["bar", "baz"], (1, 2)],
    target=["foo", ["bar", "baz"], (1, 2), "foo", ["bar", "baz"], (1, 2)],
    ensure_hashable=True,
)
print(occurrences_with_flags)
# Example output: [[0, 1,2], [3, 4,5]]


# We can use your own custom __str__ method for elements that are or contain custom objects
class CustomStrObject:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"CustomStrObject({self.value})"


occurrences_with_flags = find_in_list(
    sublist=[CustomStrObject(1), CustomStrObject(2)],
    target=[CustomStrObject(1), CustomStrObject(2), CustomStrObject(1)],
    use_custom_str=True,
)
print(occurrences_with_flags)
# Example output: [[0, 1]]
