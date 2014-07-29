#!/usr/bin/env python
import os
import re

VAR_TYPES = 'pqmi'
FIRST_WORD_RE = re.compile('^\s*([a-zA-Z]+).*?')


def clean_addr(addr):
    repl = 1
    while repl > 0:
        addr, repl = re.subn('\$0([^,])', r'$\1', addr)

    return addr


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
