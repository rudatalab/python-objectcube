#!/bin/bash

export OBJECTCUBE_DB_PORT=5435

scripts/o3 clean
scripts/o3 setup
scripts/o3 start start_pq
scripts/o3 test
scripts/o3 start stop_pq
scripts/o3 test pep8 > "pep8.txt" || true
