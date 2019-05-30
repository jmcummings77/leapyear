#!/bin/bash


start=1582
finish=2400000
iterations=25
py_file="/Users/jmcummings/Source/interviews/results/py_results.json"
go_file="/Users/jmcummings/Source/interviews/results/go_results.json"
js_file="/Users/jmcummings/Source/interviews/results/js_results.json"
cs_file="/Users/jmcummings/Source/interviews/results/cs_results.json"
runprint=false

python3 ./leap_year.py --start $start --finish $finish --iterations $iterations --output $py_file
go run leapYear.go $start $finish $iterations $go_file $runprint
node ./leapYear.js --start $start --finish $finish --iterations $iterations --fileName $js_file --print
dotnet run $start $finish  $iterations $cs_file $runprint
