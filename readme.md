# Leap Year William

![leapyyearwilliam](https://pixel.nymag.com/imgs/daily/vulture/2016/02/29/29-leap-day-30-rock-1.w710.h473.2x.jpg)

Alternative leap-year algorithms in Python, Go, JavaScript, and C#, with correctness tests and a reproducible benchmark runner.

## Range contract

Every implementation uses **start inclusive, finish exclusive**: `start <= year < finish`. Equal or reversed bounds produce no years. Methods return or print the same ascending sequence without duplicates, using the Gregorian rule: divisible by 4, except centuries not divisible by 400.

For example, `[1582, 1582)` is empty, `[1596, 1605)` contains `1596, 1600, 1604`, and `[1696, 1705)` contains `1696, 1704`.

The common strategies scan every year, replace repeated modulos with counters, step by four, or combine those optimizations. Additional implementations use bitwise operations, sets, filtering, or LINQ. Printing variants are checked for correctness but excluded from the comparison below.

## Run the checks

Requirements: Python 3.9+, Go 1.20+, Node.js 20+, and the .NET 8 SDK. All tests and benchmark programs use their language's standard library; no Python, npm, Go, or NuGet packages need installing.

From the repository root:

```sh
python3 -m unittest Python.test_leap_year -v
(cd Go && go test ./...)
node --test JavaScript/leapYear.test.js
dotnet run --project C_Sharp.Tests/C_Sharp.Tests.csproj --configuration Release
```

The suites check every starting phase of the 400-year Gregorian cycle, century boundaries, empty/reversed ranges, printing, timing precision, iteration counts, and warmup exclusion. They cover all 15 Python functions and all 11 methods in each of Go, JavaScript, and C#.

## Reproduce the comparison

```sh
./runAll.sh
# Choose a range and sample counts, or save a new published snapshot:
./runAll.sh --start 1582 --finish 1000000 --iterations 10 --warmups 3 --output benchmarks/latest.json
```

The runner executes every correctness suite first and stops on failure. It builds Go and C# (Release), then runs the languages sequentially with the same range and sample counts. Each method gets three in-process warmups followed by ten measured calls by default. Printing is disabled. Reported values are arithmetic means in milliseconds, including result construction and any garbage collection during the call; compilation and process startup are excluded. Python, Go, and JavaScript use monotonic timers; C# records `Elapsed.TotalMilliseconds` as a `double`.

The default output is `results/latest.json`. The report includes all method means, bounds, sample counts, runtime versions, hardware, timestamps, and SHA-256 hashes of the measured sources. The runner also prints the common-strategy table. Positive iteration counts and nonnegative warmup counts are required.

Individual programs remain usable:

```sh
python3 Python/leap_year.py --start 1582 --finish 2020 --iterations 10 --warmups 3 --output results/python.json
go run Go/leapYear.go 1582 2020 10 results/go.json false 3
node JavaScript/leapYear.js --start 1582 --finish 2020 --iterations 10 --warmups 3 --fileName results/javascript.json
dotnet run --project C_Sharp/C_Sharp.csproj --configuration Release -- 1582 2020 10 results/csharp.json false 3
```

Create `results/` first when invoking individual programs. The Go and C# final positional arguments are the print flag and optional warmup count; Python uses `-r` for printing and JavaScript uses `--print`.

## Measured comparison

Measured on **2026-10-04 UTC**, on an **Apple M1, macOS 26.5.1 (arm64)**, with Python **3.9.6**, Go **1.24.1**, Node.js **25.9.0**, and .NET **8.0.2** (SDK **8.0.201**, Release).

All methods use `[1582, 1000000)`, containing **242,116 leap years**, with **3 warmups and 10 measured calls per method**. Values below are mean milliseconds per call; lower is faster.

| Strategy | Python | Go | JavaScript | C# |
| --- | ---: | ---: | ---: | ---: |
| Scan each year | 60.857 | 3.253 | 2.125 | 1.551 |
| Counter each year | 125.127 | 3.082 | 4.067 | 1.905 |
| Step by four | 21.216 | 2.909 | 2.091 | 1.532 |
| Optimized modulo | 37.653 | 2.069 | 2.109 | 1.219 |
| Optimized counter | 24.707 | 2.193 | 1.608 | 0.863 |

Additional variants measured in the same run:

| Language | Method | Mean ms |
| --- | --- | ---: |
| Python | `leap_bit_no_print` (Bitwise, stepping by four) | 16.232 |
| Python | `leap_year_no_loops` (Range/filter) | 17.678 |
| Python | `leap_year_sets` (Set difference and sort) | 23.896 |
| Go | `leapYear` (Modulo, testing 400 first) | 3.050 |
| JavaScript | `leapYearNoLoops` (Array construction/filter) | 14.111 |
| C# | `LeapYearLinq` (LINQ) | 7.854 |

These measurements describe this workload on this machine and runtime configuration. Small differences can vary with scheduling, allocation, garbage collection, and JIT behavior; this run does not establish a general language ranking. The complete measurements and source hashes are in [benchmarks/latest.json](benchmarks/latest.json).
