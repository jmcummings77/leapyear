# Leap Year William

This repository consists of alternative implementations of an algorithm to produce a list of leap years given a start and end year. The code is bad and I *do* feel bad. This is the only documentation you will get because I am a busy, busy man (read: lazy).

Each language file (leap_year.py, LeapYear.cs, leapYear.go, leapYear.js) contains a core set of functions which represent some of the most common implementations and optimizations people suggest. I tried to implement each optimization category (1) on its own, then (2) paired with each of the other optimizations one at a time, then (3) all combined together to the greatest extent possible. That meant including unnecessary modulos in certain locations for consistency.

Broadly those optimizations are:

1. Removing prints. This is the single most important optimization, and in fact omitting printing altogether is absolutely required for higher year-count runs--node even crashes at some point.
2. Minimizing the number of modulos.
3. Counting by four in the for loop (or equivalent range expression in Python)
4. Eliminating modulos altogether from the for loops in favor of a counter and if statements (mods still required at the beginning to determine where the start year is in relation to the full 400 year cycle)
5. Language specific "optimizations" which were of course not possible to reproduce and compare across languages, and most of which were either substantially slower (e.g. LINQ in C#) or only marginally competitive (range/filter in Python)

Example results format:

```json
{
    "no_print_reduced_modulos": 22.656354904174805,
    "no_print_counter": 34.19808387756348,
    "no_print_count_by_four": 11.428391933441162,
    "leap_year_modulos": 8.139839172363281,
    "leap_year_counter": 8.39179277420044,
    "leap_year_no_loops": 9.034435749053955,
    "leap_year_sets": 4.163060188293457
}
```

Thus far, Go wins out as the best overall performance. The worst Go implementation is better than the best C# implementation. In turn the worst C# implementation is better than the best JavaScript implementation and so on until Python shows up several minutes later wondering where everyone went.

The best algorithms vary by language, with the fully optimized counter implementation being the best in most languages, except Python, in which the raw, brute force modulo approach seems to be best.

Of course, I probably did a terrible job in each language so take all of this with a grain of salt.