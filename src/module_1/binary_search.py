def binary_search(array: list[int], number: int) -> int:
    arr = sorted(array)
    start = 0
    end = len(arr) - 1
    while start <= end:
        mid = (start + end) // 2
        guess = arr[mid]
        if guess == number:
            return mid
        if guess > number:
            end = mid - 1
        if guess < number:
            start = mid + 1
    return -1


def binary_search_recursive(array: list[int], number: int, start: int, end: int) -> int:
    if start > end:
        return -1
    mid: int = (start + end) // 2
    guess = array[mid]
    if guess == number:
        return mid
    if guess > number:
        return binary_search_recursive(array, number, start=start, end=mid - 1)
    return binary_search_recursive(array, number, start=mid + 1, end=end)
