#!/bin/bash
cat *.md > blob
echo "Turtles: $(grep -i "turtle" blob | wc -l)
Pipes: $(grep "pipe" blob | wc -l)
Tools: $(grep "tool" blob | wc -l)" | python3 MLBarchart.py 
rm blob
