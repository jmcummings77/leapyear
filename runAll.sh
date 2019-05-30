#!/bin/bash


start=1582
finish=2400000
iterations=25
py_file="./results/py_results.json"
go_file="./results/go_results.json"
js_file="./results/js_results.json"
cs_file="./results/cs_results.json"
runprint=false

python3 ./Python/leap_year.py --start $start --finish $finish --iterations $iterations --output $py_file
go run l./Go/eapYear.go $start $finish $iterations $go_file $runprint
node ./JavaScript/leapYear.js --start $start --finish $finish --iterations $iterations --fileName $js_file --print
cd ./C_Sharp
dotnet run $start $finish  $iterations $cs_file $runprint
