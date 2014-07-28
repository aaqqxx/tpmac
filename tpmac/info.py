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

def _eval_ivar(f, page, ivar, category, desc):
    if '/' in ivar:
        for iv in ivar.split('/'):
            _eval_ivar(f, page, iv, category, desc)
        return
    elif '-' in ivar:
        r0, r1 = [ivar_to_int(iv) for iv in ivar.split('-')]
        for i in range(r0, r1 + 1):
            _eval_ivar(f, page, int_to_ivar(i), category, desc)
    else: 
        try:
            ivar_int = ivar_to_int(ivar)
        except:
            print('Failed: %s' % ivar)
        else:
            print('i%d\t%s\t%s\t%d' % (ivar_int, desc, category, page), file=f)
        
            if ivar in ivars:
                print('Duplicate', ivar, ivars[ivar], '//', (category, desc))

            ivars[ivar] = (category, desc, page)


def eval_ivar(f, page, ivar, category, desc):
    if 'Motor xx' in desc:
        class_, replace = 'motor', 'xx'
    elif 'Servo IC m Channel n' in desc:
        class_, replace = 'servo', 'mn'
    elif 'Servo IC m' in desc:
        class_, replace = 'servo0', 'm'
    elif ('MACRO IC Channel n' in desc) or ('MACRO IC Encoder n' in desc):
        class_, replace = 'macro', 'n'
    elif 'Coordinate System' in desc:
        class_, replace = 'cs', 'sx'
    else:
        class_ = ''
    
    if class_:
        range_ = ranges[class_]
        for replace_with, desc_replace in range_:
            _eval_ivar(f, page,
                      ivar.replace(replace, replace_with), 
                      replace_multiple(category, *desc_replace),
                      replace_multiple(desc, *desc_replace))
    else:
        _eval_ivar(f, page, ivar, category, desc)

def replace_multiple(s, *from_to):
    for from_, to in from_to:
        s = s.replace(from_, to)
    return s

def generate_toc_info(input_fn, output_fn, only_ivars=False):
    category = ''
    re_istart = re.compile('(I[sxmn0-9][sxmn0-9-]*)')
    
    all_toc = []

    category = ''

    with open(output_fn, 'wt') as f:
        print('# vi: ts=30 sw=30', file=f)
        with open(input_fn, 'rt') as inf:
            for line in inf.readlines():
                if not line.strip():
                    continue
                elif '....' not in line:
                    continue

                is_category = not line.startswith(' ')
                
                line, page = line.split('....', 1)
                line = line.rstrip('.').strip()
                page = int(page.lstrip('.'))
                
                line = line.replace('\t', ' ')
                line = line.replace('  ', ' ')

                all_toc.append((page, line))
                
                if is_category:
                    category = line

                if only_ivars:
                    if not is_category:
                        m = re_istart.match(line)
                        if m:
                            ivar, desc = line.split(' ', 1)
                            eval_ivar(f, page, ivar, category, desc.strip())
                    continue

                print('%s\t%s\t%d' % (line, category, page), file=f)

def generate_mem_info(fn, output_fn):
    addr_info = {}

    whitespace = re.compile('[\s]')

    def fix_comment(s):
        if s.startswith('&'):
            s = 'CS %s' % s[1:]
        elif s.startswith('#'):
            s = 'Motor %s' % s[1:]
        
        return s
    
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
            mem = util.clean_addr(mem)
            
            if not comment:
                print('%s points to %s which is %s' % (mvar, mem, comment))
            
            addr_info[mem] = fix_comment(comment)

    with open(output_fn, 'wt') as f:
        print('# vi: sw=20 ts=20', file=f)

        for mem, info in sorted(addr_info.items(), key=lambda (mem, info): '%s %s' % (info.lower(), mem)):
            print('%s\t%s' % (mem, info), file=f)


class Info(object):
    def __init__(self, fn, delim='\t'):
        self.data = data = {}
        self._lower_keys = {}
        for line in open(fn, 'rt').readlines():
            line = line.strip()
            if line.startswith('#'):
                continue

            info = line.split(delim)
            
            key = info[0]
            self._lower_keys[key.lower()] = key
            data[key] = info[1:]
    
    def __getitem__(self, key):
        if key in self._lower_keys:
            key = self._lower_keys[key]

        return self.data[key]

    def search(self, text, in_keys=True, in_data=True, 
               case_insensitive=True):
        # note: very inefficient search
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

# table of contents file generated using:
#    pdftotext -layout turbo_srm.pdf and partially hand-tweaked
# see the geobrick_lv one for example
RAW_IVAR_FN = 'ivars_raw.txt'
RAW_TOC_FN = 'contents.txt'
# memory information should be a commented script containing
# mappings from (arbitrary) m variables to memory addresses.
# the address and comment for that line then get stored.
RAW_MEM_FN = 'm_variables.pmc'

# the actual information files -- tsv (tab-separated values)
IVAR_FN = 'ivars.tsv'
MEM_FN = 'mem.tsv'
TOC_FN = 'contents.tsv'

ivar_info = None
mem_info = None
toc_info = None

def load_settings(profile, ivar_fn=IVAR_FN, mem_fn=MEM_FN,
                 toc_fn=TOC_FN):
    global ivar_info, mem_info, toc_info
    
    profile_path = util.get_profile_path(profile)

    ivar_fn = os.path.join(profile_path, ivar_fn)
    ivar_info = Info(ivar_fn)

    mem_fn = os.path.join(profile_path, mem_fn)
    mem_info = Info(mem_fn)

    toc_fn = os.path.join(profile_path, toc_fn)
    toc_info = Info(toc_fn)

def generate_settings(profile, ivar_fns=(RAW_TOC_FN, IVAR_FN),
                      mem_fns=(RAW_MEM_FN, MEM_FN),
                      toc_fns=(RAW_TOC_FN, TOC_FN)):
    profile_path = util.get_profile_path(profile)

    ivar_fns = [os.path.join(profile_path, fn) for fn in ivar_fns]
    mem_fns = [os.path.join(profile_path, fn) for fn in mem_fns]
    toc_fns = [os.path.join(profile_path, fn) for fn in toc_fns]

    generate_toc_info(ivar_fns[0], ivar_fns[1], only_ivars=True)
    generate_mem_info(*mem_fns)
    generate_toc_info(*toc_fns)
    
    
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: %s profile_name' % (sys.argv[0]))
        sys.exit(1)
    
    profile = sys.argv[1]
    generate_settings(profile)
