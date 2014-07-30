#!/usr/bin/env python
# vi: ts=4 sw=4
"""
Usage: tpmac.clean [-fav] [--indent=2] [--profile=geobrick_lv] [--min-col=10] INPUT_PMC [OUTPUT_PMC]

Cleans up indentation and optionally annotates Turbo PMAC configuration files (.pmc)

Arguments:
    INPUT_PMC        the PMC file to process
    OUTPUT_PMC       optionally output to a file (stdout by default)

Options:
    -a --annotate    annotate addresses with comments
    -f --fix-indent  fixes indentation in PLC scripts
    -i --indent=2    indentation amount, in spaces [default: 2]
    -m --min-col=10  minimum column to align comments [default: 10]
    -v --verbose     verbose mode
    -p --profile=x   variable information profile [default: geobrick_lv]
"""

from __future__ import print_function
import sys

from docopt import docopt

from . import conf
from .conf import TpConfig
from . import info as tp_info


def clean_pmc(input_fn, verbose=False, annotate=False,
              fix_indent=False, indent=2):
    config = TpConfig(input_fn, verbose=verbose)

    if annotate:
        for vars_ in config.variables.values():
            for tpvar in vars_:
                tpvar.annotate()

    if fix_indent:
        for plc in config.plcs.values():
            plc.reformat(start_indent=indent, indent_amount=indent)

    for line in config.dump():
        yield line


if __name__ == '__main__':
    opts = docopt(__doc__)

    input_fn = opts['INPUT_PMC']
    output_fn = opts['OUTPUT_PMC']
    indent = int(opts['--indent'])
    verbose = bool(opts['--verbose'])
    tp_info.load_settings(opts['--profile'])

    conf.MIN_COMMENT_COL = int(opts['--min-col'])

    ret = clean_pmc(input_fn,
                    annotate=opts['--annotate'],
                    fix_indent=opts['--fix-indent'],
                    indent=indent,
                    verbose=verbose)

    if output_fn is not None:
        output_ = open(output_fn, 'wt')
    else:
        output_ = sys.stdout

    for line in ret:
        print(line, file=output_)
