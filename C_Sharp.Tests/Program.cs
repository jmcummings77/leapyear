using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text.Json;
using System.Threading;
using C_Sharp;

internal static class Program
{
    private static readonly string[] ArrayMethods = {
        "PullUpPrinting", "NoPrintReducedModulos", "NoPrintCounter", "NoPrintCountByFour",
        "LeapYearModulos", "LeapYearCounter", "LeapYearLinq"
    };
    private static readonly string[] PrintMethods = {
        "NoOptimizations", "ReducedModulos", "Counter", "CountByFour"
    };

    private static void Main()
    {
        var ranges = CheckAlgorithms();
        CheckTiming("Measure", false);
        CheckTiming("MeasureSlow", true);
        CheckRun();
        Console.WriteLine($"Passed: all 11 C# algorithms over {ranges} ranges, both timing wrappers, and CLI validation/output.");
    }

    private static int CheckAlgorithms()
    {
        var arrayMethods = ArrayMethods.ToDictionary(name => name,
            name => (Func<int, int, int[]>)Method(name).CreateDelegate(typeof(Func<int, int, int[]>)));
        var printMethods = PrintMethods.ToDictionary(name => name,
            name => (Func<int, int, string>)Method(name).CreateDelegate(typeof(Func<int, int, string>)));
        var ranges = new List<(int Start, int Finish)> {
            (1582, 1582), (1582, 1583), (1582, 1584), (1582, 1585), (1584, 1585),
            (1584, 1584), (1600, 1582), (1582, 2401), (1896, 1905), (1996, 2005),
            (2096, 2105), (2396, 2405), (1900, 1901), (2000, 2001), (2100, 2101),
            (-410, 410), (-400, -399), (-100, -99), (-5, 5), (0, 1),
            (int.MinValue, int.MinValue + 20), (int.MaxValue - 20, int.MaxValue),
            (int.MaxValue, int.MaxValue), (int.MaxValue, int.MaxValue - 1)
        };
        // Every alignment and position in a 400-year cycle, including short and empty intervals.
        for (var start = 1580; start < 1980; start++)
        {
            foreach (var width in new[] { 0, 1, 2, 3, 4, 5, 8, 100, 401 })
                ranges.Add((start, start + width));
        }
        var originalOut = Console.Out;
        try
        {
            foreach (var range in ranges)
            {
                var expected = Expected(range.Start, range.Finish);
                foreach (var pair in arrayMethods)
                {
                    using (var output = new StringWriter(CultureInfo.InvariantCulture))
                    {
                        Console.SetOut(output);
                        Equal(expected, pair.Value(range.Start, range.Finish), pair.Key, range);
                        if (pair.Key == "PullUpPrinting")
                            Equal(expected, PrintedYears(output), pair.Key + " output", range);
                        else
                            Require(output.ToString() == "", pair.Key + " unexpectedly printed output.");
                    }
                }
                foreach (var pair in printMethods)
                {
                    using (var output = new StringWriter(CultureInfo.InvariantCulture))
                    {
                        Console.SetOut(output);
                        pair.Value(range.Start, range.Finish);
                        Equal(expected, PrintedYears(output), pair.Key + " output", range);
                    }
                }
            }
        }
        finally
        {
            Console.SetOut(originalOut);
        }
        return ranges.Count;
    }

    private static int[] Expected(int start, int finish)
    {
        var years = new List<int>();
        for (var year = start; year < finish; year++)
        {
            // Use the framework oracle for its supported calendar years.
            var leap = year >= 1 && year <= 9999
                ? DateTime.IsLeapYear(year)
                : year % 400 == 0 || (year % 4 == 0 && year % 100 != 0);
            if (leap) years.Add(year);
        }
        return years.ToArray();
    }

    private static int[] PrintedYears(StringWriter output)
    {
        return output.ToString().Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries)
            .Select(value => int.Parse(value, CultureInfo.InvariantCulture)).ToArray();
    }

    private static void Equal(int[] expected, int[] actual, string method, (int Start, int Finish) range)
    {
        Require(expected.SequenceEqual(actual), $"{method} disagrees with the calendar oracle for [{range.Start}, {range.Finish}).");
    }

    private static void CheckTiming(string methodName, bool slow)
    {
        var calls = 0;
        Action count = () => calls++;
        var sample = Measure(methodName, slow, count, 3);
        Require(calls == 3, methodName + " ignored the requested iteration count.");
        Require(sample.GetType().GetProperty("average").PropertyType == typeof(double),
            methodName + " must preserve fractional milliseconds in its average.");
        Require((string)sample.GetType().GetProperty("name").GetValue(sample) == "sample",
            methodName + " changed the result name.");
        foreach (var invalid in new[] { 0, -1 })
        {
            Expect<ArgumentOutOfRangeException>(() => Measure(methodName, slow, count, invalid));
            Require(calls == 3, methodName + " ran a benchmark with invalid iterations.");
        }
        Expect<ArgumentOutOfRangeException>(() => Measure(methodName, slow, count, 1, -1));
        Require(calls == 3, methodName + " ran a benchmark with invalid warmups.");

        calls = 0;
        var warmedSample = Measure(methodName, slow, () => {
            if (++calls == 1) Thread.Sleep(1100);
        }, 2, 1);
        Require(calls == 3, methodName + " must run warmups plus measured iterations.");
        Require(Average(warmedSample) < 250, methodName + " included the slow warmup in its average.");

        var longSample = Measure(methodName, slow, () => Thread.Sleep(1100), 1);
        Require(Average(longSample) >= 1000, methodName + " lost whole seconds from elapsed time.");

        // A sub-millisecond workload must retain stopwatch precision, including in the serialized result.
        var fractionalSample = Measure(methodName, slow, () => {
            var timer = Stopwatch.StartNew();
            while (timer.ElapsedTicks < Stopwatch.Frequency / 4000) { }
        }, 8);
        var average = Average(fractionalSample);
        Require(average > 0 && average != Math.Truncate(average),
            methodName + " discarded fractional elapsed milliseconds.");
        using (var serialized = JsonDocument.Parse(JsonSerializer.Serialize(fractionalSample)))
        {
            Require(serialized.RootElement.GetProperty("average").GetDouble() == average,
                methodName + " lost fractional milliseconds when serializing results.");
        }
    }

    private static object Measure(string name, bool slow, Action action, int iterations, int warmups = 0)
    {
        object callback;
        if (slow)
            callback = new Func<int, int, string>((start, finish) => { action(); return ""; });
        else
            callback = new Func<int, int, int[]>((start, finish) => { action(); return Array.Empty<int>(); });
        return Invoke(Method(name), new object[] { 1582, 1601, callback, "sample", iterations, warmups });
    }

    private static double Average(object sample)
    {
        return (double)sample.GetType().GetProperty("average").GetValue(sample);
    }

    private static void CheckRun()
    {
        var directory = Path.Combine(Path.GetTempPath(), "leapyear-tests-" + Guid.NewGuid());
        Directory.CreateDirectory(directory);
        var path = Path.Combine(directory, "results.json");
        var originalOut = Console.Out;
        try
        {
            Expect<ArgumentException>(() => LeapYear.Run(Array.Empty<string>()));
            Expect<ArgumentException>(() => LeapYear.Run(new[] { "oops", "1601", "1", path }));
            Expect<ArgumentException>(() => LeapYear.Run(new[] { "1582", "oops", "1", path }));
            Expect<ArgumentException>(() => LeapYear.Run(new[] { "1582", "1601", "oops", path }));
            Expect<ArgumentException>(() => LeapYear.Run(new[] { "1582", "1601", "1", path, "oops" }));
            Expect<ArgumentOutOfRangeException>(() => LeapYear.Run(new[] { "1582", "1601", "0", path }));
            Expect<ArgumentOutOfRangeException>(() => LeapYear.Run(new[] { "1582", "1601", "-1", path }));
            Expect<ArgumentException>(() => LeapYear.Run(new[] { "1582", "1601", "1", path, "false", "oops" }));
            Expect<ArgumentOutOfRangeException>(() => LeapYear.Run(new[] { "1582", "1601", "1", path, "false", "-1" }));
            Require(!File.Exists(path), "Invalid CLI arguments wrote benchmark results.");
            LeapYear.Run(new[] { "1582", "1601", "1", path });
            using (var document = JsonDocument.Parse(File.ReadAllText(path)))
            {
                var results = document.RootElement.EnumerateArray().ToArray();
                Require(results.Length == 6, "CLI must emit all six non-printing benchmarks.");
                Require(results.Select(result => result.GetProperty("name").GetString()).Distinct().Count() == 6,
                    "CLI emitted duplicate benchmark names.");
                Require(results.All(result => result.GetProperty("average").GetDouble() >= 0),
                    "CLI emitted invalid timings.");
            }
            using (var output = new StringWriter(CultureInfo.InvariantCulture))
            {
                Console.SetOut(output);
                LeapYear.Run(new[] { "1999", "2001", "2", path, "true", "3" });
                Require(PrintedYears(output).SequenceEqual(Enumerable.Repeat(2000, 25)),
                    "Printing benchmarks did not honor the requested iterations and warmups or print the leap year.");
            }
            using (var document = JsonDocument.Parse(File.ReadAllText(path)))
            {
                Require(document.RootElement.GetArrayLength() == 11, "CLI omitted printing benchmarks.");
            }
        }
        finally
        {
            Console.SetOut(originalOut);
            Directory.Delete(directory, true);
        }
    }

    private static MethodInfo Method(string name)
    {
        return typeof(LeapYear).GetMethod(name, BindingFlags.Static | BindingFlags.NonPublic);
    }

    private static object Invoke(MethodInfo method, object[] arguments)
    {
        try { return method.Invoke(null, arguments); }
        catch (TargetInvocationException exception) { throw exception.InnerException; }
    }

    private static void Expect<T>(Action action) where T : Exception
    {
        try { action(); }
        catch (T) { return; }
        throw new Exception("Expected " + typeof(T).Name + ".");
    }

    private static void Require(bool condition, string message)
    {
        if (!condition) throw new Exception(message);
    }
}
