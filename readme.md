# Leap Year William

![leapyyearwilliam](https://pixel.nymag.com/imgs/daily/vulture/2016/02/29/29-leap-day-30-rock-1.w710.h473.2x.jpg)

This repository consists of alternative implementations of an algorithm to produce a list of leap years given a start and end year. The code is bad and I *do* feel bad. This is the only documentation you will get because I am a busy, busy man (read: lazy).

Each language file (leap_year.py, LeapYear.cs, leapYear.go, leapYear.js) contains a core set of functions which represent some of the most common implementations and optimizations people suggest. I tried to implement each optimization category (1) on its own, then (2) paired with each of the other optimizations one at a time, then (3) all combined together to the greatest extent possible. That meant including unnecessary modulos in certain locations for consistency.

Broadly those optimizations are:

1. Removing prints. This is the single most important optimization, and in fact omitting printing altogether is absolutely required for higher year-count runs--node even crashes at some point.
2. Minimizing the number of modulos.
3. Counting by four in the for loop (or equivalent range expression in Python)
4. Eliminating modulos altogether from the for loops in favor of a counter and if statements (mods still required at the beginning to determine where the start year is in relation to the full 400 year cycle)
5. Language specific "optimizations" which were of course not possible to reproduce and compare across languages, and most of which were either substantially slower (e.g. LINQ in C#) or only marginally competitive (range/filter in Python)

Example results format (all times in ms averaged from 100 iterations of a 24m year run):

```json
[{
    "C#": {
        "NoPrintReducedModulos": 115.77,
        "NoPrintCounter": 239.98,
        "NoPrintCountByFour": 54.16,
        "LeapYearModulos": 74.86,
        "LeapYearCounter": 58.32,
        "LeapYearLinq": 258.19
    },
    "Go": {
        "leapYear": 45.34,
        "leapYearCounter": 39,
        "leapYearModulos": 40.84,
        "noPrintCountByFour": 38.4,
        "noPrintCounter": 148.06,
        "noPrintReducedModulos": 67.24
    },
    "JavaScript": {
        "leapYearModulos": 110.26716390000657,
        "leapYearCounter": 111.66275182003156,
        "leapYearNoLoops": 1091.6129790399968,
        "noPrintReducedModulos": 156.53878397995607,
        "noPrintCounter": 607.1191596999764,
        "noPrintCountByFour": 124.87465265996754
    },
    "Python": {
        "no_print_reduced_modulos": 2095.338363647461,
        "no_print_counter": 3259.244499206543,
        "no_print_count_by_four": 1122.3544692993164,
        "leap_year_modulos": 804.6444940567017,
        "leap_year_counter": 811.4770174026489,
        "leap_year_no_loops": 941.9522285461426,
        "leap_year_sets": 1080.1961708068848
    }}]
```

Thus far, Go wins out as the best overall performance. The worst Go implementation is better than the best C# implementation. In turn the worst C# implementation is better than the best JavaScript implementation and so on until Python shows up several minutes later wondering where everyone went.

The best algorithms vary by language, with the fully optimized counter implementation being the best in most languages, except Python, in which the raw, brute force modulo approach seems to be best.

Of course, I probably did a terrible job in each language so take all of this with a grain of salt.
