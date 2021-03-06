#!/usr/bin/python
#
# Copyright 2015 The ANGLE Project Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# perf_test_runner.py:
#   Helper script for running and analyzing perftest results. Runs the
#   tests in an infinite batch, printing out the mean and standard
#   deviation of the population continuously.
#

import subprocess
import sys
import os

# You might have to re-order these to find the specific version you want.
perftests_paths = ['out/Release', 'build/Release_x64', 'build/Release_Win32']
metric = 'score'

scores = []

# Danke to http://stackoverflow.com/a/27758326
def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        raise ValueError('mean requires at least one data point')
    return float(sum(data))/float(n) # in Python 2 use sum(data)/float(n)

def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((float(x)-c)**2 for x in data)
    return ss

def pstdev(data):
    """Calculates the population standard deviation."""
    n = len(data)
    if n < 2:
        raise ValueError('variance requires at least two data points')
    ss = _ss(data)
    pvar = ss/n # the population variance
    return pvar**0.5

def truncated_list(data, n):
    """Compute a truncated list, n is truncation size"""
    if len(data) < n * 2:
        raise ValueError('list not large enough to truncate')
    return sorted(data)[n:-n]

def truncated_mean(data, n):
    return mean(truncated_list(data, n))

def truncated_stddev(data, n):
    return pstdev(truncated_list(data, n))

perftests_path = ""

# TODO(jmadill): Linux binaries
for path in perftests_paths:
    perftests_path = os.path.join(path, 'angle_perftests.exe')
    if os.path.exists(perftests_path):
        break

if not os.path.exists(perftests_path):
    print("Cannot find angle_perftests.exe!")
    sys.exit(1)

test_name = "DrawCallPerfBenchmark.Run/d3d11_null"

if len(sys.argv) >= 2:
    test_name = sys.argv[1]

# Infinite loop of running the tests.
while True:
    output = subprocess.check_output([perftests_path, '--gtest_filter=' + test_name])

    start_index = output.find(metric + "=")
    if start_index == -1:
        print("Did not find test output")
        sys.exit(1)

    start_index += len(metric) + 2

    end_index = output[start_index:].find(" ")
    if end_index == -1:
        print("Error parsing output")
        sys.exit(2)

    end_index += start_index

    score = int(output[start_index:end_index])
    sys.stdout.write("score: " + str(score))

    scores.append(score)
    sys.stdout.write(", mean: " + str(mean(scores)))

    if (len(scores) > 1):
        sys.stdout.write(", stddev: " + str(pstdev(scores)))

    if (len(scores) > 7):
        trucation_n = len(scores) >> 3
        sys.stdout.write(", truncated mean: " + str(truncated_mean(scores, trucation_n)))
        sys.stdout.write(", stddev: " + str(truncated_stddev(scores, trucation_n)))

    print("")
