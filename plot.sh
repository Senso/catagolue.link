#!/bin/bash

cat header.html > /var/www/html/stats/index.html

for rule in $(cat rules.txt); do 
    okname=$(echo ${rule} | sed "s/\//_/")
    OUT=$(wget "https://catagolue.appspot.com/textcensus/${rule}/objcount" -O ~/catagolue/${okname}-`date +%Y%m%d` 1>/dev/null 2>&1)
done

for pattern in $(cat rules.txt); do
    orig_pat=$pattern
    pattern=$(echo ${pattern} | sed "s/\//_/")
    rm "catagolue/${pattern}.dat"
    for cronfile in `ls catagolue/${pattern}-*`; do
        last=$(tail -n 1 ${cronfile} | sed 's/Total objects: //')
        run_date=$(echo ${cronfile} | sed "s/catagolue\/${pattern}\-//")
        echo -e "${run_date} ${last}" >> "catagolue/${pattern}.dat"
    done

    gnuplot << EOF
set title "${pattern}"
set xlabel "Date"
set ylabel "Total\nObjects"
set datafile separator " "
set xdata time
set style data lines
set style line 1 lt 2 lc rgb "blue" lw 3
set term png size 800,600 noenhanced font "Arial,10"
set output "/var/www/html/stats/${pattern}.png"
set timefmt "%Y%m%d"
set format x "%m-%d\n%Y"
set grid xtics lt 0 lw 1 lc rgb "#bbbbbb"
set grid ytics lt 0 lw 1 lc rgb "#bbbbbb"
set xtics axis in 172800
plot "catagolue/${pattern}.dat" using 1:2 ls 1 title ''
EOF

    cat << EOF >> /var/www/html/stats/index.html
<div style='float:left; overflow: hidden; text-align:center;'>
<strong><a href="https://catagolue.appspot.com/census/${orig_pat}" target="_blank">${orig_pat}</a></strong> <br />
<a href="${pattern}.png">
    <img src="${pattern}.png" width=300 height=200>
</a>
</div>

EOF

done

cat footer.html >> /var/www/html/stats/index.html

