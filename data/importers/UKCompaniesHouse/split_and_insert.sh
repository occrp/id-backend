#!/bin/bash

NEO4JSHELL="/home/id/install/neo4j-community-2.1.7/bin/neo4j-shell"

echo "Splitting $1 for neo4j insert"
split -l 50000 $1.csv ins-
for a in ins-??; do head -n 1 $1.csv > $a.csv && cat $a >> $a.csv; done

for a in ins-??.csv; do
	echo "Doing part $a"
	p="$(pwd)/$a"
        cat $1.cql | sed "s:%PATH%:$p:" | $NEO4JSHELL
done;

rm ins-*
echo "Done!"
