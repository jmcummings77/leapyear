'use strict';

const assert = require('node:assert/strict');
const { test } = require('node:test');
const { performance } = require('node:perf_hooks');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const leapYear = require('./leapYear');

const returningNames = ['leapYearModulos', 'leapYearCounter', 'leapYearNoLoops',
    'noPrintReducedModulos', 'noPrintCounter', 'noPrintCountByFour'];
const printingNames = ['noOptimizations', 'pullUpPrinting', 'reducedModulos', 'counter', 'countByFour'];

function expectedYears(start, finish) {
    const result = [];
    for (let year = start; year < finish; year++) {
        // Date provides an independent proleptic Gregorian-calendar oracle, including years 0–99.
        const date = new Date(0);
        date.setUTCFullYear(year, 1, 29);
        if (date.getUTCMonth() === 1) result.push(year);
    }
    return result;
}

function capturePrinting(callback) {
    const values = [];
    const originalLog = console.log;
    console.log = (...args) => {
        for (const value of args.flat()) {
            values.push(...String(value).split(/\s+/).filter(Boolean).map(Number));
        }
    };
    try {
        callback();
    } finally {
        console.log = originalLog;
    }
    return values;
}

function assertAllMethods(start, finish, expected) {
    for (const name of returningNames) {
        assert.deepEqual(leapYear[name](start, finish), expected, `${name}(${start}, ${finish})`);
    }
    for (const name of printingNames) {
        const result = capturePrinting(() => leapYear[name](start, finish));
        assert.deepEqual(result, expected, `${name}(${start}, ${finish})`);
    }
}

function temporaryDirectory(t) {
    const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'leap-year-js-'));
    t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
    return directory;
}

function runCli(args, source = path.join(__dirname, 'leapYear.js')) {
    return spawnSync(process.execPath, [source, ...args], { encoding: 'utf8' });
}

function assertTimings(times, includePrinting = false) {
    const expected = includePrinting ? [...printingNames, ...returningNames] : returningNames;
    assert.deepEqual(Object.keys(times).sort(), [...expected].sort());
    for (const value of Object.values(times)) {
        assert.equal(typeof value, 'number');
        assert.ok(Number.isFinite(value) && value >= 0);
    }
}

test('reported empty range and explicit century/boundary regressions', () => {
    const cases = [
        [1582, 1582, []], [1582, 1584, []], [1582, 1585, [1584]],
        [1584, 1584, []], [1584, 1585, [1584]], [1585, 1584, []],
        [1596, 1605, [1596, 1600, 1604]], [1600, 1601, [1600]],
        [1696, 1705, [1696, 1704]], [1700, 1701, []],
        [1896, 1905, [1896, 1904]], [1996, 2005, [1996, 2000, 2004]],
        [2096, 2105, [2096, 2104]], [1704, 1600, []], [-4, 5, [-4, 0, 4]],
    ];
    for (const [start, finish, expected] of cases) assertAllMethods(start, finish, expected);
});

test('every Gregorian cycle phase and endpoint residue matches the native calendar', () => {
    for (let start = 1582; start < 1982; start++) {
        for (const length of [-5, 0, 1, 2, 3, 4, 5, 24, 100, 401]) {
            assertAllMethods(start, start + length, expectedYears(start, start + length));
        }
    }
});

test('multiple cycles and negative years are sorted, unique, and correct', () => {
    for (const [start, finish] of [[1, 2401], [-801, 402]]) {
        assertAllMethods(start, finish, expectedYears(start, finish));
    }
});

test('all methods reject noninteger or unsafe bounds before looping', () => {
    for (const name of [...returningNames, ...printingNames]) {
        for (const value of [NaN, Infinity, 1582.5, '1582', Number.MAX_SAFE_INTEGER + 1]) {
            assert.throws(() => leapYear[name](value, 2020), /safe integers/);
            assert.throws(() => leapYear[name](1582, value), /safe integers/);
        }
    }
});

test('measurement averages total milliseconds, preserves fractions, and returns the last result', t => {
    const readings = [0, 1250, 2000, 2000.125];
    t.mock.method(performance, 'now', () => readings.shift());
    let calls = 0;
    const measured = leapYear.measurePerformance(1582, 1601, () => ++calls, 2);
    assert.deepEqual(measured, { result: 2, milliseconds: 625.0625 });
    assert.equal(calls, 2);
    assert.equal(readings.length, 0);
});

test('warmup callbacks run before measurement and are excluded from its average', t => {
    const readings = [0, 1250, 2000, 2000.125];
    let calls = 0;
    t.mock.method(performance, 'now', () => {
        assert.ok(calls >= 3, 'clock should not be read for warmups');
        return readings.shift();
    });
    const measured = leapYear.measurePerformance(1582, 1601, () => ++calls, 2, 3);
    assert.deepEqual(measured, { result: 5, milliseconds: 625.0625 });
    assert.equal(calls, 5);
    assert.equal(readings.length, 0);
});

test('invalid iteration and warmup counts never invoke the measured function', () => {
    const callback = () => assert.fail('invalid samples must not run');
    for (const iterations of [0, -1, 1.5, NaN, Infinity, '1']) {
        assert.throws(() => leapYear.measurePerformance(1582, 1601, callback, iterations), /positive integer/);
        assert.throws(() => leapYear.evaluatePerformance(1582, 1601, iterations), /positive integer/);
    }
    for (const warmups of [-1, 1.5, NaN, Infinity, '1']) {
        assert.throws(() => leapYear.measurePerformance(1582, 1601, callback, 1, warmups), /nonnegative integer/);
        assert.throws(() => leapYear.evaluatePerformance(1582, 1601, 1, false, warmups), /nonnegative integer/);
    }
});

test('each benchmark run owns its samples and respects the print flag', t => {
    let tick = 0;
    t.mock.method(performance, 'now', () => tick++);
    let first;
    const printed = capturePrinting(() => { first = leapYear.evaluatePerformance(1600, 1601, 2, true, 1); });
    assertTimings(first, true);
    assert.deepEqual(printed, Array(printingNames.length * 3).fill(1600));
    assert.ok(Object.values(first).every(value => value === 1));

    t.mock.method(performance, 'now', () => { tick += 2; return tick; });
    let second;
    assert.deepEqual(capturePrinting(() => { second = leapYear.evaluatePerformance(1582, 1582, 1); }), []);
    assert.deepEqual(second, Object.fromEntries(returningNames.map(name => [name, 2])));
    assert.ok(Object.values(first).every(value => value === 1), 'previous results remain unchanged');
});

test('benchmark helpers return their own timing maps and optional result printing', () => {
    let timings;
    const output = capturePrinting(() => {
        timings = leapYear.evaluateHighPerformanceFunctions(1696, 1705, true, 1);
    });
    assertTimings(timings);
    assert.deepEqual(output, Array.from({ length: returningNames.length }, () => [1696, 1704]).flat());
});

test('algorithms and benchmark helpers do not leak accidental globals', () => {
    const before = new Set(Object.getOwnPropertyNames(globalThis));
    capturePrinting(() => leapYear.evaluatePerformance(1596, 1605, 1, true));
    assert.deepEqual(Object.getOwnPropertyNames(globalThis).filter(name => !before.has(name)), []);
});

test('CLI writes valid numeric JSON to the requested file without print output', t => {
    const output = path.join(temporaryDirectory(t), 'results.json');
    const child = runCli(['--start=-4', '--finish=5', '--iterations=2', '--warmups=1', '--fileName', output]);
    assert.equal(child.status, 0, child.stderr);
    assert.equal(child.stdout, '');
    assert.equal(child.stderr, '');
    assertTimings(JSON.parse(fs.readFileSync(output, 'utf8')));
});

test('CLI print flag runs printing benchmarks and includes their timings', t => {
    const output = path.join(temporaryDirectory(t), 'results.json');
    const child = runCli(['--start', '1600', '--finish', '1601', '--iterations', '1', '--print', '--fileName', output]);
    assert.equal(child.status, 0, child.stderr);
    assert.match(child.stdout, /1600/);
    assertTimings(JSON.parse(fs.readFileSync(output, 'utf8')), true);
});

test('CLI printing keeps the entire sequence beyond the console array truncation limit', t => {
    const output = path.join(temporaryDirectory(t), 'results.json');
    const child = runCli(['--start', '1', '--finish', '2401', '--iterations', '1', '--print', '--fileName', output]);
    assert.equal(child.status, 0, child.stderr);
    const expected = Array.from({ length: printingNames.length }, () => expectedYears(1, 2401)).flat();
    assert.deepEqual(child.stdout.trim().split(/\s+/).map(Number), expected);
    assertTimings(JSON.parse(fs.readFileSync(output, 'utf8')), true);
});

test('CLI default output resolves beside the script without external packages', t => {
    const directory = temporaryDirectory(t);
    const source = path.join(directory, 'leapYear.js');
    fs.copyFileSync(path.join(__dirname, 'leapYear.js'), source);
    const child = runCli(['--start', '1582', '--finish', '1582', '--iterations', '1'], source);
    assert.equal(child.status, 0, child.stderr);
    assertTimings(JSON.parse(fs.readFileSync(path.join(directory, 'javascript_results.json'), 'utf8')));
});

test('CLI rejects bad options without writing misleading timing output', t => {
    const output = path.join(temporaryDirectory(t), 'results.json');
    const cases = [
        ['--iterations', '0'], ['--iterations=-1'], ['--iterations', '1.5'],
        ['--warmups=-1'], ['--warmups', '1.5'], ['--start', 'not-a-year'],
        ['--finish', 'Infinity'], ['--start', '9007199254740992'], ['--unknown'], ['--start'],
    ];
    for (const args of cases) {
        const child = runCli(['--fileName', output, ...args]);
        assert.equal(child.status, 1, args.join(' '));
        assert.notEqual(child.stderr, '');
        assert.equal(fs.existsSync(output), false);
    }
});
