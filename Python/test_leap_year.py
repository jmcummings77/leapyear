"""Run from the repository root: python3 -m unittest Python.test_leap_year -v."""

import calendar
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Python import leap_year


RETURNING_METHODS = (
    leap_year.no_print_reduced_modulos,
    leap_year.no_print_counter,
    leap_year.no_print_count_by_four,
    leap_year.leap_bit_no_print,
    leap_year.leap_year_modulos,
    leap_year.leap_year_counter,
    leap_year.leap_year_no_loops,
    leap_year.leap_year_sets,
)
PRINTING_METHODS = (
    leap_year.code_golf,
    leap_year.leap_bit,
    leap_year.no_optimizations,
    leap_year.pull_up_printing,
    leap_year.reduced_modulos,
    leap_year.counter,
    leap_year.count_by_four,
)


class LeapYearTests(unittest.TestCase):
    def tearDown(self):
        leap_year.times.clear()

    def assert_all_methods(self, start, finish, expected):
        for method in RETURNING_METHODS:
            with self.subTest(method=method.__name__, start=start, finish=finish):
                self.assertEqual(method(start, finish), expected)
        for method in PRINTING_METHODS:
            with self.subTest(method=method.__name__, start=start, finish=finish):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    method(start, finish)
                self.assertEqual([int(year) for year in output.getvalue().split()], expected)

    def test_reported_empty_range(self):
        self.assert_all_methods(1582, 1582, [])

    def test_bounds_and_centuries(self):
        cases = (
            (1582, 1584, []),
            (1582, 1585, [1584]),
            (1584, 1584, []),
            (1584, 1585, [1584]),
            (1596, 1605, [1596, 1600, 1604]),
            (1600, 1601, [1600]),
            (1696, 1705, [1696, 1704]),
            (1700, 1701, []),
            (1896, 1905, [1896, 1904]),
            (1996, 2005, [1996, 2000, 2004]),
            (2096, 2105, [2096, 2104]),
            (1585, 1584, []),
            (1704, 1600, []),
            (-4, 5, [-4, 0, 4]),
        )
        for start, finish, expected in cases:
            self.assert_all_methods(start, finish, expected)

    def test_every_start_in_a_gregorian_cycle(self):
        # Exercise every cycle phase and all possible endpoint residues modulo 4.
        for start in range(1582, 1982):
            for length in (-5, 0, 1, 2, 3, 4, 5, 24, 100, 401):
                finish = start + length
                expected = [year for year in range(start, finish) if calendar.isleap(year)]
                self.assert_all_methods(start, finish, expected)

    def test_multiple_cycles_and_negative_years(self):
        for start, finish in ((1, 2401), (-801, 402)):
            expected = [year for year in range(start, finish) if calendar.isleap(year)]
            self.assert_all_methods(start, finish, expected)


class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        leap_year.times.clear()

    def tearDown(self):
        leap_year.times.clear()

    def test_total_milliseconds_from_monotonic_clock(self):
        for elapsed, milliseconds in ((1.25, 1250.0), (0.000125, 0.125)):
            with self.subTest(elapsed=elapsed):
                with patch.object(leap_year.time, 'perf_counter', side_effect=(0.0, elapsed)):
                    self.assertEqual(leap_year.leap_year_modulos(1600, 1601), [1600])
                self.assertAlmostEqual(leap_year.times['leap_year_modulos'][-1], milliseconds)

    def test_each_run_uses_only_its_requested_samples(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'results.json'
            with contextlib.redirect_stdout(io.StringIO()):
                leap_year.evaluate_performance(1596, 1605, output, 2, True)
            expected_names = {method.__name__ for method in RETURNING_METHODS + PRINTING_METHODS}
            expected_names.remove('code_golf')  # This standalone demonstration is not benchmarked.
            self.assertEqual(set(leap_year.times), expected_names)
            self.assertTrue(all(len(samples) == 2 for samples in leap_year.times.values()))

            # A second call must neither retain printing methods nor average old samples.
            with patch.object(leap_year.time, 'perf_counter', side_effect=[0.0, 1.25] * 8):
                leap_year.evaluate_performance(1582, 1582, output, 1, False)
            expected = {method.__name__: 1250.0 for method in RETURNING_METHODS}
            self.assertEqual(json.loads(output.read_text()), expected)
            self.assertEqual(leap_year.times, {name: [value] for name, value in expected.items()})

    def test_iterations_must_be_positive(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'results.json'
            for iterations in (0, -1):
                with self.subTest(iterations=iterations):
                    with self.assertRaisesRegex(ValueError, 'iterations must be positive'):
                        leap_year.evaluate_performance(1582, 2020, output, iterations, False)
                    self.assertFalse(output.exists())

    def test_warmup_samples_are_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'results.json'
            # Eight functions: one slow warmup each, then two measured samples each.
            ticks = [0.0, 100.0] * 8 + [0.0, 0.25] * 16
            with patch.object(leap_year.time, 'perf_counter', side_effect=ticks) as clock:
                leap_year.evaluate_performance(1582, 1601, output, 2, False, warmups=1)
            self.assertEqual(clock.call_count, 48)
            self.assertTrue(all(samples == [250.0, 250.0] for samples in leap_year.times.values()))
            self.assertEqual(json.loads(output.read_text()),
                             {method.__name__: 250.0 for method in RETURNING_METHODS})
            with self.assertRaisesRegex(ValueError, 'warmups must be nonnegative'):
                leap_year.evaluate_performance(1582, 1601, output, 2, False, warmups=-1)


if __name__ == '__main__':
    unittest.main()
