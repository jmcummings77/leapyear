// Leap-year benchmarks over start <= year < finish, in ascending order.
package main

import (
	"encoding/json"
	"fmt"
	"os"
	"strconv"
	"time"
)

type fn func(int, int) []int
type fnSlow func(int, int)

const maxInt = int(^uint(0) >> 1)

func main() {
	if err := run(os.Args[1:]); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func run(args []string) error {
	if len(args) < 4 || len(args) > 6 {
		return fmt.Errorf("usage: leapYear START FINISH ITERATIONS OUTPUT [PRINT] [WARMUPS]")
	}
	start, err := strconv.Atoi(args[0])
	if err != nil {
		return fmt.Errorf("invalid start: %w", err)
	}
	finish, err := strconv.Atoi(args[1])
	if err != nil {
		return fmt.Errorf("invalid finish: %w", err)
	}
	iterations, err := strconv.Atoi(args[2])
	if err != nil || iterations <= 0 {
		return fmt.Errorf("iterations must be a positive integer")
	}
	fname := args[3]
	if fname == "" {
		fname = "./go_results.txt"
	}
	runPrint := false
	if len(args) >= 5 {
		runPrint, err = strconv.ParseBool(args[4])
		if err != nil {
			return fmt.Errorf("invalid print flag: %w", err)
		}
	}
	warmups := 0
	if len(args) == 6 {
		warmups, err = strconv.Atoi(args[5])
		if err != nil || warmups < 0 {
			return fmt.Errorf("warmups must be a non-negative integer")
		}
	}
	results := make(map[string]float64)
	if runPrint {
		results["noOptimizations"] = measureSlow(start, finish, noOptimizations, iterations, warmups)
		results["pullUpPrinting"] = measureSlow(start, finish, pullUpPrinting, iterations, warmups)
		results["reducedModulos"] = measureSlow(start, finish, reducedModulos, iterations, warmups)
		results["counter"] = measureSlow(start, finish, counter, iterations, warmups)
		results["countByFour"] = measureSlow(start, finish, countByFour, iterations, warmups)
	}
	results["leapYear"] = measure(start, finish, leapYear, iterations, warmups)
	results["leapYearModulos"] = measure(start, finish, leapYearModulos, iterations, warmups)
	results["leapYearCounter"] = measure(start, finish, leapYearCounter, iterations, warmups)
	results["noPrintReducedModulos"] = measure(start, finish, noPrintReducedModulos, iterations, warmups)
	results["noPrintCounter"] = measure(start, finish, noPrintCounter, iterations, warmups)
	results["noPrintCountByFour"] = measure(start, finish, noPrintCountByFour, iterations, warmups)
	data, err := json.Marshal(results)
	if err != nil {
		return err
	}
	if err := os.WriteFile(fname, data, 0644); err != nil {
		return err
	}
	fmt.Println(string(data))
	fmt.Println(fname)
	return nil
}

func validateCounts(iterations, warmups int) {
	if iterations <= 0 {
		panic("iterations must be positive")
	}
	if warmups < 0 {
		panic("warmups must be non-negative")
	}
}

func averageMilliseconds(total time.Duration, iterations int) float64 {
	validateCounts(iterations, 0)
	return float64(total) / float64(time.Millisecond) / float64(iterations)
}

func measure(a, b int, f fn, iterations, warmups int) float64 {
	validateCounts(iterations, warmups)
	for count := 0; count < warmups; count++ {
		f(a, b)
	}
	var total time.Duration
	for count := 0; count < iterations; count++ {
		start := time.Now()
		f(a, b)
		total += time.Since(start)
	}
	return averageMilliseconds(total, iterations)
}

func measureSlow(a, b int, f fnSlow, iterations, warmups int) float64 {
	validateCounts(iterations, warmups)
	for count := 0; count < warmups; count++ {
		f(a, b)
	}
	var total time.Duration
	for count := 0; count < iterations; count++ {
		start := time.Now()
		f(a, b)
		total += time.Since(start)
	}
	return averageMilliseconds(total, iterations)
}

// Go's remainder can be negative; counters need a position within the cycle.
func positiveModulo(year, divisor int) int {
	value := year % divisor
	if value < 0 {
		value += divisor
	}
	return value
}

func leapYear(start, finish int) []int {
	for start < finish && start%4 != 0 {
		start++
	}
	results := make([]int, 0)
	for year := start; year < finish; year += 4 {
		if year%400 == 0 {
			results = append(results, year)
		} else if year%100 != 0 {
			results = append(results, year)
		}
		if year > maxInt-4 {
			break
		}
	}
	return results
}

func leapYearCounter(start, finish int) []int {
	for start < finish && start%4 != 0 {
		start++
	}
	results := make([]int, 0)
	hundredCounter := positiveModulo(start, 100) / 4
	fourHundredCounter := positiveModulo(start, 400) / 100
	for year := start; year < finish; year += 4 {
		if hundredCounter != 0 || fourHundredCounter == 0 {
			results = append(results, year)
		}
		hundredCounter++
		if hundredCounter == 25 {
			hundredCounter = 0
			fourHundredCounter++
			if fourHundredCounter == 4 {
				fourHundredCounter = 0
			}
		}
		if year > maxInt-4 {
			break
		}
	}
	return results
}

func noOptimizations(start, finish int) {
	for year := start; year < finish; year++ {
		isDivisibleBy4 := year%4 == 0
		isDivisibleBy100 := year%100 == 0
		isDivisibleBy400 := year%400 == 0
		if isDivisibleBy4 && (!isDivisibleBy100 || isDivisibleBy400) {
			fmt.Println(year)
		}
	}
}

func pullUpPrinting(start, finish int) {
	results := make([]int, 0)
	for year := start; year < finish; year++ {
		isDivisibleBy4 := year%4 == 0
		isDivisibleBy100 := year%100 == 0
		isDivisibleBy400 := year%400 == 0
		if isDivisibleBy4 && (!isDivisibleBy100 || isDivisibleBy400) {
			results = append(results, year)
		}
	}
	fmt.Println(results)
}

func reducedModulos(start, finish int) {
	for year := start; year < finish; year++ {
		if year%4 == 0 && (year%100 != 0 || year%400 == 0) {
			fmt.Println(year)
		}
	}
}

func counter(start, finish int) {
	fourCounter := positiveModulo(start, 4)
	hundredCounter := positiveModulo(start, 100)
	fourHundredCounter := positiveModulo(start, 400)
	for year := start; year < finish; year++ {
		if fourCounter == 0 && (hundredCounter != 0 || fourHundredCounter == 0) {
			fmt.Println(year)
		}
		fourCounter++
		hundredCounter++
		fourHundredCounter++
		if fourCounter == 4 {
			fourCounter = 0
		}
		if hundredCounter == 100 {
			hundredCounter = 0
		}
		if fourHundredCounter == 400 {
			fourHundredCounter = 0
		}
	}
}

func countByFour(start, finish int) {
	for start < finish && start%4 != 0 {
		start++
	}
	for year := start; year < finish; year += 4 {
		isDivisibleBy100 := year%100 == 0
		isDivisibleBy400 := year%400 == 0
		if !isDivisibleBy100 || isDivisibleBy400 {
			fmt.Println(year)
		}
		if year > maxInt-4 {
			break
		}
	}
}

func noPrintReducedModulos(start, finish int) []int {
	results := make([]int, 0)
	for year := start; year < finish; year++ {
		if year%4 == 0 && (year%100 != 0 || year%400 == 0) {
			results = append(results, year)
		}
	}
	return results
}

func noPrintCountByFour(start, finish int) []int {
	results := make([]int, 0)
	for start < finish && start%4 != 0 {
		start++
	}
	for year := start; year < finish; year += 4 {
		if year%100 != 0 || year%400 == 0 {
			results = append(results, year)
		}
		if year > maxInt-4 {
			break
		}
	}
	return results
}

func noPrintCounter(start, finish int) []int {
	results := make([]int, 0)
	fourCounter := positiveModulo(start, 4)
	hundredCounter := positiveModulo(start, 100)
	fourHundredCounter := positiveModulo(start, 400)
	for year := start; year < finish; year++ {
		if fourCounter == 0 && (hundredCounter != 0 || fourHundredCounter == 0) {
			results = append(results, year)
		}
		fourCounter++
		hundredCounter++
		fourHundredCounter++
		if fourCounter == 4 {
			fourCounter = 0
		}
		if hundredCounter == 100 {
			hundredCounter = 0
		}
		if fourHundredCounter == 400 {
			fourHundredCounter = 0
		}
	}
	return results
}

func leapYearModulos(start, finish int) []int {
	for start < finish && start%4 != 0 {
		start++
	}
	results := make([]int, 0)
	for year := start; year < finish; year += 4 {
		if year%100 == 0 {
			if year%400 == 0 {
				results = append(results, year)
			}
		} else {
			results = append(results, year)
		}
		if year > maxInt-4 {
			break
		}
	}
	return results
}
