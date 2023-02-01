#!/usr/bin/env python3
import os
# parse the rai output log file to get the correctness


# 100% correctness should get something like "All tests passed (66956 assertions in 1 test case)" near the end
# faulty code may get two lines
# test cases: 1 | 1 failed
# assertions: 2 | 1 passed | 1 failed

def _parse_log(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if "All tests passed" in line:
                print("100% correctness")
                return
            elif line.startswith("test cases"):
                # extract the number of test cases and failures
                num_test_cases = int(line.split("|")[0].split(":")[1])
                num_failures = int(line.split("|")[1].split(":")[1])
            elif line.startswith("assertions"):
                num_assertions = int(line.split("|")[0].split(":")[1])
                num_passed = int(line.split("|")[1].split(":")[1])
                num_failed = int(line.split("|")[2].split(":")[1])
        # print test cases, failures, assertions, passed, failed
        print("test cases: {} | {}, failures: {} | {} | {}".format(num_test_cases, num_failures, num_assertions,
                                                                   num_passed, num_failed))


def parse_log(submission_prefix,netid):
    _parse_log(os.path.join("out","{}.{}.log".format(submission_prefix, netid)))

def parse_all_logs(submission_prefix, netids):
    for netid in netids:
        parse_log(submission_prefix, netid)
