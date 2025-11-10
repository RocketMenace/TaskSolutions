import argparse
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import Process, Queue, cpu_count
from multiprocessing.pool import Pool
from pathlib import Path
from typing import Any


def generate_data(number: int) -> list[int]:
    return [random.randint(1, 1000) for _ in range(number)]


def process_number(number: int) -> dict[str, Any]:
    is_prime = True
    if number < 2:
        is_prime = False
    elif number == 2:
        is_prime = True
    elif number % 2 == 0:
        is_prime = False
    else:
        sqrt_n = int(number**0.5) + 1
        for i in range(3, sqrt_n, 2):
            if number % i == 0:
                is_prime = False
                break

    sum_of_squares = sum(int(digit) ** 2 for digit in str(number))

    factorial_sum = 0
    temp = number
    while temp > 0:
        digit = temp % 10
        fact = 1
        for i in range(1, digit + 1):
            fact *= i
        factorial_sum += fact
        temp //= 10

    return {
        "number": number,
        "is_prime": is_prime,
        "sum_of_squares": sum_of_squares,
        "factorial_sum": factorial_sum,
    }


def process_sequential(data: list[int]) -> list[dict[str, Any]]:
    return [process_number(number) for number in data]


def process_with_thread_pool(
    data: list[int], max_workers: int | None = None
) -> list[dict[str, Any]]:
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_number = {executor.submit(process_number, num): num for num in data}
        for future in as_completed(future_to_number):
            results.append(future.result())
    return results


def process_with_process_pool(data: list[int]) -> list[dict[str, Any]]:
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(process_number, data)
    return results


def worker_process(input_queue: Queue, output_queue: Queue) -> None:
    while True:
        number = input_queue.get()
        if number is None:
            break
        result = process_number(number)
        output_queue.put(result)


def process_with_separate_processes(data: list[int]) -> list[dict[str, Any]]:
    num_workers = cpu_count()
    input_queue = Queue()
    output_queue = Queue()

    processes = []
    for _ in range(num_workers):
        p = Process(target=worker_process, args=(input_queue, output_queue))
        p.start()
        processes.append(p)

    for number in data:
        input_queue.put(number)

    for _ in range(num_workers):
        input_queue.put(None)

    results = []
    for _ in range(len(data)):
        results.append(output_queue.get())

    for p in processes:
        p.join()

    return results


def save_results(results: list[dict[str, Any]], filename: str | Path) -> None:
    output_path = Path(filename)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def compare_performance(
    data: list[int], output_file: str | Path = "results.json"
) -> dict[str, Any]:
    results = {}
    times = {}

    print(f"Обработка {len(data)} чисел...")
    print("-" * 60)

    # Однопоточная обработка
    print("Запуск однопоточного варианта...")
    start_time = time.time()
    sequential_results = process_sequential(data)
    sequential_time = time.time() - start_time
    times["sequential"] = sequential_time
    results["sequential"] = sequential_results
    print(f"Однопоточный вариант: {sequential_time:.2f} секунд")

    # Вариант А: ThreadPoolExecutor
    print("Запуск варианта А (ThreadPoolExecutor)...")
    start_time = time.time()
    thread_results = process_with_thread_pool(data)
    thread_time = time.time() - start_time
    times["thread_pool"] = thread_time
    results["thread_pool"] = thread_results
    print(f"Вариант А (ThreadPoolExecutor): {thread_time:.2f} секунд")

    # Вариант Б: multiprocessing.Pool
    print("Запуск варианта Б (multiprocessing.Pool)...")
    start_time = time.time()
    process_pool_results = process_with_process_pool(data)
    process_pool_time = time.time() - start_time
    times["process_pool"] = process_pool_time
    results["process_pool"] = process_pool_results
    print(f"Вариант Б (multiprocessing.Pool): {process_pool_time:.2f} секунд")

    # Вариант В: Отдельные процессы с очередями
    print("Запуск варианта В (отдельные процессы с очередями)...")
    start_time = time.time()
    separate_processes_results = process_with_separate_processes(data)
    separate_processes_time = time.time() - start_time
    times["separate_processes"] = separate_processes_time
    results["separate_processes"] = separate_processes_results
    print(f"Вариант В (отдельные процессы): {separate_processes_time:.2f} секунд")

    print("-" * 60)
    print("\nСравнение производительности:")
    print(f"{'Метод':<30} {'Время (сек)':<15} {'Ускорение':<15}")
    print("-" * 60)

    baseline = sequential_time
    for method, elapsed_time in times.items():
        speedup = baseline / elapsed_time if elapsed_time > 0 else 0
        method_name = {
            "sequential": "Однопоточный",
            "thread_pool": "ThreadPoolExecutor",
            "process_pool": "multiprocessing.Pool",
            "separate_processes": "Отдельные процессы",
        }.get(method, method)
        print(f"{method_name:<30} {elapsed_time:<15.2f} {speedup:<15.2f}x")

    output_data = {
        "performance": times,
        "results": results["process_pool"],  # Сохраняем результаты одного из вариантов
        "data_size": len(data),
        "cpu_count": cpu_count(),
    }

    save_results(output_data, output_file)
    print(f"\nРезультаты сохранены в файл: {output_file}")

    return output_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Сравнение производительности различных методов параллельной обработки данных"
    )
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        default=10000,
        help="Количество случайных чисел для обработки (по умолчанию: 10000)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="multiprocessing_results.json",
        help="Имя выходного файла (по умолчанию: multiprocessing_results.json)",
    )

    args = parser.parse_args()

    n = args.number
    print(f"Генерация {n} случайных чисел...")
    print(f"Количество CPU: {cpu_count()}")
    data = generate_data(n)

    compare_performance(data, args.output)
