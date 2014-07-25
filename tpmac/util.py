#!/usr/bin/env python
import re

VAR_TYPES = 'pqmi'

def clean_addr(addr):
    repl = 1
    while repl > 0:
        addr, repl = re.subn('\$0([^,])', r'$\1', addr)

    return addr
