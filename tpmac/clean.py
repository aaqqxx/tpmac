#!/usr/bin/env python
# vi: ts=4 sw=4
"""
Usage: tpmac.clean [-fav] [--indent=2] [--min-col=10] INPUT_PMC [OUTPUT_PMC]

Arguments:
    INPUT_PMC        the PMC file to process
    OUTPUT_PMC       optionally output to a file (stdout by default)

Options:
    -a --annotate    annotate addresses with comments
    -f --fix-indent  fixes indentation in PLC scripts
    -i --indent=2    indentation amount, in spaces [default: 2]
    -m --min-col=10  minimum column to align comments [default: 10]
    -v --verbose     verbose mode

"""

from __future__ import print_function
import sys

from docopt import docopt

from . import conf
from .conf import TpConfig


if __name__ == '__main__':
    opts = docopt(__doc__)

    input_ = opts['INPUT_PMC']
    output_f = opts['OUTPUT_PMC']
    verbose = bool(opts['--verbose'])
    if output_f is not None:
        output_ = open(output_f, 'wt')
    else:
        output_ = sys.stdout
    
    config = TpConfig(input_, verbose=verbose)

    if opts['--annotate']:
        for vars_ in config.variables.values():
            for tpvar in vars_:
                tpvar.annotate()

    if opts['--fix-indent']:
        indent = int(opts['--indent'])
        for plc in config.plcs.values():
            plc.reformat(start_indent=indent, indent_amount=indent)
   
    conf.MIN_COMMENT_COL = int(opts['--min-col'])
    for line in config.dump():
        print(line, file=output_)
