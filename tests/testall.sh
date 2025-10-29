#!/bin/bash

python3 -m unittest discover -s unit -p "test_*.py" && \
    python3 -m unittest discover -s integration -p "test_*.py"

