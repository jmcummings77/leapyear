namespace C_Sharp
{
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using System.Diagnostics;
    using System.IO;
    using System.Text.Json;

    public static class LeapYear
    {
        public static void Run(string[] args)
        {
            const string usage = "Expected: start finish iterations outfilename [true|false] [warmups]";
            if (args.Length < 4 || args.Length > 6)
            {
                throw new ArgumentException(usage);
            }
            int start, finish, iterations;
            if (!int.TryParse(args[0], out start) ||
                !int.TryParse(args[1], out finish) ||
                !int.TryParse(args[2], out iterations))
            {
                throw new ArgumentException(usage);
            }
            if (iterations <= 0)
            {
                throw new ArgumentOutOfRangeException(nameof(iterations), "Iterations must be positive.");
            }
            bool print = false;
            if (args.Length >= 5 && !bool.TryParse(args[4], out print))
            {
                throw new ArgumentException(usage);
            }
            int warmups = 0;
            if (args.Length == 6 && !int.TryParse(args[5], out warmups))
            {
                throw new ArgumentException(usage);
            }
            if (warmups < 0)
            {
                throw new ArgumentOutOfRangeException(nameof(warmups), "Warmups cannot be negative.");
            }
            var results = new List<object>();
            if (print)
            {
                results.Add(MeasureSlow(start, finish, NoOptimizations, "NoOptimizations", iterations, warmups));
                results.Add(Measure(start, finish, PullUpPrinting, "PullUpPrinting", iterations, warmups));
                results.Add(MeasureSlow(start, finish, ReducedModulos, "ReducedModulos", iterations, warmups));
                results.Add(MeasureSlow(start, finish, Counter, "Counter", iterations, warmups));
                results.Add(MeasureSlow(start, finish, CountByFour, "CountByFour", iterations, warmups));
            }
            
            results.Add(Measure(start, finish, NoPrintReducedModulos, "NoPrintReducedModulos", iterations, warmups));
            results.Add(Measure(start, finish, NoPrintCounter, "NoPrintCounter", iterations, warmups));
            results.Add(Measure(start, finish, NoPrintCountByFour, "NoPrintCountByFour", iterations, warmups));
            results.Add(Measure(start, finish, LeapYearModulos, "LeapYearModulos", iterations, warmups));
            results.Add(Measure(start, finish, LeapYearCounter, "LeapYearCounter", iterations, warmups));
            results.Add(Measure(start, finish, LeapYearLinq, "LeapYearLinq", iterations, warmups));
            File.WriteAllText(args[3], JsonSerializer.Serialize(results));
        }

        private static object Measure(int start, int finish, Func<int, int, int[]> method, string name, int iterations = 100, int warmups = 0)
        {
            if (iterations <= 0)
            {
                throw new ArgumentOutOfRangeException(nameof(iterations), "Iterations must be positive.");
            }
            if (warmups < 0)
            {
                throw new ArgumentOutOfRangeException(nameof(warmups), "Warmups cannot be negative.");
            }
            for (var i = 0; i < warmups; i++) method(start, finish);
            var results = new List<double>();
            for (var i = 0; i < iterations; i++)
            {
                var sw = new Stopwatch();
                sw.Start();
                method(start, finish);
                sw.Stop();
                results.Add(sw.Elapsed.TotalMilliseconds);
            }
            var average = results.Average();
            return new { name, average };
        }

        private static object MeasureSlow(int start, int finish, Func<int, int, string> method, string name, int iterations = 100, int warmups = 0)
        {
            if (iterations <= 0)
            {
                throw new ArgumentOutOfRangeException(nameof(iterations), "Iterations must be positive.");
            }
            if (warmups < 0)
            {
                throw new ArgumentOutOfRangeException(nameof(warmups), "Warmups cannot be negative.");
            }
            for (var i = 0; i < warmups; i++) method(start, finish);
            var results = new List<double>();
            for (var i = 0; i < iterations; i++)
            {
                var sw = new Stopwatch();
                sw.Start();
                method(start, finish);
                sw.Stop();
                results.Add(sw.Elapsed.TotalMilliseconds);
            }
            var average = results.Average();
            return new { name, average };
        }

        private static string NoOptimizations(int start, int finish) 
        {
            for (var year = start; year < finish; year++) {
                var isDivisibleBy4 = year % 4 == 0;
                var isDivisibleBy100 = year % 100 == 0;
                var isDivisibleBy400 = year % 400 == 0;
                if (isDivisibleBy4 && (!isDivisibleBy100 || isDivisibleBy400)) {
                    Console.WriteLine(year);
                }
            }
            return "";
        }

        // one optimization
        private static int[] PullUpPrinting(int start, int finish) 
        {
            var results = new List<int>();
            for (var year = start; year < finish; year++) {
                var isDivisibleBy4 = year % 4 == 0;
                var isDivisibleBy100 = year % 100 == 0;
                var isDivisibleBy400 = year % 400 == 0;
                if (isDivisibleBy4 && (!isDivisibleBy100 || isDivisibleBy400)) {
                    results.Add(year);
                }
            }
            if (results.Count > 0)
            {
                Console.WriteLine(string.Join(Environment.NewLine, results));
            }
            return results.ToArray();

        }

        private static string ReducedModulos(int start, int finish) 
        {
            for (var year = start; year < finish; year++) {
                if (year % 4 == 0 && (year % 100 != 0 || year % 400 == 0)) {
                    Console.WriteLine(year);
                }
            }
            return "";
        }

        private static string Counter(int start, int finish) 
        {
            var fourCounter = (start % 4 + 4) % 4;
            var hundredCounter = (start % 100 + 100) % 100;
            var fourHundredCounter = (start % 400 + 400) % 400;
            for (var year = start; year < finish; year++) {
                if (fourCounter == 0 && (hundredCounter != 0 || fourHundredCounter == 0)) {
                    Console.WriteLine(year);
                }
                if (++fourCounter == 4) fourCounter = 0;
                if (++hundredCounter == 100) hundredCounter = 0;
                if (++fourHundredCounter == 400) fourHundredCounter = 0;
            }
            return "";

        }

        private static string CountByFour(int start, int finish) 
        {
            for (var year = FirstMultipleOfFour(start); year < finish; year+=4) {
                var isDivisibleBy100 = year % 100 == 0;
                var isDivisibleBy400 = year % 400 == 0;
                if (!isDivisibleBy100 || isDivisibleBy400) {
                    Console.WriteLine(year);
                }
            }
            return "";
        }

        // pull up (no) print + second optimization
        private static int[] NoPrintReducedModulos(int start, int finish) 
        {
            var results = new List<int>();
            for (var year = start; year < finish; year++) {
                if (year % 4 == 0 && (year % 100 != 0 || year % 400 == 0)) {
                    results.Add(year);
                }
            }
            return results.ToArray();
        }

        private static int[] NoPrintCountByFour(int start, int finish) 
        {
            var results = new List<int>();
            for (var year = FirstMultipleOfFour(start); year < finish; year+=4) {
                if (year % 100 != 0 || year % 400 == 0) {
                    results.Add((int)year);
                }
            }

            return results.ToArray();
        }

        private static int[] NoPrintCounter(int start, int finish) 
        {
            var results = new List<int>();
            var fourCounter = (start % 4 + 4) % 4;
            var hundredCounter = (start % 100 + 100) % 100;
            var fourHundredCounter = (start % 400 + 400) % 400;
            for (var year = start; year < finish; year++) {
                if (fourCounter == 0 && (hundredCounter != 0 || fourHundredCounter == 0)) {
                    results.Add(year);
                }
                if (++fourCounter == 4) fourCounter = 0;
                if (++hundredCounter == 100) hundredCounter = 0;
                if (++fourHundredCounter == 400) fourHundredCounter = 0;
            }

            return results.ToArray();
        }

        // fully optimized
        private static int[] LeapYearModulos(int start, int finish) 
        {
            var results = new List<int>();
            for (var year = FirstMultipleOfFour(start); year < finish; year+=4) {
                if(year % 100 == 0) {
                    if (year % 400 == 0) {
                        results.Add((int)year);
                    }
                } else {
                    results.Add((int)year);
                }
            }
            return results.ToArray();
        }

        private static int[] LeapYearCounter(int start, int finish) {
            var results = new List<int>();
            var firstYear = FirstMultipleOfFour(start);
            var cycle = (firstYear % 400 + 400) % 400;
            var hundredCounter = cycle % 100 / 4;
            var fourHundredCounter = cycle / 100;
            for (var year = firstYear; year < finish; year+=4)
            {
                if (hundredCounter != 0 || fourHundredCounter == 0)
                {
                    results.Add((int)year);
                }
                if (++hundredCounter == 25)
                {
                    hundredCounter = 0;
                    if (++fourHundredCounter == 4)
                    {
                        fourHundredCounter = 0;
                    }
                }
            }
            return results.ToArray();
        }

        private static int[] LeapYearLinq(int start, int finish)
        {
            if (start >= finish) return new int[0];
            return Enumerable.Range(start, checked(finish - start)).Where(x => x % 4 == 0)
                .Where(y => y % 100 != 0 || y % 400 == 0).ToArray();
        }

        // Use a wider loop variable so rounding up or stepping by four cannot wrap at int.MaxValue.
        private static long FirstMultipleOfFour(int start)
        {
            return (long)start + (4 - start % 4) % 4;
        }
    }
}
