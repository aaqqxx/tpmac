#!/usr/bin/env python
# vi: ts=4 sw=4
"""
tpmac.info
Generates (and reads) tab-separated files containing turbo pmac variable,
memory, and documentation page locations
"""

from __future__ import print_function
import os
import sys
import re

from . import util


ranges = {'motor': [('%.2d' % x, [('xx', '%d' % x)]) for x in range(1, 33)],
          'macro': [('%d' % n, [(' n ', ' %d' % n)]) for n in range(1, 3)],
          'servo': [('%d%d' % (m, n),
                    [('Servo IC m', 'Servo IC %d' % m),
                     ('Channel n', 'Channel %d' % n)])
                    for m in range(0, 10) for n in range(1, 5)],
          'servo0': [('%d0' % m,
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
ivars = {}


def _eval_ivar(f, page, ivar, category, desc):
    if '/' in ivar:
        for iv in ivar.split('/'):
            _eval_ivar(f, page, iv, category, desc)
        return
    elif '-' in ivar:
        r0, r1 = [util.ivar_to_int(iv) for iv in ivar.split('-')]
        for i in range(r0, r1 + 1):
            _eval_ivar(f, page, 'i%d' % i, category, desc)
    else:
        try:
            ivar_int = util.ivar_to_int(ivar)
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
    def __init__(self, fn=None, delim='\t'):
        self.clear()

        if fn is not None:
            self.load_file(fn, delim=delim)

    def clear(self):
        self.data = {}
        self._lower_keys = {}
        self._lower_data = {}

    def load_file(self, fn, delim='\t', clear=True):
        if clear:
            self.clear()

        for line in open(fn, 'rt').readlines():
            line = line.strip()
            if line.startswith('#'):
                continue

            info = line.split(delim)

            key, data = info[0], info[1:]
            self.add_item(key, data)

    def add_item(self, key, data):
        self._lower_keys[key.lower()] = key
        self.data[key] = data

    def __getitem__(self, key):
        if key.lower() in self._lower_keys:
            key = self._lower_keys[key.lower()]

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

            s = s.decode('ascii', 'ignore')

            if text in s:
                yield (key, values)


class VarInfo(Info):
    def __init__(self, type_='i', **kwargs):
        self.type_ = type_
        Info.__init__(self, **kwargs)

    def __getitem__(self, key):
        if '->' in key:
            key = key.split('->', 1)[0]

        return Info.__getitem__(self, util.clean_var(key, type_=self.type_))

    def add_item(self, key, data):
        return Info.add_item(self, util.clean_var(key, type_=self.type_), data)


class MemInfo(Info):
    def __getitem__(self, key):
        if '->' in key:
            key = key.split('->', 1)[1]

        return Info.__getitem__(self, util.clean_addr(key))

    def add_item(self, key, data):
        return Info.add_item(self, util.clean_addr(key), data)


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
    ivar_info = VarInfo(fn=ivar_fn, type_='i')

    mem_fn = os.path.join(profile_path, mem_fn)
    mem_info = MemInfo(fn=mem_fn)

    toc_fn = os.path.join(profile_path, toc_fn)
    toc_info = Info(fn=toc_fn)


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


def lookup(text):
    global ivar_info, mem_info, toc_info
    text = text.strip()
    if not text:
        return []

    if ':$' in text:
        try:
            desc = mem_info[text][0]
        except KeyError:
            pass
        else:
            return [(desc, None)]

    try:
        var_type, num = util.var_split(text)
    except ValueError:
        pass
    else:
        if var_type == 'i':
            try:
                desc, category, page = ivar_info[text]
            except KeyError:
                pass
            else:
                return [('%s [%s]' % (desc, category), int(page))]

    contents = toc_info
    return [('%s [%s]' % (desc_, cat_), int(page_))
            for desc_, (cat_, page_) in contents.search(text)]


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: %s profile_name' % (sys.argv[0]))
        sys.exit(1)

    profile = sys.argv[1]
    generate_settings(profile)
