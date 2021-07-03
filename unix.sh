#!/bin/sh
for a in $(cat DEPS.txt); do
	python3 -m pip install $a
done
python3 src/tprts.py
