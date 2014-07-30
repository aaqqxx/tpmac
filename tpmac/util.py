#!/usr/bin/env python
# vi: ts=4 sw=4
"""
tpmac.util
Miscellaneous utility functions
"""

import os
import re

VAR_TYPES = 'pqmi'
simple_var_re = re.compile('^([pqmi])(\d+)$', flags=re.IGNORECASE)
FIRST_WORD_RE = re.compile('^\s*([a-zA-Z]+).*?')


def clean_addr(addr):
    repl = 1
    while repl > 0:
        addr, repl = re.subn('\$0([^,])', r'$\1', addr)

    return addr

def var_split(var):
    m = simple_var_re.match(var.strip())
    if not m:
        raise ValueError('Not a variable: %s' % var)

    var_type, var_num = m.groups()
    return var_type.lower(), int(var_num)


def ivar_to_int(ivar):
    type_, num = var_split(ivar)
    if type_ != 'i':
        raise ValueError('not I variable')

    return num


def clean_var(var, type_=None):
    var_type, num = var_split(var)
    if type_ is not None and var_type != type_.lower():
        raise ValueError('Variable type mismatch')

    return '%s%d' % (var_type, num)


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
