package main

import (
	"encoding/json"
	"io"
	"os"
	"path/filepath"
	"reflect"
	"strconv"
	"strings"
	"testing"
	"time"
)

func expectedYears(start, finish int) []int {
	result := make([]int, 0)
	for year := start; year < finish; year++ {
		if year%400 == 0 || year%4 == 0 && year%100 != 0 {
			result = append(result, year)
		}
	}
	return result
}

func testRanges() [][2]int {
	ranges := [][2]int{
		{1582, 1582}, {1582, 1584}, {1582, 1585}, {1584, 1584},
		{1900, 1901}, {2000, 2001}, {2100, 2101}, {2400, 2401},
		{-401, 402}, {0, 1}, {maxInt - 10, maxInt},
		{-maxInt - 1, -maxInt + 9}, {maxInt, maxInt},
	}
	// Every starting phase in a complete Gregorian cycle, including negatives.
	for _, base := range []int{-400, 1582} {
		for offset := 0; offset < 400; offset++ {
			for _, width := range []int{-4, 0, 1, 3, 4, 5, 25, 100, 400} {
				start := base + offset
				ranges = append(ranges, [2]int{start, start + width})
			}
		}
	}
	return ranges
}

func TestReturningAlgorithms(t *testing.T) {
	methods := map[string]fn{
		"leapYear":              leapYear,
		"leapYearModulos":       leapYearModulos,
		"leapYearCounter":       leapYearCounter,
		"noPrintReducedModulos": noPrintReducedModulos,
		"noPrintCounter":        noPrintCounter,
		"noPrintCountByFour":    noPrintCountByFour,
	}
	for name, method := range methods {
		t.Run(name, func(t *testing.T) {
			for _, bounds := range testRanges() {
				want := expectedYears(bounds[0], bounds[1])
				got := method(bounds[0], bounds[1])
				if !reflect.DeepEqual(got, want) {
					t.Fatalf("range %v: got %v, want %v", bounds, got, want)
				}
			}
		})
	}
}

func captureStdout(t *testing.T, f func()) string {
	t.Helper()
	r, w, err := os.Pipe()
	if err != nil {
		t.Fatal(err)
	}
	old := os.Stdout
	os.Stdout = w
	defer func() {
		os.Stdout = old
		r.Close()
		w.Close()
	}()
	// Each test prints at most two 400-year cycles, well within the pipe buffer.
	f()
	w.Close()
	output, err := io.ReadAll(r)
	if err != nil {
		t.Fatal(err)
	}
	return string(output)
}

func TestPrintingAlgorithms(t *testing.T) {
	methods := map[string]fnSlow{
		"noOptimizations": noOptimizations,
		"pullUpPrinting":  pullUpPrinting,
		"reducedModulos":  reducedModulos,
		"counter":         counter,
		"countByFour":     countByFour,
	}
	for name, method := range methods {
		t.Run(name, func(t *testing.T) {
			for _, bounds := range testRanges() {
				output := captureStdout(t, func() { method(bounds[0], bounds[1]) })
				got := make([]int, 0)
				for _, field := range strings.Fields(strings.Trim(output, "[]\n ")) {
					year, err := strconv.Atoi(field)
					if err != nil {
						t.Fatal(err)
					}
					got = append(got, year)
				}
				want := expectedYears(bounds[0], bounds[1])
				if !reflect.DeepEqual(got, want) {
					t.Fatalf("range %v: got %v, want %v", bounds, got, want)
				}
			}
		})
	}
}

func TestAverageMilliseconds(t *testing.T) {
	for _, tc := range []struct {
		total time.Duration
		count int
		want  float64
	}{
		{750 * time.Microsecond, 3, 0.25},
		{1500 * time.Microsecond, 2, 0.75},
		{2500 * time.Millisecond, 2, 1250},
	} {
		if got := averageMilliseconds(tc.total, tc.count); got != tc.want {
			t.Fatalf("averageMilliseconds(%v, %d) = %v; want %v", tc.total, tc.count, got, tc.want)
		}
	}
}

func TestMeasurementCountsAndWarmups(t *testing.T) {
	for _, slow := range []bool{false, true} {
		calls := 0
		var warmupElapsed time.Duration
		callback := func(a, b int) {
			if a != 1582 || b != 2001 {
				t.Fatalf("callback range = [%d, %d)", a, b)
			}
			calls++
			if calls <= 2 {
				start := time.Now()
				time.Sleep(time.Millisecond)
				warmupElapsed += time.Since(start)
			}
		}
		start := time.Now()
		var average float64
		if slow {
			average = measureSlow(1582, 2001, callback, 3, 2)
		} else {
			average = measure(1582, 2001, func(a, b int) []int { callback(a, b); return nil }, 3, 2)
		}
		elapsed := time.Since(start)
		if calls != 5 {
			t.Fatalf("slow=%v: got %d callback calls, want 5", slow, calls)
		}
		// Bound by actual elapsed time, avoiding an absolute scheduler-sensitive limit.
		if average <= 0 || average*3 > float64(elapsed-warmupElapsed)/float64(time.Millisecond) {
			t.Fatalf("slow=%v: average %v ms includes warmup time", slow, average)
		}
	}
}

func TestMeasurementRejectsInvalidCounts(t *testing.T) {
	for _, counts := range [][2]int{{0, 0}, {-1, 0}, {1, -1}} {
		for _, slow := range []bool{false, true} {
			func() {
				defer func() {
					if recover() == nil {
						t.Errorf("slow=%v counts=%v: expected panic", slow, counts)
					}
				}()
				callback := func(int, int) { t.Fatal("invalid count called benchmark") }
				if slow {
					measureSlow(0, 1, callback, counts[0], counts[1])
				} else {
					measure(0, 1, func(a, b int) []int { callback(a, b); return nil }, counts[0], counts[1])
				}
			}()
		}
	}
}

func TestCLIArguments(t *testing.T) {
	for _, flag := range []string{"false", "true"} {
		file := filepath.Join(t.TempDir(), "results.json")
		captureStdout(t, func() {
			if err := run([]string{"1582", "1585", "2", file, flag, "1"}); err != nil {
				t.Fatal(err)
			}
		})
		data, err := os.ReadFile(file)
		if err != nil {
			t.Fatal(err)
		}
		results := make(map[string]float64)
		if err := json.Unmarshal(data, &results); err != nil {
			t.Fatal(err)
		}
		want := 6
		if flag == "true" {
			want = 11
		}
		if len(results) != want {
			t.Fatalf("print=%s: got %d results, want %d", flag, len(results), want)
		}
	}
	file := filepath.Join(t.TempDir(), "not-written.json")
	for _, args := range [][]string{
		{}, {"1582", "1585", "0", file}, {"1582", "1585", "-1", file},
		{"1582", "1585", "bad", file}, {"bad", "1585", "1", file},
		{"1582", "bad", "1", file}, {"1582", "1585", "1", file, "bad"},
		{"1582", "1585", "1", file, "false", "-1"},
		{"1582", "1585", "1", file, "false", "bad"},
		{"1582", "1585", "1", file, "false", "1", "extra"},
	} {
		if err := run(args); err == nil {
			t.Errorf("run(%v) should fail", args)
		}
	}
	if _, err := os.Stat(file); !os.IsNotExist(err) {
		t.Fatal("invalid arguments should not write an output file")
	}
}
