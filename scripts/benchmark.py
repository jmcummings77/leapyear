#!/usr/bin/env python3
"""Check correctness, then benchmark each language sequentially on shared inputs."""

import argparse
import calendar
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METHODS = {
    'Python': ('no_print_reduced_modulos', 'no_print_counter', 'no_print_count_by_four',
               'leap_year_modulos', 'leap_year_counter', 'leap_bit_no_print',
               'leap_year_no_loops', 'leap_year_sets'),
    'Go': ('noPrintReducedModulos', 'noPrintCounter', 'noPrintCountByFour',
           'leapYearModulos', 'leapYearCounter', 'leapYear'),
    'JavaScript': ('noPrintReducedModulos', 'noPrintCounter', 'noPrintCountByFour',
                   'leapYearModulos', 'leapYearCounter', 'leapYearNoLoops'),
    'C#': ('NoPrintReducedModulos', 'NoPrintCounter', 'NoPrintCountByFour',
           'LeapYearModulos', 'LeapYearCounter', 'LeapYearLinq'),
}
STRATEGIES = ('Scan each year', 'Counter each year', 'Step by four',
              'Optimized modulo', 'Optimized counter')


def executable(name, fallbacks=()):
    path = shutil.which(name)
    if path:
        return path
    for path in fallbacks:
        if Path(path).is_file():
            return path
    raise SystemExit(f'{name} is required. Install it or add it to PATH before benchmarking.')


def run(command, cwd=ROOT):
    subprocess.run([str(value) for value in command], cwd=cwd, check=True)


def output(command):
    return subprocess.check_output(command, cwd=ROOT, text=True).strip()


def cpu_model():
    if sys.platform == 'darwin':
        try:
            return subprocess.check_output(['sysctl', '-n', 'machdep.cpu.brand_string'],
                                           text=True, stderr=subprocess.DEVNULL).strip()
        except (OSError, subprocess.CalledProcessError):
            pass
    return platform.processor() or 'unavailable'


def nonnegative(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError('must be nonnegative')
    return number


def positive(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError('must be positive')
    return number


def table(results):
    languages = ('Python', 'Go', 'JavaScript', 'C#')
    lines = ['| Strategy | Python | Go | JavaScript | C# |',
             '| --- | ---: | ---: | ---: | ---: |']
    for index, strategy in enumerate(STRATEGIES):
        values = [f'{results[language][METHODS[language][index]]:.3f}' for language in languages]
        lines.append('| ' + ' | '.join((strategy, *values)) + ' |')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start', type=int, default=1582)
    parser.add_argument('--finish', type=int, default=1000000,
                        help='Exclusive upper year (default: 1000000).')
    parser.add_argument('--iterations', type=positive, default=10)
    parser.add_argument('--warmups', type=nonnegative, default=3)
    parser.add_argument('--output', type=Path, default=ROOT / 'results/latest.json')
    args = parser.parse_args()
    # All four programs can represent this shared domain exactly.
    if not (-(2**31) <= args.start <= 2**31 - 1 and -(2**31) <= args.finish <= 2**31 - 1):
        parser.error('shared year bounds must fit in a signed 32-bit integer')
    if args.finish - args.start > 2**31 - 1:
        parser.error('the range length must fit in a signed 32-bit integer for C# LINQ')

    go = executable('go', ('/opt/homebrew/bin/go', '/usr/local/go/bin/go'))
    node = executable('node')
    dotnet = executable('dotnet', ('/usr/local/share/dotnet/dotnet',))
    print('Checking all four implementations before measuring...', flush=True)
    run([sys.executable, '-m', 'unittest', 'Python.test_leap_year', '-v'])
    run([go, 'test', './...'], cwd=ROOT / 'Go')
    run([node, '--test'], cwd=ROOT / 'JavaScript')
    run([dotnet, 'run', '--project', 'C_Sharp.Tests/C_Sharp.Tests.csproj',
         '--configuration', 'Release', '-p:UseSharedCompilation=false'])
    run([dotnet, 'build', 'C_Sharp/C_Sharp.csproj', '--configuration', 'Release',
         '--nologo', '-p:UseSharedCompilation=false'])

    with tempfile.TemporaryDirectory(prefix='leapyear-benchmark-') as directory:
        temporary = Path(directory)
        go_binary = temporary / ('leapyear.exe' if os.name == 'nt' else 'leapyear')
        run([go, 'build', '-o', go_binary, '.'], cwd=ROOT / 'Go')
        files = {language: temporary / f'{index}.json' for index, language in enumerate(METHODS)}
        positional = [args.start, args.finish, args.iterations]
        commands = {
            'Python': [sys.executable, ROOT / 'Python/leap_year.py', '--start', args.start,
                       '--finish', args.finish, '--iterations', args.iterations,
                       '--warmups', args.warmups, '--output', files['Python']],
            'Go': [go_binary, *positional, files['Go'], 'false', args.warmups],
            'JavaScript': [node, ROOT / 'JavaScript/leapYear.js', f'--start={args.start}',
                           f'--finish={args.finish}', '--iterations', args.iterations,
                           '--warmups', args.warmups, '--fileName', files['JavaScript']],
            'C#': [dotnet, ROOT / 'C_Sharp/bin/Release/net8.0/C_Sharp.dll',
                   *positional, files['C#'], 'false', args.warmups],
        }
        results = {}
        started_at = datetime.now(timezone.utc).isoformat()
        for language, command in commands.items():
            print(f'Measuring {language}...', flush=True)
            run(command)
            values = json.loads(files[language].read_text())
            if language == 'C#':
                values = {item['name']: item['average'] for item in values}
            if set(values) != set(METHODS[language]):
                raise ValueError(f'{language} emitted an unexpected set of benchmarks')
            if any(not isinstance(value, (int, float)) or not 0 <= value < float('inf')
                   for value in values.values()):
                raise ValueError(f'{language} emitted an invalid duration')
            results[language] = values

    sources = ('Python/leap_year.py', 'Go/leapYear.go', 'JavaScript/leapYear.js',
               'C_Sharp/LeapYear.cs', 'C_Sharp/C_Sharp.csproj', 'scripts/benchmark.py')
    report = {
        'started_at_utc': started_at,
        'finished_at_utc': datetime.now(timezone.utc).isoformat(),
        'environment': {
            'os': platform.platform(), 'architecture': platform.machine(), 'cpu': cpu_model(),
            'python': platform.python_version(), 'go': output([go, 'version']),
            'node': output([node, '--version']), 'dotnet_sdk': output([dotnet, '--version']),
            'dotnet_runtimes': [line.split(' [', 1)[0]
                               for line in output([dotnet, '--list-runtimes']).splitlines()],
        },
        'settings': {
            'start_inclusive': args.start, 'finish_exclusive': args.finish,
            'measured_iterations_per_method': args.iterations,
            'warmup_iterations_per_method': args.warmups, 'printing': False,
            'statistic': 'arithmetic mean', 'unit': 'milliseconds',
            'expected_leap_year_count': sum(calendar.isleap(year) for year in range(args.start, args.finish)),
            'execution': 'sequential language processes; warmups in each process; build and process startup excluded',
            'csharp_configuration': 'Release',
        },
        'source_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sources},
        'mean_ms': results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    print('\nMean milliseconds per method call:\n' + table(results))
    print(f'\nFull timings and environment saved to {args.output}')


if __name__ == '__main__':
    main()
