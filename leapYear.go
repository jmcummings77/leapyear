package main

import (
	"fmt"
	"time"
	"math"
	"os"
	"strconv"
	"encoding/json"
)

type fn func(int, int) []int 
type fnSlow func(int, int)

func main() {
	start, err := strconv.Atoi(os.Args[1])
	if err != nil {
		panic(err)
	}
	finish, err := strconv.Atoi(os.Args[2])
	if err != nil {
		panic(err)
	}
	iterations, err := strconv.Atoi(os.Args[3])
	if err != nil {
		panic(err)
	}
	fname := os.Args[4]
	if fname == "" {
		fname = "./go_results.txt"
	}

	runPrint, err := strconv.ParseBool(os.Args[4])
	if err != nil {
		runPrint = false
	}
	results := make(map[string]float64)

	if runPrint {
		results["noOptimizations"] = measureSlow(start, finish, noOptimizations, iterations);
		results["pullUpPrinting"] = measureSlow(start, finish, pullUpPrinting,  iterations);
		results["reducedModulos"] = measureSlow(start, finish, reducedModulos, iterations);
		results["counter"] = measureSlow(start, finish, counter, iterations);
		results["countByFour"] = measureSlow(start, finish, countByFour, iterations);
	}
	
	results["leapYear"] = measure(start, finish, leapYear, iterations)
	results["leapYearModulos"] = measure(start, finish, leapYearModulos, iterations);
	results["leapYearCounter"] = measure(start, finish, leapYearCounter, iterations);
	results["noPrintReducedModulos"] = measure(start, finish, noPrintReducedModulos, iterations);
	results["noPrintCounter"] = measure(start, finish, noPrintCounter, iterations);
	results["noPrintCountByFour"] = measure(start, finish, noPrintCountByFour, iterations);
	file, err := os.Create(fname)

	if err != nil {
		panic(err)
	}
	defer file.Close()
	data, err := json.Marshal(results)
	if err != nil {
		panic(err)
	}
	fmt.Println(string(data))
	fmt.Println(file.Name())

	file.Write(data)
	file.Close()
}

func measure(a int, b int, f fn, iterations int) float64 {
	counterResults := make([]time.Duration, 0)
	for count := 0; count < iterations; count++ {
		start := time.Now()
		f(a, b)
		counterResults = append(counterResults, time.Since(start))
	}
	var total time.Duration
	for _, value:= range counterResults {
		total += value
	}
	totalMs := int64(total/time.Millisecond)
	return float64(totalMs)/float64(len(counterResults))
}

func measureSlow(a int, b int, f fnSlow, iterations int) float64 {
	counterResults := make([]time.Duration, 0)
	for count := 0; count < iterations; count++ {
		start := time.Now()
		f(a, b)
		counterResults = append(counterResults, time.Since(start))
	}
	var total time.Duration
	for _, value:= range counterResults {
		total += value
	}
	totalMs := int64(total/time.Millisecond)
	return float64(totalMs)/float64(len(counterResults))
}

func leapYear(start, finish int) []int {
	for start % 4 != 0 {
		start++
	}
	finish += 4
	results := make([]int, 0)
    for year := start; year < finish; year+=4 {
		if year % 400 == 0 {
			results = append(results, year)
		} else if year % 100 == 0 {

		} else {
			results = append(results, year)
		}
    }
    return results
}

func leapYearCounter(start, finish int) []int {
	finish += 4
	results := make([]int, 0)
    mod := start % 4
    if mod != 0 {
        start += 4 - mod
	}
    hundredCounter := math.Floor(float64(start % 100.0) / 4.0)
    fourHundredCounter := math.Floor(float64(start % 400.0) / 100.0)
	for year := start; year < finish; year+=4 {
        if hundredCounter == 25 {
			fourHundredCounter++
			hundredCounter = 1
			if fourHundredCounter == 4 {
				results = append(results, year)
				fourHundredCounter = 0
			}
		} else {
			hundredCounter++
			results = append(results, year)
		}
	}
    return results
}


func noOptimizations(start, finish int) {
    for year := start; year < finish; year++ {
    	isDivisibleBy4 := year % 4 == 0;
        isDivisibleBy100 := year % 100 == 0;
        isDivisibleBy400 := year % 400 == 0;
        if (isDivisibleBy4 && (!isDivisibleBy100 || isDivisibleBy400)) {
            fmt.Println(year);
        }
    }
}

// one optimization
func pullUpPrinting(start, finish int) {
	results := make([]int, 0)
    for year := start; year < finish; year++ {
        isDivisibleBy4 := year % 4 == 0;
        isDivisibleBy100 := year % 100 == 0;
        isDivisibleBy400 := year % 400 == 0;
        if (isDivisibleBy4 && (!isDivisibleBy100 || isDivisibleBy400)) {
			results = append(results, year)
        }
    }
    fmt.Println(results);
}

func reducedModulos(start, finish int) {
    for year := start; year < finish; year++ {
        if (year % 4 == 0 && (year % 100 != 0 || year % 400 == 0)) {
            fmt.Println(year);
        }
    }
}

func counter(start, finish int) {
    for start % 4 != 0 {
        start++;
    }
    hundredCounter := math.Floor(float64(start % 100.0) / 4.0)
    fourHundredCounter := math.Floor(float64(start % 400.0) / 100.0)
	for year := start; year < finish; year++ {
        if (hundredCounter == 100) {
			fourHundredCounter++;
			hundredCounter = 1;
			if (fourHundredCounter == 4) {
                fmt.Println(year);
				fourHundredCounter = 0;
			}
		} else {
			hundredCounter++;
            fmt.Println(year);
		}
	}
}

func countByFour(start, finish int) {
    for start % 4 != 0 {
        start++;
    }
    
    for year := start; year < finish; year+=4 {
        isDivisibleBy100 := year % 100 == 0;
        isDivisibleBy400 := year % 400 == 0;
        if (!isDivisibleBy100 || isDivisibleBy400) {
            fmt.Println(year);
        }
    }
}

// pull up (no) print + second optimization
func noPrintReducedModulos(start, finish int) []int {
    results := make([]int, 0)
    for year := start; year < finish; year++ {
        if (year % 4 == 0 && (year % 100 != 0 || year % 400 == 0)) {
            results = append(results, year)
        }
    }
    return results;
}

func noPrintCountByFour(start, finish int) []int {
    results := make([]int, 0)
    for (start % 4 != 0) {
        start++;
    }
    
    for year := start; year < finish; year+=4 {
        if (year % 100 != 0 || year % 400 == 0) {
            results = append(results, year)
        }
    }

    return results;
}

func noPrintCounter(start, finish int) []int {
    results := make([]int, 0)
    for start % 4 != 0 {
        start++;
    }
	hundredCounter := math.Floor(float64(start % 100.0) / 4.0)
    fourHundredCounter := math.Floor(float64(start % 400.0) / 100.0)

	for year := start; year < finish; year++ {
        if (hundredCounter == 100) {
			fourHundredCounter++;
			hundredCounter = 1;
			if (fourHundredCounter == 4) {
                results = append(results, year)
				fourHundredCounter = 0;
			}
		} else {
			hundredCounter++;
            results = append(results, year)
		}
	}

    return results;
}

// fully optimized
func leapYearModulos(start, finish int) []int {
	for (start % 4 != 0) {
		start++;
	}
    finish += 4;
	results := make([]int, 0);
    for year := start; year < finish; year+=4 {
        if(year % 100 == 0) {
            if (year % 400 == 0) {
                results = append(results, year);
            }
        } else {
            results = append(results, year)
        }
    }
    return results;
}
