#!/usr/bin/env python
# vi: ts=4 sw=4
"""
tpmac.util
Miscellaneous utility functions
"""

import os
import re

VAR_TYPES = 'pqmi'
FIRST_WORD_RE = re.compile('^\s*([a-zA-Z]+).*?')


def clean_addr(addr):
    repl = 1
    while repl > 0:
        addr, repl = re.subn('\$0([^,])', r'$\1', addr)

    return addr


def ivar_to_int(ivar):
    ivar = ivar.upper()
    if not ivar.startswith('I'):
        raise ValueError('not I variable')

    if '/' in ivar or '-' in ivar:
        raise ValueError('ivar range')

    return int(ivar[1:])


def int_to_ivar(i):
    return 'I%d' % i


def clean_ivar(ivar):
    return int_to_ivar(ivar_to_int(ivar))


def get_profile_path(profile):
    module_path = os.path.abspath(os.path.split(__file__)[0])

    profile_path = os.path.join(module_path, 'info', profile)

    if not os.path.exists(profile_path):
        raise RuntimeError('Profile %s path "%s" does not exist' %
                           (profile, profile_path))

    return profile_path


def get_first_word(line):
    m = FIRST_WORD_RE.match(line.lower())
    if m:
        return m.groups()[0]
    else:
        return line
