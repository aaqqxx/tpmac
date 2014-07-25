#!/usr/bin/env python
# vi: ts=4 sw=4

from __future__ import print_function
import os
import sys
import re

from . import util

ranges = {
    'motor': [('%.2d' % x, [('xx', '%d' % x)]) for x in range(1, 33)],
    'macro': [('%d' % n, [(' n ', ' %d' % n)]) for n in range(1, 3)],
    'servo' : [('%d%d' % (m, n),
               [('Servo IC m', 'Servo IC %d' % m),
               ('Channel n', 'Channel %d' % n)])
               for m in range(0, 10) for n in range(1, 5)],
    'servo0' : [('%d0' % m,
                [('Servo IC m', 'Servo IC %d' % m)])
                for m in range(0, 10)],
    }


def cs_range():
    cs = 1
    ret = []
    for s in range(5, 7):
        if s == 0:
            x_range = range(1, 10)
        else:
            x_range = range(1, 7)

        for x in x_range:
            ret.append(('%s%s' % (s, x), [(' x ', ' %d ' % cs)]))
            cs += 1
    return ret

ranges['cs'] = cs_range()

def ivar_to_int(ivar):
    ivar = ivar.upper()
    if not ivar.startswith('I'):
        raise ValueError('not I variable')
    
    if '/' in ivar or '-' in ivar:
        raise ValueError('ivar range')

    return int(ivar[1:])

def int_to_ivar(i):
    return 'I%d' % i

ivars = {}

def eval_ivar(f, ivar, category, desc):
    if '/' in ivar:
        for iv in ivar.split('/'):
            eval_ivar(f, iv, category, desc)
        return
    elif '-' in ivar:
        r0, r1 = [ivar_to_int(iv) for iv in ivar.split('-')]
        for i in range(r0, r1 + 1):
            eval_ivar(f, int_to_ivar(i), category, desc)
    else: 
        try:
            ivar_to_int(ivar)
        except:
            print('Failed: %s' % ivar)
        else:
            print('%s\t%s\t%s' % (ivar, desc, category), file=f)
        
            if ivar in ivars:
                print('Duplicate', ivar, ivars[ivar], '//', (category, desc))

            ivars[ivar] = (category, desc)

def replace_multiple(s, *from_to):
    for from_, to in from_to:
        s = s.replace(from_, to)
    return s

def generate_ivar_info(input_fn, output_fn):
    category = ''
    with open(output_fn, 'wt') as f:
        print('# vi: ts=30 sw=30', file=f)
        with open(input_fn, 'rt') as inf:
            for line in inf.readlines():
                line = line.strip()
                if line.startswith('*'):
                    category = line[1:].strip()
                    continue
                elif line.startswith('#'):
                    continue

                if 'Motor xx' in line:
                    class_, replace = 'motor', 'xx'
                elif 'Servo IC m Channel n' in line:
                    class_, replace = 'servo', 'mn'
                elif 'Servo IC m' in line:
                    class_, replace = 'servo0', 'm'
                elif ('MACRO IC Channel n' in line) or ('MACRO IC Encoder n' in line):
                    class_, replace = 'macro', 'n'
                elif 'Coordinate System' in line:
                    class_, replace = 'cs', 'sx'
                else:
                    class_ = ''
                
                # print('->', line)

                ivar, desc = line.split(' ', 1)
                if class_:
                    range_ = ranges[class_]
                    for replace_with, desc_replace in range_:
                        eval_ivar(f, ivar.replace(replace, replace_with), 
                                  replace_multiple(category, *desc_replace),
                                  replace_multiple(desc, *desc_replace))
                else:
                    eval_ivar(f, ivar, category, desc)
                    print(line, file=sys.stderr)

def generate_mem_info(fn, output_fn):
    addr_info = {}

    whitespace = re.compile('[\s]')

    clear_re = re.compile('(.*)->\*')
    m_re = re.compile('M(\d+)->')

    def fix_comment(s):
        if s.startswith('&'):
            s = 'CS %s' % s[1:]
        elif s.startswith('#'):
            s = 'Motor %s' % s[1:]
        
        return s
    
    mem_fix = re.compile('\$0([^,])')
    for line in open(fn, 'rt').readlines():
        line = line.strip()
        if ';' in line:
            line, comment = line.split(';', 1)
            comment = comment.strip()
        else:
            comment = ''

        line = whitespace.subn('', line)[0]
        if not line:
            continue
         
        if '->' in line:
            mvar, mem = line.split('->')
            if mem.strip() == '*':
                continue
            
            mvar = mvar.upper()

            repl = 1
            while repl > 0:
                mem, repl = re.subn('\$0([^,])', r'$\1', mem)
            
            if not comment:
                print('%s points to %s which is %s' % (mvar, mem, comment))
               
            addr_info[mem] = fix_comment(comment)

    with open(output_fn, 'wt') as f:
        print('# vi: sw=20 ts=20', file=f)

        for mem, info in sorted(addr_info.items(), key=lambda (mem, info): '%s %s' % (info.lower(), mem)):
            print('%s\t%s' % (mem, info), file=f)


class Info(object):
    def __init__(self, fn, delim='\t', lower_case_keys=True):
        self.data = data = {}
        for line in open(fn, 'rt').readlines():
            line = line.strip()
            if line.startswith('#'):
                continue

            info = line.split(delim)
            if lower_case_keys:
                info[0] = info[0].lower()

            data[info[0]] = info[1:]
    
    def __getitem__(self, key):
        return self.data[key]

    def search(self, text, in_keys=True, in_data=True, 
               case_insensitive=True):
        if case_insensitive:
            text = text.lower()

        for key, values in self.data.items():
            s = []
            if in_keys:
                s.append(key)
            if in_data:
                s.extend(values)

            s = ''.join(s)
            if case_insensitive:
                s = s.lower()

            if text in s.lower():
                yield (key, values)

# raw ivar file should be formatted roughly as in the PDF, see
# the geobrick_lv one for example
RAW_IVAR_FN = 'ivars_raw.txt'
# memory information should be a commented script containing
# mappings from (arbitrary) m variables to memory addresses.
# the address and comment for that line then get stored.
RAW_MEM_FN = 'm_variables.pmc'

IVAR_FN = 'ivars.csv'
MEM_FN = 'mem.csv'

ivar_info = None
mem_info = None

def load_settings(profile, ivar_fn=IVAR_FN, mem_fn=MEM_FN):
    global ivar_info, mem_info, loaded_profile
    
    profile_path = util.get_profile_path(profile)

    ivar_fn = os.path.join(profile_path, ivar_fn)
    ivar_info = Info(ivar_fn)

    mem_fn = os.path.join(profile_path, mem_fn)
    mem_info = Info(mem_fn)

def generate_settings(profile, ivar_fns=(RAW_IVAR_FN, IVAR_FN),
                      mem_fns=(RAW_MEM_FN, MEM_FN)):
    profile_path = util.get_profile_path(profile)

    ivar_fns = [os.path.join(profile_path, fn) for fn in ivar_fns]
    mem_fns = [os.path.join(profile_path, fn) for fn in mem_fns]
    generate_ivar_info(*ivar_fns)
    generate_mem_info(*mem_fns)
    
    
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: %s profile_name' % (sys.argv[0]))
        sys.exit(1)
    
    profile = sys.argv[1]
    generate_settings(profile)
