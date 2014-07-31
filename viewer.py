#!/usr/bin/env python
# vi: ts=4 sw=4
"""
Usage: viewer.py [-ci] [--pdf=FILE] [--profile=geobrick_lv] PMC_FILE [PMC_FILE [PMC_FILE... ]]
       viewer.py --download [--pdf=FILE]

Displays turbo pmac configuration files

Arguments:
    PMC_FILE         the PMC file to display

Options:
    -c --clean       clean pmc file first (fix tabs, annotate lines)
    -p --profile=x   variable information profile [default: geobrick_lv]
    -d --download    download "turbo srm.pdf" from Delta Tau website (http://www.deltatau.com/manuals/pdfs/TURBO%20SRM.pdf)
    -p --pdf=FILE    specify pdf documentation location (current index is of 2014/2/14 manual) [default: turbo_srm.pdf]
    -i --includes    open files included in all PMC files
"""

# TODO option for executing program instead of relying on browser pdf viewer
from __future__ import print_function
import os
import sys
import atexit

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

import tempfile

try:
    from PyQt4 import QtGui
    from PyQt4 import QtCore
except ImportError:
    from PySide import QtGui
    from PySide import QtCore
    try:
        from PySide import Qsci
    except ImportError:
        print('ERROR: PySide-QScintilla is not installed')
        sys.exit(1)
else:
    try:
        from PyQt4 import Qsci
    except ImportError:
        print('ERROR: qscintilla-python package is not installed.')
        sys.exit(1)

# try:
#     import popplerqt4 as poppler
# except ImportError:
#     try:
#         import poppler
#     except ImportError:
#         poppler = None
#         print('NOTE: popplerqt4 (pypoppler) not installed; pdf will open in browser tab')

from docopt import docopt

from tpmac.conf import (TpConfig, TpVars)
import tpmac.info as tp_info
from tpmac.clean import clean_pmc
from tpmac import util

PDF_FILE = 'turbo_srm.pdf'
PDF_URL = 'http://www.deltatau.com/manuals/pdfs/TURBO%20SRM.pdf'
__temp_files__ = []


@atexit.register
def _cleanup_temp_files():
    global __temp_files__

    for fn in list(__temp_files__):
        try:
            os.unlink(fn)
        except:
            pass
        else:
            __temp_files__.remove(fn)

    if __temp_files__:
        print('Unable to delete temporary files: %s' % ' '.join(__temp_files__))


def open_documentation_pdf(page=0, use_browser=True):
    global PDF_FILE
    global __temp_files__
    pdf = PDF_FILE
    print('Opening pdf %s, page %d...' % (pdf, page))

    pdf = os.path.abspath(PDF_FILE)
    url = QtCore.QUrl.fromLocalFile(pdf)
    if page is not None:
        url.setFragment('page=%d' % page)

    if use_browser:
        # URL fragments don't work on Windows, so use a temporary html
        # file which redirects to the pdf at the proper page
        template = open('redirect_template.html', 'rt').read()

        temp_fn = None

        url = unicode(url.toString())
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            temp_fn = f.name
            template = unicode(template) % locals()
            print(template.encode('utf-8'), file=f)

        url = QtCore.QUrl.fromLocalFile(temp_fn)

        __temp_files__.append(temp_fn)

    services = QtGui.QDesktopServices()
    services.openUrl(url)


def show_tooltip(text):
    QtGui.QToolTip.showText(QtGui.QCursor.pos(), text)


class LookupWidget(QtGui.QFrame):
    def __init__(self, title, entries, parent=None):
        QtGui.QFrame.__init__(self, parent)

        self.setWindowTitle(title)
        self.list_ = QtGui.QListWidget()
        self.list_.itemDoubleClicked.connect(self.open_)

        for entry, page in sorted(entries):
            item = QtGui.QListWidgetItem(entry)
            item.setData(QtCore.Qt.UserRole, page)
            self.list_.addItem(item)

        self.open_button = QtGui.QPushButton('&Open')
        self.open_button.setDefault(True)
        self.open_button.released.connect(self.open_)

        self.cancel_button = QtGui.QPushButton('&Cancel')
        self.cancel_button.setShortcut(QtGui.QKeySequence('Esc'))
        self.cancel_button.released.connect(self.close)

        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(self.list_, 0, 0, 1, 2)
        self.layout.addWidget(self.open_button, 1, 0)
        self.layout.addWidget(self.cancel_button, 1, 1)
        self.setLayout(self.layout)

    def open_(self, item=None):
        item = self.list_.currentItem()
        if item:
            page = item.data(QtCore.Qt.UserRole).toPyObject()

            open_documentation_pdf(page=page)
            self.close()


class TextEditor(Qsci.QsciScintilla):
    ARROW_MARKER_NUM = 8

    # based on:
    #     http://eli.thegreenplace.net/2011/04/01/sample-using-qscintilla-with-pyqt/
    def __init__(self, cview, lexer_type=Qsci.QsciLexerPascal, font_name='Courier',
                 parent=None):
        Qsci.QsciScintilla.__init__(self, parent)

        self.cview = cview
        self.main = cview.main
        self.filename = cview.fn

        self.setReadOnly(True)

        # Set the default font
        font = QtGui.QFont()
        font.setFamily(font_name)
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)
        self.setMarginsFont(font)

        # Margin 0 is used for line numbers
        fontmetrics = QtGui.QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.width("00000") + 6)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QtGui.QColor("#cccccc"))

        # Clickable margin 1 for showing markers
        self.setMarginSensitivity(1, True)
        self.marginClicked.connect(self.on_margin_clicked)
        self.markerDefine(self.RightArrow, self.ARROW_MARKER_NUM)
        self.setMarkerBackgroundColor(QtGui.QColor("#ee1111"),
                                      self.ARROW_MARKER_NUM)

        # Brace matching: enable for a brace immediately before or after
        # the current position
        #
        self.setBraceMatching(self.SloppyBraceMatch)

        # Current line visible with special background color
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QtGui.QColor("#ffe4e4"))

        lexer = lexer_type()
        lexer.setDefaultFont(font)
        self.setLexer(lexer)
        self.SendScintilla(self.SCI_STYLESETFONT, 1, font_name)

        # Don't want to see the horizontal scrollbar at all
        # Use raw message to Scintilla here (all messages are documented
        # here: http://www.scintilla.org/ScintillaDoc.html)
        self.SendScintilla(self.SCI_SETHSCROLLBAR, 0)
        self.SendScintilla(self.SCI_SETMOUSEDWELLTIME, 1000)

        self.setMinimumSize(600, 450)

        self.copy_action = QtGui.QAction('&Copy', self)
        self.copy_action.setShortcut(QtGui.QKeySequence('Ctrl+C'))
        self.copy_action.triggered.connect(self.act_copy)

        self.select_all_action = QtGui.QAction('Select &all', self)
        self.select_all_action.setShortcut(QtGui.QKeySequence('Ctrl+A'))
        self.select_all_action.triggered.connect(self.act_select_all)

        self.lookup_action = QtGui.QAction('&Look up...', self)
        self.lookup_action.triggered.connect(lambda _: self.lookup())
        self.lookup_action.setEnabled(True)
        self.addAction(self.lookup_action)

        # To get the hover tooltips, connect the 'dwell start' signal
        self.SCN_DWELLSTART.connect(self.dwell_start)

    def dwell_start(self, letter_pos, x, y):
        word = self.selectedText()
        if not word:
            word = self.wordAtPoint(QtCore.QPoint(x, y))

        self.lookup(str(word), tooltip_only=True)

    def focusInEvent(self, event):
        self.lookup_action.setShortcuts([QtGui.QKeySequence('F1'),
                                         QtGui.QKeySequence('Ctrl+I'),
                                         ])
        return Qsci.QsciScintilla.focusInEvent(self, event)

    def focusOutEvent(self, event):
        self.lookup_action.setShortcuts([])
        return Qsci.QsciScintilla.focusOutEvent(self, event)

    def act_copy(self):
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(self.selectedText())

    def act_select_all(self):
        first_line = self.firstVisibleLine()

        last_line = self.lines()
        self.setSelection(0, 0, last_line, self.lineLength(last_line))

        self.setFirstVisibleLine(first_line)

    def lookup(self, text=None, tooltip_only=False):
        if text is None:
            text = str(self.selectedText())

        text = text.strip()

        entries = tp_info.lookup(text)

        if not entries:
            return

        if tooltip_only:
            if len(entries) == 1:
                tooltip, page = entries[0]
                if page is not None:
                    tooltip = '%s (page=%d)' % (tooltip, page)

                print('%s: %s' % (text, tooltip))
                show_tooltip(tooltip)
            return

        if len(entries) == 1:
            tooltip, page = entries[0]
            print('%s: %s' % (text, tooltip))
            if page is not None:
                open_documentation_pdf(page=page)
            else:
                show_tooltip(tooltip)
        else:
            self._lookup_widget = LookupWidget(text, entries)
            self._lookup_widget.show()

    def on_margin_clicked(self, nmargin, nline, modifiers):
        # Toggle marker for the line the margin was clicked on
        if self.markersAtLine(nline) != 0:
            self.markerDelete(nline, self.ARROW_MARKER_NUM)
        else:
            self.markerAdd(nline, self.ARROW_MARKER_NUM)

    def contextMenuEvent(self, event):
        text = str(self.selectedText())
        if text:
            menu = QtGui.QMenu()
            menu.addAction(self.lookup_action)
            menu.addSeparator()
            menu.addAction(self.copy_action)
            menu.addAction(self.select_all_action)

            menu.exec_(event.globalPos())
        else:
            return Qsci.QsciScintilla.contextMenuEvent(self, event)


class RefListWidget(QtGui.QListWidget):
    def __init__(self, refwidget, plc, plc_text_editor):
        QtGui.QListWidget.__init__(self)

        self.main = refwidget.main
        self.cview = refwidget.cview

        self.refwidget = refwidget
        self.plc = plc
        self.plc_text_editor = plc_text_editor

        self._last_clicked = None
        self.itemDoubleClicked.connect(self.jump_to_item)

        self.itemSelectionChanged.connect(self.item_selected)

    @property
    def source_widget(self):
        return self.cview.source_widget

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.jump_to_item(self.currentItem())
        elif event.key() == QtCore.Qt.Key_H:
            self.open_pdf(self.currentItem())

        return QtGui.QListWidget.keyPressEvent(self, event)

    def item_selected(self):
        self.update_description(self.currentItem())

    def update_description(self, list_item):
        text = '%s' % list_item.text()

        info = []

        def lookup(text):
            for desc, page in tp_info.lookup(text):
                yield desc, page

            mvar_info = self.main.mvar_info

            if mvar_info is not None:
                try:
                    addr = mvar_info[text][0]
                except ValueError:  # not an m-variable
                    pass
                except KeyError:
                    pass
                else:
                    try:
                        mem_info = tp_info.mem_info[addr][0]
                    except:
                        mem_info = 'unknown'

                    yield ('%s->%s [%s]' % (text, addr, mem_info), None)

        for desc, page in lookup(text):
            info.append(desc)
            if page is not None:
                page = int(page)
                info.append('Documentation page <a href="%d">%d</a>' % (page, page))

        s = '<br>\n'.join(info)
        self.refwidget.info.setText(s)

    def open_pdf(self, list_item):
        text = '%s' % list_item.text()
        try:
            desc, category, page = tp_info.ivar_info[text]
        except KeyError:
            pass
        else:
            page = int(page)
            print('%s (%s)' % (text, category))
            print('%s' % desc)
            open_documentation_pdf(page=page)
            return

        print('No documentation found for: %s' % text)

    def jump_to_item(self, list_item):
        text = list_item.text()

        if self._last_clicked is list_item:
            self.plc_text_editor.findNext()
            self.source_widget.findNext()
        else:
            self.plc_text_editor.findFirst(text, False, False, False, True)
            self.source_widget.findFirst(text, False, False, False, True)

        self._last_clicked = list_item


class RefWidget(QtGui.QFrame):
    def __init__(self, plc, text_editor):
        QtGui.QFrame.__init__(self)

        self.main = text_editor.main
        self.cview = text_editor.cview

        self.list_ = RefListWidget(self, plc, text_editor)
        self.info = QtGui.QLabel()

        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.list_)
        self.layout.addWidget(self.info)

        self.setLayout(self.layout)

        self.info.linkActivated.connect(self.open_url)

    def open_url(self, text):
        page = int(text)
        print('Opening documentation page %d...' % page)
        open_documentation_pdf(page=page)


class PLCEditor(QtGui.QSplitter):
    def __init__(self, cview, plc, reformat=False, parent=None):
        QtGui.QFrame.__init__(self, QtCore.Qt.Vertical, parent)

        self.cview = cview
        self.plc = plc

        if reformat:
            plc.reformat()

        self.editor = TextEditor(cview)
        self.refs = RefWidget(plc, self.editor)

        refs = plc.find_references()
        if refs:
            self.addWidget(self.refs)

            for ref in refs:
                self.refs.list_.addItem(ref)

        self.addWidget(self.editor)
        self.editor.setText('%s' % plc)


class PLCView(QtGui.QTabWidget):
    def __init__(self, cview):
        QtGui.QTabWidget.__init__(self)

        self.cview = cview
        self.config = cview.config
        self.plcs = []
        for plc_num, plc in self.config.plcs.items():
            plc_editor = PLCEditor(cview, plc)
            self.plcs.append(plc_editor)
            self.addTab(plc_editor, 'PLC %d' % plc.number)


class VariableView(QtGui.QFrame):
    def __init__(self, vars, parent=None):
        QtGui.QFrame.__init__(self, parent)

        self.list_ = QtGui.QListWidget()
        self.list_.itemDoubleClicked.connect(self.open_)

        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(self.list_, 0, 0, 1, 2)
        self.setLayout(self.layout)

    def open_(self):
        pass


class ConfigView(QtGui.QTabWidget):
    def __init__(self, main, config, fn, parent=None):
        QtGui.QTabWidget.__init__(self, parent)

        self.fn = fn
        self.config = config
        self.main = main

        sw = self.source_widget = TextEditor(self)
        sw.setText('\n'.join(config.dump()))

        self.addTab(sw, 'Source')

        if config.plcs:
            self.plc_view = PLCView(self)
            self.addTab(self.plc_view, 'PLCs')


class MainWindow(QtGui.QMainWindow):
    def __init__(self, fns, clean=False, load_includes=False):
        QtGui.QMainWindow.__init__(self)

        if not fns:
            return

        self.tabs = QtGui.QTabWidget()

        self.setCentralWidget(self.tabs)

        self.mvar_info = tp_info.VarInfo(type_='m')
        self.configs = {}
        self.config_views = {}
        self.variables = {}

        self.setWindowTitle('TpView - [%s]' % fns[0])
        self.load_includes = load_includes

        for var_type in util.VAR_TYPES:
            self.variables[var_type] = TpVars(var_type)

        for fn in fns:
            self.load_file(fn, clean, load_includes=load_includes)

    def load_file(self, fn, clean=False, load_includes=False):
        fn = os.path.relpath(fn)
        if fn in self.configs:
            return

        if clean:
            print('Cleaning file: %s' % fn)
            output = StringIO()
            for line in clean_pmc(fn, annotate=True, fix_indent=True):
                print(line, file=output)

            output.seek(0)
            self.configs[fn] = TpConfig(output)
        else:
            self.configs[fn] = TpConfig(fn)

        config = self.configs[fn]
        config_view = self.config_views[fn] = ConfigView(self, config, fn)
        self.tabs.addTab(config_view, fn)

        for tpvar in config.variables['m']:
            var_name = tpvar.var_str
            addr = tpvar.value
            self.mvar_info.add_item(var_name, [addr])

        for var_type in util.VAR_TYPES:
            for tpvar in config.variables[var_type]:
                self.variables[var_type].add_var(tpvar)

        if load_includes:
            for include in config.includes:
                self.load_file(include.fn, clean=clean, load_includes=load_includes)


def download(url, filename):
    print('Download: %s' % url)
    print('Save to : %s' % filename)

    if os.path.exists(filename):
        print('File exists; aborting')
        return

    try:
        import urllib2
    except ImportError:
        from urllib.request import urlretrieve
        local_fn, headers = urlretrieve(url, filename=filename)
    else:
        with open(filename, 'wb') as f:
            response = urllib2.urlopen(url)
            data = response.read()
            f.write(data)

    print('Done')


if __name__ == "__main__":
    opts = docopt(__doc__)

    PDF_FILE = opts['--pdf']
    if opts['--download']:
        download(PDF_URL, PDF_FILE)
        sys.exit(0)

    tp_info.load_settings(opts['--profile'])
    pmc_files = opts['PMC_FILE']

    print('Loading: %s' % ', '.join(pmc_files))

    app = QtGui.QApplication(sys.argv)
    main = MainWindow(pmc_files, clean=opts['--clean'],
                      load_includes=opts['--includes'])

    main.show()
    app.exec_()
