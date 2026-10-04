'use strict';

// Requires Node.js 20+. All methods use start <= year < finish.
const { performance } = require('node:perf_hooks');
const fs = require('node:fs');
const path = require('node:path');
const { parseArgs } = require('node:util');

function validateRange(start, finish) {
    if (!Number.isSafeInteger(start) || !Number.isSafeInteger(finish)) {
        throw new RangeError('start and finish must be safe integers');
    }
}

function validateSamples(iterations, warmups) {
    if (!Number.isSafeInteger(iterations) || iterations <= 0) {
        throw new RangeError('iterations must be a positive integer');
    }
    if (!Number.isSafeInteger(warmups) || warmups < 0) {
        throw new RangeError('warmups must be a nonnegative integer');
    }
}

// JavaScript's remainder is negative for negative years; counters need positive phases.
function modulo(value, divisor) {
    return ((value % divisor) + divisor) % divisor;
}

function measurePerformance(start, finish, func, iterations, warmups = 0) {
    validateRange(start, finish);
    validateSamples(iterations, warmups);
    for (let i = 0; i < warmups; i++) {
        func(start, finish);
    }
    let result;
    let total = 0;
    for (let i = 0; i < iterations; i++) {
        const before = performance.now();
        result = func(start, finish);
        total += performance.now() - before;
    }
    return { result, milliseconds: total / iterations };
}

function evaluateLowPerformanceFunctions(start, finish, iterations, warmups = 0) {
    const times = {};
    for (const method of PRINTING_METHODS) {
        times[method.name] = measurePerformance(start, finish, method, iterations, warmups).milliseconds;
    }
    return times;
}

function evaluateHighPerformanceFunctions(start, finish, print, iterations, warmups = 0) {
    const times = {};
    for (const method of RETURNING_METHODS) {
        const measurement = measurePerformance(start, finish, method, iterations, warmups);
        times[method.name] = measurement.milliseconds;
        if (print && measurement.result.length > 0) {
            console.log(measurement.result.join('\n'));
        }
    }
    return times;
}

function evaluatePerformance(start, finish, iterations, runPrint = false, warmups = 0) {
    validateRange(start, finish);
    validateSamples(iterations, warmups);
    const times = runPrint ? evaluateLowPerformanceFunctions(start, finish, iterations, warmups) : {};
    return Object.assign(times, evaluateHighPerformanceFunctions(start, finish, false, iterations, warmups));
}

function noOptimizations(start, finish) {
    validateRange(start, finish);
    for (let year = start; year < finish; year++) {
        const isDivisibleBy4 = year % 4 === 0;
        const isDivisibleBy100 = year % 100 === 0;
        const isDivisibleBy400 = year % 400 === 0;
        if (isDivisibleBy4 && (!isDivisibleBy100 || isDivisibleBy400)) {
            console.log(year);
        }
    }
}

// One optimization.
function pullUpPrinting(start, finish) {
    validateRange(start, finish);
    const result = [];
    for (let year = start; year < finish; year++) {
        const isDivisibleBy4 = year % 4 === 0;
        const isDivisibleBy100 = year % 100 === 0;
        const isDivisibleBy400 = year % 400 === 0;
        if (isDivisibleBy4 && (!isDivisibleBy100 || isDivisibleBy400)) {
            result.push(year);
        }
    }
    if (result.length > 0) console.log(result.join('\n'));
}

function reducedModulos(start, finish) {
    validateRange(start, finish);
    for (let year = start; year < finish; year++) {
        if (year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0)) {
            console.log(year);
        }
    }
}

function counter(start, finish) {
    validateRange(start, finish);
    let fourCounter = modulo(start, 4);
    let hundredCounter = modulo(start, 100);
    let fourHundredCounter = modulo(start, 400);
    for (let year = start; year < finish; year++) {
        if (fourCounter === 0 && (hundredCounter !== 0 || fourHundredCounter === 0)) {
            console.log(year);
        }
        fourCounter++;
        hundredCounter++;
        fourHundredCounter++;
        if (fourCounter === 4) fourCounter = 0;
        if (hundredCounter === 100) hundredCounter = 0;
        if (fourHundredCounter === 400) fourHundredCounter = 0;
    }
}

function countByFour(start, finish) {
    validateRange(start, finish);
    while (start % 4 !== 0) start++;
    for (let year = start; year < finish; year += 4) {
        const isDivisibleBy100 = year % 100 === 0;
        const isDivisibleBy400 = year % 400 === 0;
        if (!isDivisibleBy100 || isDivisibleBy400) {
            console.log(year);
        }
    }
}

// Pull up (no) print + second optimization.
function noPrintReducedModulos(start, finish) {
    validateRange(start, finish);
    const result = [];
    for (let year = start; year < finish; year++) {
        if (year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0)) {
            result.push(year);
        }
    }
    return result;
}

function noPrintCountByFour(start, finish) {
    validateRange(start, finish);
    const result = [];
    while (start % 4 !== 0) start++;
    for (let year = start; year < finish; year += 4) {
        if (year % 100 !== 0 || year % 400 === 0) {
            result.push(year);
        }
    }
    return result;
}

function noPrintCounter(start, finish) {
    validateRange(start, finish);
    const result = [];
    let fourCounter = modulo(start, 4);
    let hundredCounter = modulo(start, 100);
    let fourHundredCounter = modulo(start, 400);
    for (let year = start; year < finish; year++) {
        if (fourCounter === 0 && (hundredCounter !== 0 || fourHundredCounter === 0)) {
            result.push(year);
        }
        fourCounter++;
        hundredCounter++;
        fourHundredCounter++;
        if (fourCounter === 4) fourCounter = 0;
        if (hundredCounter === 100) hundredCounter = 0;
        if (fourHundredCounter === 400) fourHundredCounter = 0;
    }
    return result;
}

// Fully optimized.
function leapYearModulos(start, finish) {
    validateRange(start, finish);
    while (start % 4 !== 0) start++;
    const result = [];
    for (let year = start; year < finish; year += 4) {
        if (year % 100 === 0) {
            if (year % 400 === 0) result.push(year);
        } else {
            result.push(year);
        }
    }
    return result;
}

function leapYearCounter(start, finish) {
    validateRange(start, finish);
    start += (4 - modulo(start, 4)) % 4;
    const result = [];
    let hundredCounter = modulo(start, 100) / 4;
    let fourHundredCounter = Math.floor(modulo(start, 400) / 100);
    for (let year = start; year < finish; year += 4) {
        if (hundredCounter !== 0 || fourHundredCounter === 0) {
            result.push(year);
        }
        hundredCounter++;
        if (hundredCounter === 25) {
            hundredCounter = 0;
            fourHundredCounter++;
            if (fourHundredCounter === 4) fourHundredCounter = 0;
        }
    }
    return result;
}

function leapYearNoLoops(start, finish) {
    validateRange(start, finish);
    start += (4 - modulo(start, 4)) % 4;
    const length = Math.max(0, Math.ceil((finish - start) / 4));
    return Array.from({ length }, (_, index) => start + index * 4)
        .filter(year => year % 100 !== 0 || year % 400 === 0);
}

const PRINTING_METHODS = [noOptimizations, pullUpPrinting, reducedModulos, counter, countByFour];
const RETURNING_METHODS = [leapYearModulos, leapYearCounter, leapYearNoLoops,
    noPrintReducedModulos, noPrintCounter, noPrintCountByFour];

function integerOption(value, name) {
    if (!/^-?\d+$/.test(value) || !Number.isSafeInteger(Number(value))) {
        throw new RangeError(`${name} must be a safe integer`);
    }
    return Number(value);
}

function main(argv = process.argv.slice(2)) {
    const { values } = parseArgs({
        args: argv,
        options: {
            start: { type: 'string', default: '1582' },
            finish: { type: 'string', default: '24000' },
            iterations: { type: 'string', default: '100' },
            warmups: { type: 'string', default: '0' },
            fileName: { type: 'string', default: path.join(__dirname, 'javascript_results.json') },
            print: { type: 'boolean', default: false },
        },
    });
    const times = evaluatePerformance(
        integerOption(values.start, 'start'), integerOption(values.finish, 'finish'),
        integerOption(values.iterations, 'iterations'), values.print, integerOption(values.warmups, 'warmups'),
    );
    fs.writeFileSync(values.fileName, JSON.stringify(times));
    return times;
}

module.exports = {
    ...Object.fromEntries([...PRINTING_METHODS, ...RETURNING_METHODS].map(method => [method.name, method])),
    measurePerformance,
    evaluateLowPerformanceFunctions,
    evaluateHighPerformanceFunctions,
    evaluatePerformance,
    main,
};

if (require.main === module) {
    try {
        main();
    } catch (error) {
        console.error(error.message);
        process.exitCode = 1;
    }
}
