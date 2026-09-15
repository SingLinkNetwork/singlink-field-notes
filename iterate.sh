#!/bin/sh
set -e
cd "$(dirname "$0")"
python3 generate.py
python3 verify.py
echo "iterate ok"
