import time
import math
import statistics
import argparse
import json

import numpy as np

times = {}

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        if f.__name__ not in times:
            times[f.__name__] = []
        times[f.__name__].append((time2 - time1) * 1000.0)
        return ret
    return wrap


@timing
def code_golf(start, finish):
    y=450
    while y<600:y+=1;1>y%25<y%4or print(y*4)

@timing
def leap_bit(start, finish):
    [print(y) for y in range(start, finish + 1) if (not (y & 3)) and (y % 25 or (4 > y & 15))]

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
    while start % 4 != 0:
        start += 1
    hundred_counter = math.floor(((start % 100) / 4))
    four_hundred_counter = math.floor(((start % 400) / 100))
    for year in range(start, finish):
        if hundred_counter == 100:
            four_hundred_counter += 1
            hundred_counter = 1
            if four_hundred_counter == 4:
                print(year)
                four_hundred_counter = 0
        else:
            hundred_counter += 1
            print(year)


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
    while start % 4 != 0:
        start += 1
    hundred_counter = math.floor(((start % 100) / 4))
    four_hundred_counter = math.floor(((start % 400) / 100))
    for year in range(start, finish):
        if hundred_counter == 100:
            four_hundred_counter += 1
            hundred_counter = 1
            if four_hundred_counter == 4:
                result.append(year)
                four_hundred_counter = 0
        else:
            hundred_counter += 1
            result.append(year)
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
    finish += 4
    mod = start % 4
    if mod != 0:
        start += 4 - mod
    for year in range(start, finish + 4, 4):
        if year & 15 < 1:
            if year % 25:
                result.append(year)
        else:
            result.append(year)
    return result

@timing
def leap_year_modulos(start, finish):
    finish += 4
    mod = start % 4
    if mod != 0:
        start += 4 - mod
    result = []
    for year in range(start, finish + 4, 4):
        if year % 100 == 0:
            if year % 400 != 0:
                continue
        result.append(year)
    return result

@timing
def leap_year_counter(start, finish):
    result = []
    finish += 4
    mod = start % 4
    if mod != 0:
        start += 4 - mod
    hundred_counter = math.floor(((start % 100) / 4))
    four_hundred_counter = math.floor(((start % 400) / 100))
    for year in range(start, finish, 4):
        if hundred_counter == 25:
            four_hundred_counter += 1
            hundred_counter = 1
            if four_hundred_counter == 4:
                result.append(year)
                four_hundred_counter = 0
        else:
            hundred_counter += 1
            result.append(year)
    return result


@timing
def leap_year_no_loops(start, finish):
    finish += 4
    mod = start % 4
    if mod != 0:
        start += 4 - mod
    return list(filter(lambda x: x % 100 != 0 or x % 400 == 0,
                  range(start, finish, 4)))


@timing
def leap_year_sets(start, finish):
    result = []
    finish += 4
    mod = start % 4
    if mod != 0:
        start += 4 - mod
    hundred_counter = math.floor(((start % 100) / 4))
    four_hundred_counter = math.floor(((start % 400) / 100))
    for year in range(start, finish, 4):
        if hundred_counter == 25:
            four_hundred_counter += 1
            hundred_counter = 1
            if four_hundred_counter == 4:
                start = year
                break
        else:
            hundred_counter += 1
            result.append(year)
    result.extend(list(set(range(start, finish, 4)).difference(
            set(range(start, finish, 100)).difference(set(range(start, finish, 400))))))
    return result

@timing
def leap_year_additive(start, finish):
    finish += 4
    result = []
    base = [i for i in range(0, 401, 4) if i != 100 and i != 200 and i != 300]
    mod = start % 4
    if mod != 0:
        start += 4 - mod
    hundred_counter = math.floor(((start % 100) / 4))
    four_hundred_counter = math.floor(((start % 400) / 100))
    for year in range(start, finish, 4):
        if hundred_counter == 25:
            four_hundred_counter += 1
            hundred_counter = 1
            if four_hundred_counter == 4:
                start = year
                break
        else:
            hundred_counter += 1
            result.append(year)
    total = finish - start
    leftover = total % 400
    total -= leftover
    while start < finish - leftover:
        result.extend([i + start for i in base])
        start += 400
    if leftover:
        result.extend([i for i in range(finish - leftover, finish, 4) if i % 100 != 0])
    return result

@timing
def leap_year_additive2(start, finish):
    finish += 4
    result = []
    mod = start % 4
    if mod != 0:
        start += 4 - mod
    hundred_counter = math.floor(((start % 100) / 4))
    four_hundred_counter = math.floor(((start % 400) / 100))
    for year in range(start, finish, 4):
        if hundred_counter == 25:
            four_hundred_counter += 1
            hundred_counter = 1
            if four_hundred_counter == 4:
                start = year
                break
        else:
            hundred_counter += 1
            result.append(year)
    total = finish - start
    leftover = total % 400
    total -= leftover
    result.extend([i + j + start for i in range(0, 401, 4) if i != 100 and i != 200 and i != 300 for j in range(0, total, 400)])
    if leftover:
        result.extend([i for i in range(finish - leftover, finish, 4) if i % 100 != 0])
    return result

@timing
def leap_year_numpy(start, finish):
    finish += 4
    result = []
    base = np.array([i for i in range(0, 400, 4) if i != 100 and i != 200 and i != 300])
    mod = start % 4
    if mod != 0:
        start += 4 - mod
    hundred_counter = math.floor(((start % 100) / 4))
    four_hundred_counter = math.floor(((start % 400) / 100))
    for year in range(start, finish, 4):
        if hundred_counter == 25:
            four_hundred_counter += 1
            hundred_counter = 1
            if four_hundred_counter == 4:
                start = year
                break
        else:
            hundred_counter += 1
            result.append(year)
    total = finish - start
    leftover = total % 400
    total -= leftover
    temp = np.hstack((np.array(result), base + start))
    upperbound = finish - 400 - leftover
    while start < upperbound:
        start += 400
        temp = np.hstack((temp, base + start))
    if leftover:
        temp = np.hstack((temp, np.array([i for i in range(finish - leftover, finish, 4) if i % 100 != 0 or i % 400 == 0])))
    return temp


def evaluate_performance(start, finish, filename, iterations, run_print):
    for _ in range(iterations):
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
        # warning very slow
        # leap_year_numpy(start, finish)
        leap_year_additive(start, finish)
        leap_year_additive2(start, finish)
    results = {}
    for key, value in times.items():
        results[key] = statistics.mean(times[key])
    with open(filename, 'w') as out_file:
        out_file.write(json.dumps(results))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start', type=int, nargs='?', default=1582, help='Start year.')
    parser.add_argument('-f', '--finish', type=int, nargs='?', default=2020, help='Final year.')
    parser.add_argument('-i', '--iterations', type=int, nargs='?', default=1, help='Number of iterations to run each function for profiling.')
    parser.add_argument('-o', '--output', type=str, nargs='?', default="../results/python_results.json", help='File path for output.')
    parser.add_argument('-r', action='store_true', help='Flag indicating whether to run tests for methods that print to the terminal.')
    args = parser.parse_args()
    evaluate_performance(args.start, args.finish, args.output, args.iterations, args.r)
