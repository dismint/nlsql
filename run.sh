#!/usr/bin/env bash

set -a
source .env
set +a

python3 ./src/main.py $@
