#!/usr/bin/env python3 
# -*- coding: utf-8 -*- 

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

## Get multiple pull requests diff or merge at a time.
## Formal checking (for naming or path errors) is possible adding some
## regex rule in the act_dict dictionary.
##
## Launch from repository specifying command  to execute (diff or merge)
## and pull request number.
## Example:
## ./multi_git.py diff 21,24 27 31-35
## gets the diff (-summary) between HEAD and origin/pr/21,
##                                           origin/pr/24,
##                                           origin/pr/27,
##                                           origin/pr/31,
##                                           origin/pr/32,
##                                           origin/pr/33,
##                                           origin/pr/34,
##                                           origin/pr/35

import sys
import subprocess, shlex
import re

base_url='https://github.com/strumet/strumet.github.io/tree/master/'

## Formal rules
act_dict = {
        'activities/0/': {
            'regex': re.compile('^\d{6}\.(jpg|png|jpeg)$', re.IGNORECASE),
            'url': base_url + 'activities/0#activity-0'},
        'activities/1/': {
            'regex': re.compile('^\d{6}\/', re.IGNORECASE),
            'url': base_url + 'activities/1#activity-1'},
        'activities/2/': {
            'regex': re.compile('^\d{6}\.pdf$', re.IGNORECASE),
            'url': base_url + 'activities/2#activity-2'},
        'activities/3/': {
            'regex': re.compile('^\d{6}\.(ifc|pdf)$', re.IGNORECASE),
            'url': base_url + 'activities/3#activity-3'},
        'activities/4/': {
            'regex': re.compile('^\d{6}\.(ifc|pdf)$', re.IGNORECASE),
            'url': base_url + 'activities/4#activity-4'},
        'activities/5/': {
            'regex': re.compile('^\d{6}\.(ifc|pdf)$', re.IGNORECASE),
            'url': base_url + 'activities/5#activity-5'},
        'activities/6/': {
            'regex': re.compile('^\d{6}\.pdf$', re.IGNORECASE),
            'url': base_url + 'activities/6#activity-6'},
        'activities/7/': {
            'regex': re.compile('^.*$', re.IGNORECASE),
            'url': base_url + 'activities/7#activity-7'},
        'projects/': {
            'regex': re.compile('^\d{6}\/', re.IGNORECASE),
            'url': base_url + 'projects#projects'},
        'exams/': {
            'regex': re.compile('^\d{6}\.pdf$', re.IGNORECASE),
            'url': base_url + 'exams#esame-finale'},
        }

## Functions
get_range = lambda li: [val for val in range(li[0], li[1]+1)]
get_format = lambda x: get_range(list(map(int, x.split('-')))) if '-' in x \
        else map(int, x.split(',')) 
get_path_url = lambda p: " pubblicata all'indirizzo " + act_dict[p]['url'] \
        if p in act_dict else '.'
## Create mail to send in case of errors
mail_body = lambda id_no, wrong_files, path: (
        "Ciao " + STUD_DICT[id_no][1].capitalize() + ",\n"
        "nella tua consegna sono presenti errori formali relativi ai file:\n"
        "\n" + ('').join(['* ' + f + '\n' for f in wrong_files]) + "\n"
        "Verifica che il nome, il formato e le cartelle dei file inviati "
        "corrispondano a quanto indicato nella pagina di istruzioni "
        "" + get_path_url(path) + "\n"
        "Un saluto,\nmf"
        )

## Variables, containers, regex
CMD = sys.argv[1]
RAW_PR = sys.argv[2:]
NESTED_PR = [get_format(i) for i in RAW_PR]
PR = [item for sublist in NESTED_PR for item in sublist]
## Get students data to prepare mail
STUDENTS_FILE = '/home/mf/Documents/uni/strumet/documents/status.csv'
STUD_LIST = [l.split(';') for l in 
        open(STUDENTS_FILE, encoding="ISO-8859-1").read().split('\n')]
STUD_DICT = {l[0]: l[1:4] for l in 
        STUD_LIST if len(l) > 3 and re.match('\d{6}', l[0])}
##
id_re = re.compile('/?(\d{6})')
reports = {}
mails = {}
commands = {
        'diff': lambda x: 'git diff --stat HEAD...origin/pr/' + str(x),
        'merge': lambda x: 'git merge origin/pr/' + str(x),
        'show': lambda x, filename: 'git show origin/pr/' + str(x) + \
                ':"' + filename + '" | file -'
        }


def main():
    for i in PR:
        print(commands[CMD](i))
        cmd = subprocess.run(shlex.split(commands[CMD](i)),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True)
        print(cmd.stdout)
        if len(cmd.stderr) > 0:
            print(cmd.stderr)
        ## Check formal correctness
        if CMD == 'diff':
            reports[str(i)] = []
            directories = [f for f in act_dict]
            ## Get filenames from diff output
            files = list(map(lambda x: x[:x.index('|')].strip(),
                cmd.stdout.strip().strip().split('\n')[:-1]))
            for f in files:
                if f.startswith('exams'):
                    print(f,)
                    cmd = subprocess.run(commands['show'](i, f), shell=True)
                for d in directories:
                    if d in f:
                        path = d
                        break
                    else:
                        path = ''
                filename = f[len(path):].replace('_', '-')
                if len(filename) > 0 and (path not in act_dict or
                        not act_dict[path]['regex'].search(filename)):
                    reports[str(i)].append(f)
            ## Remove empty reports
            if len(reports[str(i)]) == 0:
                del reports[str(i)]
            print()

    if CMD == 'diff' and len(reports) > 0:
        ## Create report of wrong files
        for d in reports:
            if len(reports[d]) > 0:
                id_no = id_re.search(reports[d][0]).group(1)
                print(d, ':')
                for f in reports[d]:
                    print('\t', f)
                mails[d] = mail_body(id_no, reports[d], path)
        ## Print out the mail text to send
        send_mail = None
        while send_mail not in ['n', 'y']:
            send_mail = input('\nPrepare mail?\n(y/n): ').lower()
            if send_mail == 'y':
                for m in mails:
                    print('\n' + m + ':\n' + mails[m])


main()
