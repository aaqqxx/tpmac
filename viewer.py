#!/usr/bin/env python
# vi: ts=4 sw=4
"""
Usage: viewer.py [-c] [--profile=geobrick_lv] PMC_FILE

Arguments:
    PMC_FILE         the PMC file to display

Options:
    -c --clean       clean pmc file first
    -p --profile=x   variable information profile [default: geobrick_lv]
"""

from __future__ import print_function
import sys
from PyQt4 import (QtGui, Qsci)
from PyQt4 import QtCore
from cStringIO import StringIO

from docopt import docopt

from tpmac.conf import TpConfig
import tpmac.info as tp_info
from tpmac.clean import clean_pmc

class TextEditor(Qsci.QsciScintilla):
    ARROW_MARKER_NUM = 8
    
    # based on:
    #     http://eli.thegreenplace.net/2011/04/01/sample-using-qscintilla-with-pyqt/
    def __init__(self, lexer_type=Qsci.QsciLexerPascal, font_name='Consolas', 
                 parent=None):
        super(TextEditor, self).__init__(parent)
        
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
    
        self.setMinimumSize(600, 450)

    def on_margin_clicked(self, nmargin, nline, modifiers):
        # Toggle marker for the line the margin was clicked on
        if self.markersAtLine(nline) != 0:
            self.markerDelete(nline, self.ARROW_MARKER_NUM)
        else:
            self.markerAdd(nline, self.ARROW_MARKER_NUM)


class RefWidget(QtGui.QListWidget):
    def __init__(self, plc, editor):
        QtGui.QListWidget.__init__(self)

        self.plc = plc
        self.editor = editor
        
        self._last_clicked = None
        self.itemDoubleClicked.connect(self.jump_to_item)
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.jump_to_item(self.currentItem())
        
        return QtGui.QListWidget.keyPressEvent(self, event)

    def jump_to_item(self, list_item):
        text = list_item.text()
        
        main = MainWindow.instance

        if self._last_clicked is list_item:
            self.editor.findNext()
            main.full_widget.findNext()
        else:
            self.editor.findFirst(text, False, False, False, True)
            main.full_widget.findFirst(text, False, False, False, True)

        self._last_clicked = list_item


class PLCEditor(QtGui.QSplitter):
    def __init__(self, plc, reformat=False, parent=None):
        QtGui.QFrame.__init__(self, QtCore.Qt.Vertical, parent)
        self.plc = plc
        
        if reformat:
            plc.reformat()

        self.editor = TextEditor()
        self.refs = RefWidget(plc, self.editor)
        
        self.addWidget(self.refs)
        self.addWidget(self.editor)

        refs = plc.find_references()
        for ref in refs:
            self.refs.addItem(ref)

        self.editor.setText('%s' % plc)


class MainWindow(QtGui.QMainWindow):
    def __init__(self, fn, clean=False):
        QtGui.QMainWindow.__init__(self)
        MainWindow.instance = self

        self.main_splitter = QtGui.QSplitter()
        
        self.setCentralWidget(self.main_splitter)
        
        self.plc_tabs = QtGui.QTabWidget()

        self.main_splitter.addWidget(self.plc_tabs)

        if clean:
            print('Cleaning file...')
            output = StringIO()
            for line in clean_pmc(fn, annotate=True, fix_indent=True):
                print(line, file=output)
            
            output.seek(0)
            fn = output
        
        self.config = config = TpConfig(fn)

        for plc_num, plc in config.plcs.items():
            self.plc_tabs.addTab(PLCEditor(plc), 'PLC %d' % plc.number)
        
        self.full_widget = TextEditor()
        self.full_widget.setText('\n'.join(config.dump()))

        self.main_splitter.addWidget(self.full_widget)


if __name__ == "__main__":
    opts = docopt(__doc__)

    tp_info.load_settings(opts['--profile'])
    pmc_file = opts['PMC_FILE']
    
    print('PMC file is', pmc_file)

    app = QtGui.QApplication(sys.argv)
    main = MainWindow(pmc_file, clean=opts['--clean'])
    main.show()
    app.exec_()
