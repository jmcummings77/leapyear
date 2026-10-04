"""Leap-year benchmarks over start <= year < finish, in ascending order."""

import time
import statistics
import argparse
import json
from functools import wraps

times = {}

def timing(f):
    @wraps(f)
    def wrap(*args):
        time1 = time.perf_counter()
        ret = f(*args)
        time2 = time.perf_counter()
        if f.__name__ not in times:
            times[f.__name__] = []
        times[f.__name__].append((time2 - time1) * 1000.0)
        return ret
    return wrap


@timing
def code_golf(start, finish):
    y=(start+3)//4-1
    while y<(finish-1)//4:y+=1;1>y%25<y%4 or print(y*4)

@timing
def leap_bit(start, finish):
    [print(y) for y in range(start, finish) if (not (y & 3)) and (y % 25 or (4 > y & 15))]

@timing
def no_optimizations(start, finish):
    for year in range(start, finish):
        is_divisible_by_4 = year % 4 == 0
        is_divisible_by_100 = year % 100 == 0
        is_divisible_by_400 = year % 400 == 0
        if is_divisible_by_4 and (not is_divisible_by_100 or is_divisible_by_400):
            print(year)


# one optimization
@timing
def pull_up_printing(start, finish):
    result = []
    for year in range(start, finish):
        is_divisible_by_4 = year % 4 == 0
        is_divisible_by_100 = year % 100 == 0
        is_divisible_by_400 = year % 400 == 0
        if is_divisible_by_4 and (not is_divisible_by_100 or is_divisible_by_400):
            result.append(year)
    print(*result)


@timing
def reduced_modulos(start, finish):
    for year in range(start, finish):
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            print(year)


@timing
def counter(start, finish):
    four_counter = start % 4
    hundred_counter = start % 100
    four_hundred_counter = start % 400
    for year in range(start, finish):
        if four_counter == 0 and (hundred_counter != 0 or four_hundred_counter == 0):
            print(year)
        four_counter += 1
        hundred_counter += 1
        four_hundred_counter += 1
        if four_counter == 4:
            four_counter = 0
        if hundred_counter == 100:
            hundred_counter = 0
        if four_hundred_counter == 400:
            four_hundred_counter = 0


@timing
def count_by_four(start, finish):
    while start % 4 != 0:
        start += 1
    for year in range(start, finish, 4):
        is_divisible_by_100 = year % 100 == 0
        is_divisible_by_400 = year % 400 == 0
        if not is_divisible_by_100 or is_divisible_by_400:
            print(year)


# pull up (no) print + second optimization
@timing
def no_print_reduced_modulos(start, finish):
    result = []
    for year in range(start, finish):
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            result.append(year)
    return result

@timing
def no_print_counter(start, finish):
    result = []
    four_counter = start % 4
    hundred_counter = start % 100
    four_hundred_counter = start % 400
    for year in range(start, finish):
        if four_counter == 0 and (hundred_counter != 0 or four_hundred_counter == 0):
            result.append(year)
        four_counter += 1
        hundred_counter += 1
        four_hundred_counter += 1
        if four_counter == 4:
            four_counter = 0
        if hundred_counter == 100:
            hundred_counter = 0
        if four_hundred_counter == 400:
            four_hundred_counter = 0
    return result


@timing
def no_print_count_by_four(start, finish):
    result = []
    while start % 4 != 0:
        start += 1
    for year in range(start, finish, 4):
        is_divisible_by_100 = year % 100 == 0
        is_divisible_by_400 = year % 400 == 0
        if not is_divisible_by_100 or is_divisible_by_400:
            result.append(year)
    return result


# fully optimized
@timing
def leap_bit_no_print(start, finish):
    result = []
    mod = start % 4
    if mod != 0:
        start += 4 - mod
    for year in range(start, finish, 4):
        if year % 25 != 0 or year & 15 == 0:
            result.append(year)
    return result

@timing
def leap_year_modulos(start, finish):
    mod = start % 4
    if mod != 0:
        start += 4 - mod
    result = []
    for year in range(start, finish, 4):
        if year % 100 == 0:
            if year % 400 != 0:
                continue
        result.append(year)
    return result

@timing
def leap_year_counter(start, finish):
    result = []
    mod = start % 4
    if mod != 0:
        start += 4 - mod
    hundred_counter = (start % 100) // 4
    four_hundred_counter = (start % 400) // 100
    for year in range(start, finish, 4):
        if hundred_counter != 0 or four_hundred_counter == 0:
            result.append(year)
        hundred_counter += 1
        if hundred_counter == 25:
            hundred_counter = 0
            four_hundred_counter += 1
            if four_hundred_counter == 4:
                four_hundred_counter = 0
    return result


@timing
def leap_year_no_loops(start, finish):
    mod = start % 4
    if mod != 0:
        start += 4 - mod
    return list(filter(lambda x: x % 100 != 0 or x % 400 == 0,
                  range(start, finish, 4)))


@timing
def leap_year_sets(start, finish):
    fours = set(range(start + (-start) % 4, finish, 4))
    hundreds = set(range(start + (-start) % 100, finish, 100))
    four_hundreds = set(range(start + (-start) % 400, finish, 400))
    return sorted(fours.difference(hundreds.difference(four_hundreds)))


def evaluate_performance(start, finish, filename, iterations, run_print, warmups=0):
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    if warmups < 0:
        raise ValueError("warmups must be nonnegative")
    times.clear()
    for iteration in range(warmups + iterations):
        if run_print:
            no_optimizations(start, finish)
            pull_up_printing(start, finish)
            reduced_modulos(start, finish)
            counter(start, finish)
            count_by_four(start, finish)
            leap_bit(start, finish)
        leap_bit_no_print(start, finish)
        no_print_reduced_modulos(start, finish)
        no_print_counter(start, finish)
        no_print_count_by_four(start, finish)
        leap_year_modulos(start, finish)
        leap_year_counter(start, finish)
        leap_year_no_loops(start, finish)
        leap_year_sets(start, finish)
        if iteration < warmups:
            times.clear()
    results = {}
    for key, value in times.items():
        results[key] = statistics.mean(times[key])
    with open(filename, 'w') as out_file:
        out_file.write(json.dumps(results))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start', type=int, nargs='?', default=1582, help='Start year (inclusive).')
    parser.add_argument('-f', '--finish', type=int, nargs='?', default=2020, help='Stop year (exclusive).')
    parser.add_argument('-i', '--iterations', type=int, nargs='?', default=1, help='Number of iterations to run each function for profiling.')
    parser.add_argument('--warmups', type=int, default=0, help='Untimed warmup iterations before collecting samples.')
    parser.add_argument('-o', '--output', type=str, nargs='?', default="../results/python_results.json", help='File path for output.')
    parser.add_argument('-r', action='store_true', help='Flag indicating whether to run tests for methods that print to the terminal.')
    args = parser.parse_args()
    evaluate_performance(args.start, args.finish, args.output, args.iterations, args.r, args.warmups)
