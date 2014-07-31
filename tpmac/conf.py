#!/usr/bin/env python
# vi: ts=4 sw=4
"""
tpmac.conf
Loads/saves turbo pmac configuration files, retaining the original
line order, comments, etc.
"""

from __future__ import print_function
import re

from . import (info, util)
from .util import VAR_TYPES


MIN_COMMENT_COL = 10
SPACES_PER_TAB = 4


def format_comments(lines):
    lengths = [len(line) for line, comment in lines]
    comment_col = max(lengths) + 2

    if comment_col < MIN_COMMENT_COL:
        comment_col = MIN_COMMENT_COL

    last_line = ''
    for line, comment in lines:
        if comment is not None:
            if line.strip():
                line = ''.join((line, ' ' * (comment_col - len(line)), '; ', comment))
            elif comment:
                if last_line:
                    # certainly a lazy way...
                    last_spaces = len(last_line) - len(last_line.lstrip())
                else:
                    last_spaces = 0

                line = ''.join((line, ' ' * last_spaces, '; ', comment))
            else:
                line = ';'

        yield line

        last_line = line


class TpBlock(object):
    def __init__(self, lines=None):
        if lines is not None:
            self.lines = lines
        else:
            self.lines = []

    def get_lines(self):
        for line in format_comments(self.lines):
            yield line

    def __str__(self):
        return '\n'.join(self.get_lines())

    def config_str(self, config=None):
        yield str(self)


class TpCoord(object):
    def __init__(self, coord_sys, motor, axis, comment=None):
        self.coord_sys = coord_sys
        self.motor = int(motor)
        self.axis = axis
        self.comment = comment

    def config_str(self, config=None):
        if config is None or config.coord is None or config.coord.number != self.coord_sys:
            yield '&%d%s' % (self.coord_sys, self)
        else:
            yield str(self)

    def __str__(self):
        return '#%d->%s' % (self.motor, self.axis)


class TpCoordSys(object):
    MAX_MOTORS = 32

    def __init__(self, number):
        self.coord_sys = int(number)
        self.coords = {}

    def set(self, number, tpcoord):
        self.coords[number] = tpcoord

    def config_str(self, config=None):
        yield '&%d' % self.coord_sys

        lines = [('%s' % coord, coord.comment)
                 for num, coord in sorted(self.coords.items(), key=lambda (k, v): k)]

        for line in format_comments(lines):
            yield line

    def __str__(self):
        return '\n'.join(self.config_str())


class TpVar(object):
    def __init__(self, var, value, comment=None):
        self.type_ = var[0].lower()
        try:
            var = int(var[1:])
        except:
            var = var[1:]

        self.var, self.value = var, value.strip()
        self.comment = comment

    @property
    def var_str(self):
        return '%s%s' % (self.type_, self.var)

    def config_str(self, config=None):
        if self.type_ == 'm':
            eq = '->'
        else:
            eq = '='

        yield '%s%s%s%s' % (self.type_.upper(), self.var, eq, self.value)

    def __str__(self):
        return '\n'.join(self.config_str())

    def annotate(self):
        value = self.value

        if self.type_ == 'm':
            value = util.clean_addr(value)

            try:
                desc = info.mem_info[value][0]
            except KeyError:
                return

        elif self.type_ == 'i':
            try:
                desc, category, page = info.ivar_info[self.var_str]
            except KeyError:
                return

        if self.comment:
            if desc in self.comment:
                pass
            elif desc != self.comment:
                self.comment = '%s [%s]' % (self.comment, desc)
        else:
            self.comment = desc

    @property
    def page(self):
        if self.type_ == 'i':
            try:
                desc, category, page = info.ivar_info[self.var_str]
            except KeyError:
                pass
            else:
                return int(page)


class TpVars(object):
    def __init__(self, type_):
        self.type_ = type_
        assert(type_ in VAR_TYPES)
        self.items = {}

    def __getitem__(self, key):
        return self.items[key]

    def __setitem__(self, key, value):
        self.items[key].value = value

    def __iter__(self):
        for var, tpvar in sorted(self.items.items(), key=lambda (k, v): k):
            yield tpvar

    def config_str(self, config=None):
        lines = [('%s' % tpvar, tpvar.comment)
                 for var, tpvar in sorted(self.items.items(), key=lambda (k, v): k)]

        for line in format_comments(lines):
            yield line

    def add_var(self, tpvar):
        assert(self.type_ == tpvar.type_)

        self.items[tpvar.var] = tpvar

    def __str__(self):
        return '\n'.join(self.config_str())


class TpInclude(object):
    def __init__(self, fn, comment=None):
        self.fn = fn.strip('"').strip("'")
        self.comment = comment

    def config_str(self, config=None):
        if self.comment:
            yield '#include "%s"  ; %s' % (self.fn, self.comment)
        else:
            yield '#include "%s"' % self.fn

    def __str__(self):
        return '\n'.join(self.config_str())


class TpPlcBlock(object):
    _ref_res = [re.compile('([pmqi]\([^\)]+\))', flags=re.IGNORECASE),
                re.compile('([pmqi]\d+)', flags=re.IGNORECASE)]

    def __init__(self, number, clear=True):
        self.number = int(number)
        self.clear = bool(clear)

        self.lines = []

    def append(self, line, comment):
        self.lines.append((line, comment))

    def reformat(self, start_indent=2, indent_amount=2):
        indent = start_indent

        indent_words = ('while', 'if', 'for', 'do', 'else')
        deindent_words = ()
        deindent_immediate = ('else', 'end')
        for i, (line, comment) in enumerate(self.lines):
            word = util.get_first_word(line)
            if word in deindent_immediate:
                indent -= indent_amount

            if line.strip():
                line = ''.join((' ' * indent, line.lstrip()))
            else:
                line = ''

            self.lines[i] = (line, comment)

            if word in indent_words:
                indent += indent_amount
            elif word in deindent_words:
                indent -= indent_amount

    def config_str(self, config=None):
        if self.clear:
            yield 'OPEN PLC %d CLEAR' % self.number
        else:
            yield 'OPEN PLC %d' % self.number

        for line in format_comments(self.lines):
            yield line

        yield 'CLOSE'

    def __iter__(self):
        for line, comment in self.lines:
            yield line, comment

    def find_references(self):
        refs = set()
        for line, comment in self:
            for ref_re in self._ref_res:
                for ref in ref_re.findall(line):
                    refs.add(ref)

        return list(sorted(refs))

    def __str__(self):
        return '\n'.join(self.config_str())


class TpConfig(object):
    coord_re = re.compile('^\s*&(\d+)(.*)$', flags=re.IGNORECASE)
    coord_def_re = re.compile('^\s*#(\d+)->(.*)$', flags=re.IGNORECASE)
    plc_re = re.compile('^\s*open plc (\d+)\s*(clear)?$', flags=re.IGNORECASE)
    var_re = re.compile('^\s*([pmqi]\d+)\s*(->|=)\s*(.*)$', flags=re.IGNORECASE)
    include_re = re.compile('^\s*#include\s*"?(.*)"?$', flags=re.IGNORECASE)

    def __init__(self, fn='config/mc09.pmc', **load_opts):
        if fn:
            self.load_config(fn, **load_opts)
        else:
            self._clear()

    @staticmethod
    def parse_lines(lines):
        for i, line in enumerate(lines):
            line = line.rstrip()
            line = line.replace('\t', ' ' * SPACES_PER_TAB)
            if ';' in line:
                in_quotes = False
                for i, c in enumerate(line):
                    if c in ("'", '"'):
                        in_quotes = not in_quotes
                    elif c == ';' and not in_quotes:
                        line, comment = line[:i], line[i + 1:]
                        break

                comment = comment.strip()
            else:
                comment = None

            yield i, line, comment

    def _clear(self):
        self.coords = {}
        self.coord = None
        self.lines = []

        self.plcs = {}
        self._plc = None
        self._unparsed = []
        self._var_block = None
        self.includes = []

        self.last_coord = 0
        self.blocks = []

        self.variables = {}
        for var_type in VAR_TYPES:
            self.variables[var_type] = TpVars(var_type)

    def load_config(self, fn, **kwargs):
        self._clear()

        if hasattr(fn, 'readlines'):
            f = fn
        else:
            f = open(fn, 'rt')

        self.lines = [line.rstrip() for line in f.readlines()]

        for line_num, line, comment in TpConfig.parse_lines(self.lines):
            self._eval_line(line_num, line, comment, **kwargs)

        self._unparsed_block()

    def dump(self, reformat=False, reformat_kw={}):
        for block in self.blocks:
            if hasattr(block, 'reformat') and reformat:
                block.reformat(**reformat_kw)

            if hasattr(block, 'coord_sys'):
                self.last_coord = block.coord_sys

            for line in block.config_str(self):
                yield line

    def _unparsed_block(self):
        if self._unparsed:
            self.blocks.append(TpBlock(self._unparsed))
            self._unparsed = []

    @property
    def last_block(self):
        return self.blocks[-1]

    def _matched_var(self, m, line_num, line, comment, eval_kwargs):
        var, eq, value = m.groups()
        tpvar = TpVar(var, value.strip(), comment)

        last_block = self.blocks[-1]
        if isinstance(last_block, TpVars) and last_block.type_ == tpvar.type_:
            last_block.add_var(tpvar)
        else:
            new_block = TpVars(tpvar.type_)
            new_block.add_var(tpvar)

            self.blocks.append(new_block)

        self.variables[tpvar.type_].add_var(tpvar)

    def _matched_coord(self, m, line_num, line, comment, eval_kwargs):
        coord_sys = int(m.groups()[0])

        self.last_coord = coord_sys

        last_block = self.last_block
        if isinstance(last_block, TpCoordSys) and last_block.coord_sys == coord_sys:
            # two &1's in a row, for example
            pass
        else:
            self.blocks.append(TpCoordSys(coord_sys))

        if m.groups()[1]:
            self._eval_line(line_num, m.groups()[1], comment, **eval_kwargs)

    def _matched_coord_def(self, m, line_num, line, comment, eval_kwargs):
        motor, axis = m.groups()
        motor = int(motor)

        last_block = self.last_block
        if isinstance(last_block, TpCoordSys):
            coord_sys = last_block
        else:
            coord_sys = TpCoordSys(self.last_coord)
            self.blocks.append(coord_sys)

        coord = TpCoord(coord_sys.coord_sys, motor, axis, comment)
        coord_sys.set(motor, coord)

    def _matched_plc(self, m, line_num, line, comment, eval_kwargs):
        number, clear = m.groups()
        number = int(number)
        self.plcs[number] = self._plc = TpPlcBlock(number, clear=(clear.lower() == 'clear'))
        self.blocks.append(self._plc)

    def _matched_include(self, m, line_num, line, comment, eval_kwargs):
        fn, = m.groups()
        include = TpInclude(fn, comment)
        self.includes.append(include)
        self.blocks.append(include)

    def remove_block(self, block):
        #  TODO - track parents for easy removal
        self.blocks.remove(block)

    def _eval_line(self, line_num, line, comment, verbose=True):
        line_lower = line.lower().strip()

        eval_kwargs = dict(verbose=verbose)

        if self._plc:
            if util.get_first_word(line_lower) == 'close':
                self._plc = None
            else:
                self._plc.append(line, comment)

        else:
            matches = [(self.var_re, self._matched_var),
                       (self.coord_re, self._matched_coord),
                       (self.coord_def_re, self._matched_coord_def),
                       (self.plc_re, self._matched_plc),
                       (self.include_re, self._matched_include),
                       ]

            for regex, fcn in matches:
                m = regex.match(line.rstrip())
                if m:
                    self._unparsed_block()
                    return fcn(m, line_num, line, comment, eval_kwargs)

            if line_lower == 'undefine':
                self.coords.remove(self.coord)
                self.coord = None

            elif line_lower == 'undefine all':
                self.coords = []
                self.coord = None

            if verbose and line:
                print('* [Line %d] unparsed: %s' % (line_num, line))

            self._unparsed.append((line, comment))


if __name__ == '__main__':
    conf = TpConfig()
