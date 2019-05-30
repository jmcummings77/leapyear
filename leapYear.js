const { performance } = require('perf_hooks')
const fs = require('fs')
const minimist = require('minimist');

let args = minimist(process.argv.slice(2), {  
    default: {
        start: 1582,
        finish: 24000,
        iterations: 100,
        fileName: "",
        print: false
    },
});

var times = {}

const main = () => {
    if (args.print) {
        //evaluateLowPerformanceFunctions(args.start, args.finish, args.iterations);
    }

    evaluateHighPerformanceFunctions(args.start, args.finish, false, args.iterations);
    fileName = args.fileName;
    if (fileName == "")
    {
        fileName = path.resolve(__dirname, 'javascript_results.txt')
    }
    fs.writeFile(fileName, JSON.stringify(times), (err) => console.log(err))
}

function measurePerformance(start, finish, func, funcName, iterations) {
    funcTimes = []
    for(i = 0; i < iterations; i++) {
        let t0 = performance.now();
        var result = func(start, finish);
        funcTimes.push(performance.now() - t0);
    }
    
    times[funcName] = funcTimes.reduce((total, x) => total + x)/funcTimes.length;
    return result;
}

function evaluateLowPerformanceFunctions(start, finish, iterations) {
    measurePerformance(start, finish, noOptimizations, "noOptimizations", iterations);
    measurePerformance(start, finish, pullUpPrinting, "pullUpPrinting", iterations);
    measurePerformance(start, finish, reducedModulos, "reducedModulos", iterations);
    measurePerformance(start, finish, counter, "counter", iterations);
    measurePerformance(start, finish, countByFour, "countByFour", iterations);
}

function evaluateHighPerformanceFunctions(start, finish, print, iterations) {
    let leapYearModulosResult = measurePerformance(start, finish, leapYearModulos, "leapYearModulos", iterations);
    let leapYearCounterResult = measurePerformance(start, finish, leapYearCounter, "leapYearCounter", iterations);
    let leapYearNoLoopsResult = measurePerformance(start, finish, leapYearNoLoops, "leapYearNoLoops", iterations);
    let noPrintReducedModulosResult = measurePerformance(start, finish, noPrintReducedModulos, "noPrintReducedModulos", iterations);
    let noPrintCounterResult = measurePerformance(start, finish, noPrintCounter, "noPrintCounter", iterations);
    let noPrintCountByFourResult = measurePerformance(start, finish, noPrintCountByFour, "noPrintCountByFour", iterations);
    if(print) {
        console.log(leapYearModulosResult);
        console.log(leapYearCounterResult);
        console.log(leapYearNoLoopsResult);
        console.log(noPrintReducedModulosResult);
        console.log(noPrintCounterResult);
        console.log(noPrintCountByFourResult);
    }
}


function noOptimizations(start, finish) {
    for (year = start; year < finish; year++) {
        let isDivisibleBy4 = year % 4 == 0;
        let isDivisibleBy100 = year % 100 == 0;
        let isDivisibleBy400 = year % 400 == 0;
        if (isDivisibleBy4 && (!isDivisibleBy100 || isDivisibleBy400)) {
            console.log(year);
        }
    }
}

// one optimization
function pullUpPrinting(start, finish) {
    let result = [];
    for (year = start; year < finish; year++) {
        let isDivisibleBy4 = year % 4 == 0;
        let isDivisibleBy100 = year % 100 == 0;
        let isDivisibleBy400 = year % 400 == 0;
        if (isDivisibleBy4 && (!isDivisibleBy100 || isDivisibleBy400)) {
            result.push(year);
        }
    }
    console.log(result);
}

function reducedModulos(start, finish) {
    for (year = start; year < finish; year++) {
        if (year % 4 == 0 && (year % 100 != 0 || year % 400 == 0)) {
            console.log(year);
        }
    }
}

function counter(start, finish) {
    while(start % 4 != 0) {
        start++;
    }
    let hundredCounter = Math.floor((start % 100.0) / 4.0);;
    let fourHundredCounter = Math.floor((start % 400.0) / 100.0);
	for (year = start; year < finish; year++) {
        if (hundredCounter == 100) {
			fourHundredCounter++;
			hundredCounter = 1;
			if (fourHundredCounter == 4) {
                console.log(year);
				fourHundredCounter = 0;
			}
		} else {
			hundredCounter++;
            console.log(year);
		}
	}
}

function countByFour(start, finish) {
    while(start % 4 != 0) {
        start++;
    }
    
    for (year = start; year < finish; year+=4) {
        let isDivisibleBy100 = year % 100 == 0;
        let isDivisibleBy400 = year % 400 == 0;
        if (!isDivisibleBy100 || isDivisibleBy400) {
            console.log(year);
        }
    }
}

// pull up (no) print + second optimization
function noPrintReducedModulos(start, finish) {
    let result = [];
    for (year = start; year < finish; year++) {
        if (year % 4 == 0 && (year % 100 != 0 || year % 400 == 0)) {
            result.push(year);
        }
    }
    return result;
}

function noPrintCountByFour(start, finish) {
    let result = [];
    while(start % 4 != 0) {
        start++;
    }
    
    for (year = start; year < finish; year+=4) {
        if (year % 100 != 0 || year % 400 == 0) {
            result.push(year);
        }
    }

    return result;
}

function noPrintCounter(start, finish) {
    let result = [];
    while(start % 4 != 0) {
        start++;
    }
    let hundredCounter = Math.floor((start % 100.0) / 4.0);;
    let fourHundredCounter = Math.floor((start % 400.0) / 100.0);
	for (year = start; year < finish; year++) {
        if (hundredCounter == 100) {
			fourHundredCounter++;
			hundredCounter = 1;
			if (fourHundredCounter == 4) {
                result.push(year);
				fourHundredCounter = 0;
			}
		} else {
			hundredCounter++;
            result.push(year);
		}
	}

    return result;
}

// fully optimized
function leapYearModulos(start, finish) {
	while (start % 4 != 0) {
		start++;
	}
    finish += 4;
	var results = [];
    for (year = start; year < finish; year+=4) {
        if(year % 100 == 0) {
            if (year % 400 == 0) {
                results.push(year);
            }
        } else {
            results.push(year)
        }
    }
    return results;
}

function leapYearCounter(start, finish) {
    finish += 4;
	var results = [];
    var mod = start % 4;
    if (mod != 0) {
        start += 4 - mod;
	}
    var hundredCounter = Math.floor((start % 100.0) / 4.0);;
    var fourHundredCounter = Math.floor((start % 400.0) / 100.0);
	for (year = start; year < finish; year+=4) {
        if (hundredCounter == 25) {
			fourHundredCounter++;
			hundredCounter = 1;
			if (fourHundredCounter == 4) {
			    results.push(year);
				fourHundredCounter = 0;
			}
		} else {
			hundredCounter++;
			results.push(year);
		}
	}
    return results;
}

function leapYearNoLoops(start, finish) {
    let mod = start % 4;
    if (mod != 0) {
        start += 4 - mod;
    }
    const len = Math.floor((finish - start) / 4) + 4;
    return Array(len).fill().map((_, index) => start + (index * 4)).filter(x => x % 100 != 0 || x % 400 == 0 );
}

if (require.main === module) { 
    main(); 
}