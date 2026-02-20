"""
Custom QuickSort Algorithm Implementation
No built-in sort functions used - implements QuickSort from scratch
"""

from typing import List, Dict, Any, Tuple


class QuickSortAlgorithm:
    """
    Custom QuickSort implementation with performance tracking
    Time Complexity: O(n log n) average, O(n²) worst case
    Space Complexity: O(log n) for recursion stack
    """

    def __init__(self):
        self.comparisons = 0
        self.swaps = 0

    def sort(self, arr: List[Dict[str, Any]], key: str, reverse: bool = False) -> Tuple[List[Dict[str, Any]], int, int]:
        """
        Sort array using QuickSort algorithm

        Args:
            arr: List of dictionaries to sort
            key: Key to sort by
            reverse: True for descending order

        Returns:
            Tuple of (sorted_array, comparisons_count, swaps_count)
        """
        self.comparisons = 0
        self.swaps = 0

        if len(arr) <= 1:
            return arr, 0, 0

        # Create a copy to avoid modifying original
        arr_copy = arr.copy()

        # Perform QuickSort
        self._quicksort(arr_copy, 0, len(arr_copy) - 1, key, reverse)

        return arr_copy, self.comparisons, self.swaps

    def _quicksort(self, arr: List[Dict[str, Any]], low: int, high: int, key: str, reverse: bool):
        """
        Recursive QuickSort implementation
        """
        if low < high:
            # Partition the array and get pivot index
            pivot_index = self._partition(arr, low, high, key, reverse)

            # Recursively sort elements before and after partition
            self._quicksort(arr, low, pivot_index - 1, key, reverse)
            self._quicksort(arr, pivot_index + 1, high, key, reverse)

    def _partition(self, arr: List[Dict[str, Any]], low: int, high: int, key: str, reverse: bool) -> int:
        """
        Partition array around pivot element
        """
        # Choose the last element as pivot
        pivot_value = arr[high][key]

        # Index of smaller element
        i = low - 1

        for j in range(low, high):
            self.comparisons += 1

            # Compare current element with pivot
            if reverse:
                # Descending order: current > pivot
                should_swap = arr[j][key] > pivot_value
            else:
                # Ascending order: current < pivot
                should_swap = arr[j][key] < pivot_value

            if should_swap:
                i += 1
                # Swap elements
                arr[i], arr[j] = arr[j], arr[i]
                self.swaps += 1

        # Place pivot in correct position
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        self.swaps += 1

        return i + 1


# Create global instance
sorter = QuickSortAlgorithm()


def quicksort(arr: List[Dict[str, Any]], key: str, reverse: bool = False) -> Tuple[List[Dict[str, Any]], int, int]:
    """
    Public function to sort array using QuickSort

    Args:
        arr: List of dictionaries to sort
        key: Dictionary key to sort by
        reverse: True for descending order, False for ascending

    Returns:
        Tuple of (sorted_array, comparisons_count, swaps_count)
    """
    return sorter.sort(arr, key, reverse)
