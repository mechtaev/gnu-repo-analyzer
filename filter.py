#!/usr/bin/env python3

import os
import difflib
import re
import csv
from git import Repo

count = 0

# projects = ['grep', 'make', 'gzip', 'bash', 'tar', 'coreutils']
projects = ['make']
result_file = open('result.csv', 'w')
writer = csv.writer(result_file)

writer.writerow(['plus_count', 'minus_count', 'array', 'pointer', 'struct', 'url'])
for project in projects:

    repo = Repo(project)

    for commit in repo.iter_commits("master"):
        if len(commit.parents) == 0:
            continue
        diffIndex = commit.diff(commit.parents[0])

        changed_tests = False

        for diff in diffIndex.iter_change_type('A'):
            if re.match('.*test.*.sh', diff.b_path):
                changed_tests = True

        modified_source = []
        for diff in diffIndex.iter_change_type('M'):

            if re.match('.*test.*.sh', diff.b_path):
                changed_tests = True

            _, extension = os.path.splitext(diff.a_path)
            if extension == '.c':
                modified_source.append(diff)
        if len(modified_source) == 0 or len(modified_source) > 2 or not changed_tests:
            continue

        too_long = False
        has_array = False
        has_struct = False
        has_pointer = False

        plus_count = 0
        minus_count = 0

        for diff in modified_source:
            b = diff.b_blob.data_stream.read()
            if not isinstance(b, str):
                b = b.decode("latin-1")
            a = diff.a_blob.data_stream.read()
            if not isinstance(a, str):
                a = a.decode("latin-1")
            ud = difflib.unified_diff(b.splitlines(keepends=True),
                                      a.splitlines(keepends=True), n=0)
            for line in ud:
                if line.startswith('-'):
                    if re.match('.*\[.*\].*', line):
                        has_array = True
                    if re.match('.*memset.*', line):
                        has_array = True
                    if re.match('.*memcpy.*', line):
                        has_array = True
                    if re.match('.*->.*', line):
                        has_struct = True
                    if re.match('.*\*.*', line):
                        has_pointer = True
                    minus_count = minus_count + 1
                if line.startswith('+'):
                    if re.match('.*\[.*\].*', line):
                        has_array = True
                    if re.match('.*memset.*', line):
                        has_array = True
                    if re.match('.*memcpy.*', line):
                        has_array = True
                    if re.match('.*->.*', line):
                        has_struct = True
                    if re.match('.*\*.*', line):
                        has_pointer = True
                    plus_count = plus_count + 1
            if plus_count + minus_count > 20:
                too_long = True

        # if too_long or not changed_tests or not (has_array or has_pointer or has_struct):
        if too_long:
            continue

        #     for line in ud:
        #         line_num += 1
        # if line_num > 15:
        #     print('too long')
        #     continue
        print('plus_count:', plus_count, 'minus_count:', minus_count)

        count = count + 1

        url_str = "http://git.savannah.gnu.org/cgit/{}.git/commit/?id={}".format(project, commit.hexsha)
        print(url_str)
        array_str = ''
        pointer_str = ''
        struct_str = ''
        if has_array:
            array_str = 'ARRAY'
            print(array_str)
        if has_pointer:
            pointer_str = 'POINTER'
            print(pointer_str)
        if has_struct:
            struct_str = 'STRUCT'
            print(struct_str)
        writer.writerow([str(plus_count), str(minus_count), array_str, pointer_str, struct_str, url_str])


print("Total: {}".format(count))
result_file.close()