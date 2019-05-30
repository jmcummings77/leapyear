namespace interviews
{
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using System.Diagnostics;
    using System.IO;
    using Newtonsoft.Json;

    public static class LeapYear
    {
        public static void Run(string[] args)
        {
            int start = 1582;
            int finish = 24000;
            int iterations = 100;
            var success = int.TryParse(args[0], out start);
            success = success && int.TryParse(args[1], out finish);
            var hasIterations = success && int.TryParse(args[2], out iterations);
            if(!success)
            {
                Console.WriteLine("Bad inputs: must be three integers and a file name separated by spaces. => start finish iterations outfilename");
            }
            bool print = false;
            var parse = bool.TryParse(args[4], out print);
            var results = new List<object>();
            if (print)
            {
                results.Add(MeasureSlow(start, finish, NoOptimizations, "NoOptimizations", iterations));
                results.Add(Measure(start, finish, PullUpPrinting, "PullUpPrinting", iterations));
                results.Add(MeasureSlow(start, finish, ReducedModulos, "ReducedModulos", iterations));
                results.Add(MeasureSlow(start, finish, Counter, "Counter", iterations));
                results.Add(MeasureSlow(start, finish, CountByFour, "CountByFour", iterations));
            }
            
            results.Add(Measure(start, finish, NoPrintReducedModulos, "NoPrintReducedModulos", iterations));
            results.Add(Measure(start, finish, NoPrintCounter, "NoPrintCounter", iterations));
            results.Add(Measure(start, finish, NoPrintCountByFour, "NoPrintCountByFour", iterations));
            results.Add(Measure(start, finish, LeapYearModulos, "LeapYearModulos", iterations));
            results.Add(Measure(start, finish, LeapYearCounter, "LeapYearCounter", iterations));
            results.Add(Measure(start, finish, LeapYearLinq, "LeapYearLinq", iterations));
            File.WriteAllText(args[3], JsonConvert.SerializeObject(results));
        }

        private static object Measure(int start, int finish, Func<int, int, int[]> method, string name, int iterations = 100)
        {
            var results = new List<int>();
            for (var i = 0; i < 100; i++) 
            {
                var sw = new Stopwatch();
                sw.Start();
                method(start, finish);
                sw.Stop();
                results.Add(sw.Elapsed.Milliseconds);
            }
            var average = results.Average();
            return new { name, average };
        }

        private static object MeasureSlow(int start, int finish, Func<int, int, string> method, string name, int iterations = 100)
        {
            var results = new List<int>();
            for (var i = 0; i < 100; i++) 
            {
                var sw = new Stopwatch();
                sw.Start();
                method(start, finish);
                sw.Stop();
                results.Add(sw.Elapsed.Milliseconds);
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
            Console.WriteLine(results);
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
            while(start % 4 != 0) {
                start++;
            }
            var hundredCounter = Math.Floor((start % 100.0) / 4.0);;
            var fourHundredCounter = Math.Floor((start % 400.0) / 100.0);
            for (var year = start; year < finish; year++) {
                if (hundredCounter == 100) {
                    fourHundredCounter++;
                    hundredCounter = 1;
                    if (fourHundredCounter == 4) {
                        Console.WriteLine(year);
                        fourHundredCounter = 0;
                    }
                } else {
                    hundredCounter++;
                    Console.WriteLine(year);
                }
            }
            return "";

        }

        private static string CountByFour(int start, int finish) 
        {
            while(start % 4 != 0) {
                start++;
            }
            
            for (var year = start; year < finish; year+=4) {
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
            while(start % 4 != 0) {
                start++;
            }
            
            for (var year = start; year < finish; year+=4) {
                if (year % 100 != 0 || year % 400 == 0) {
                    results.Add(year);
                }
            }

            return results.ToArray();
        }

        private static int[] NoPrintCounter(int start, int finish) 
        {
            var results = new List<int>();
            while(start % 4 != 0) {
                start++;
            }
            var hundredCounter = Math.Floor((start % 100.0) / 4.0);;
            var fourHundredCounter = Math.Floor((start % 400.0) / 100.0);
            for (var year = start; year < finish; year++) {
                if (hundredCounter == 100) {
                    fourHundredCounter++;
                    hundredCounter = 1;
                    if (fourHundredCounter == 4) {
                        results.Add(year);
                        fourHundredCounter = 0;
                    }
                } else {
                    hundredCounter++;
                    results.Add(year);
                }
            }

            return results.ToArray();
        }

        // fully optimized
        private static int[] LeapYearModulos(int start, int finish) 
        {
            while (start % 4 != 0) {
                start++;
            }
            finish += 4;
            var results = new List<int>();
            for (var year = start; year < finish; year+=4) {
                if(year % 100 == 0) {
                    if (year % 400 == 0) {
                        results.Add(year);
                    }
                } else {
                    results.Add(year);
                }
            }
            return results.ToArray();
        }

        private static int[] LeapYearCounter(int start, int finish) {
            finish += 4;
            var results = new List<int>();
            var mod = start % 4;
            if (mod != 0) {
                start += 4 - mod;
            }
            var hundredCounter = Math.Floor((start % 100.0) / 4.0);;
            var fourHundredCounter = Math.Floor((start % 400.0) / 100.0);
            for (var year = start; year < finish; year+=4) 
            {
                if (hundredCounter == 25) 
                {
                    fourHundredCounter++;
                    hundredCounter = 1;
                    if (fourHundredCounter == 4) 
                    {
                        results.Add(year);
                        fourHundredCounter = 0;
                    }
                } 
                else 
                {
                    hundredCounter++;
                    results.Add(year);
                }
            }
            return results.ToArray();
        }

        private static int[] LeapYearLinq(int start, int finish)
        {
            return Enumerable.Range(start, finish - start + 1).Where(x => x % 4 == 0)
                .Where(y => y % 100 != 0 || y % 400 == 0).ToArray();
        }
    }
}
