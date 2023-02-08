#!/usr/bin/env python3
import os
# parse the rai output log file to get the correctness


# 100% correctness should get something like "All tests passed (66956 assertions in 1 test case)" near the end
# faulty code may get two lines
# test cases: 1 | 1 failed
# assertions: 2 | 1 passed | 1 failed

def _parse_log(filename):
    with open(filename, 'r') as f:
        num_test_cases = -1
        num_cases_passed = -1
        num_cases_failed = -1
        num_assertions = -1
        num_assertions_passed = -1
        num_assertions_failed = -1
        #print(filename)
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if "All tests passed" in line:
                print(filename+" 100% correctness")
                return
            elif line.startswith("test cases"):
                # extract the number of test cases and failures
                num_test_cases = int(line.split("|")[0].split(":")[1])
                if len(line.split("|")) > 2:
                    num_cases_passed = int(line.split("|")[1].split()[0])
                    num_cases_failed = int(line.split("|")[2].split()[0])
                else:
                    num_cases_passed = 0
                    num_cases_failed = int(line.split("|")[1].split()[0])
            elif line.startswith("assertions"):
                num_assertions = int(line.split("|")[0].split(":")[1])
                if len(line.split("|")) > 2:
                    num_assertions_passed = int(line.split("|")[1].split()[0])
                    num_assertions_failed = int(line.split("|")[2].split()[0])
                else:
                    num_assertions_passed = 0
                    num_assertions_failed = int(line.split("|")[1].split()[0])
        # print test cases, failures, assertions, passed, failed
        
        print(filename+" test cases: {} | {} | {}, failures: {} | {} | {}".format(num_test_cases, num_cases_passed, num_cases_failed, num_assertions,
                                                                   num_assertions_passed, num_assertions_failed))


def parse_log(submission_prefix,netid):
    _parse_log(os.path.join("out","{}.{}.log".format(submission_prefix, netid)))

def parse_all_logs(submission_prefix, netids):
    for netid in netids:
        parse_log(submission_prefix, netid)

if __name__ == "__main__":
    parse_log("scatter","kunwu2")
