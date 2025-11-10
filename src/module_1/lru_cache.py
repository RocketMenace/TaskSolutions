import unittest.mock
from functools import wraps
from typing import Callable


class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev: Node
        self.next: Node


class LinkedList:
    def __init__(self):
        self.head: Node = Node(key=None, value=None)
        self.tail: Node = Node(key=None, value=None)
        self.head.next = self.tail
        self.tail.prev = self.head
        self.head.prev = None

    def add_front(self, node: Node) -> None:
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def remove_node(self, node: Node) -> None:
        prev = node.prev
        next = node.next
        prev.next = next
        next.prev = prev

    def move_front(self, node: Node) -> None:
        self.remove_node(node)
        self.add_front(node)

    def remove_tail(self) -> Node | None:
        if self.tail.prev == self.head:
            return None
        lru_node = self.tail.prev
        self.remove_node(lru_node)
        return lru_node


def lru_cache(maxsize: int = 128):
    def create_wrapper(func: Callable, actual_maxsize: int):
        if actual_maxsize == 0:

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        cache: dict = dict()
        linked_list: LinkedList = LinkedList()

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))

            if key in cache:
                node = cache[key]
                linked_list.move_front(node)
                return node.value

            result = func(*args, **kwargs)

            if actual_maxsize is not None:
                if len(cache) >= actual_maxsize:
                    lru_node = linked_list.remove_tail()
                    if lru_node is not None:
                        cache.pop(lru_node.key)

            new_node = Node(key=key, value=result)
            linked_list.add_front(new_node)
            cache[key] = new_node

            return result

        return wrapper

    if isinstance(maxsize, int):
        if maxsize < 0:
            maxsize = 0
    elif callable(maxsize):
        func, maxsize = maxsize, 128
        wrapper = create_wrapper(func, maxsize)
        return wrapper
    elif maxsize is not None:
        raise TypeError("Expected first argument to be an integer, a callable, or None")

    def decorating_function(func: Callable):
        wrapper = create_wrapper(func, maxsize)
        return wrapper

    return decorating_function


@lru_cache
def sum(a: int, b: int) -> int:
    return a + b


@lru_cache
def sum_many(a: int, b: int, *, c: int, d: int) -> int:
    return a + b + c + d


@lru_cache(maxsize=3)
def multiply(a: int, b: int) -> int:
    return a * b


if __name__ == "__main__":
    assert sum(1, 2) == 3
    assert sum(3, 4) == 7

    assert multiply(1, 2) == 2
    assert multiply(3, 4) == 12

    assert sum_many(1, 2, c=3, d=4) == 10

    mocked_func = unittest.mock.Mock()
    mocked_func.side_effect = [1, 2, 3, 4]

    decorated = lru_cache(maxsize=2)(mocked_func)
    assert decorated(1, 2) == 1
    assert decorated(1, 2) == 1
    assert decorated(3, 4) == 2
    assert decorated(3, 4) == 2
    assert decorated(5, 6) == 3
    assert decorated(5, 6) == 3
    assert decorated(1, 2) == 4
    assert mocked_func.call_count == 4
