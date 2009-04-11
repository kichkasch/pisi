"""
Third party module for make a beautiful (non-verbose) CLI output with a progress bar

The original has been taken from http://epydoc.sourceforge.net/ - all non-required stuff has been deleted
"""
# epydoc -- Utility functions
#
# Copyright (C) 2005 Edward Loper
# Author: Edward Loper <edloper@loper.org>
# URL: <http://epydoc.sf.net>
#
# $Id$


import re, sys

######################################################################
## Terminal Control
######################################################################

class TerminalController:
    """
    A class that can be used to portably generate formatted output to
    a terminal.  See
    U{http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/475116}
    for documentation.  (This is a somewhat stripped-down version.)
    """
    BOL = ''             #: Move the cursor to the beginning of the line
    UP = ''              #: Move the cursor up one line
    DOWN = ''            #: Move the cursor down one line
    LEFT = ''            #: Move the cursor left one char
    RIGHT = ''           #: Move the cursor right one char
    CLEAR_EOL = ''       #: Clear to the end of the line.
    CLEAR_LINE = ''      #: Clear the current line; cursor to BOL.
    BOLD = ''            #: Turn on bold mode
    NORMAL = ''          #: Turn off all modes
    COLS = 75            #: Width of the terminal (default to 75)
    UNDERLINE = ''       #: Underline the text
    REVERSE = ''         #: Reverse the foreground & background
    BLACK = BLUE = GREEN = CYAN = RED = MAGENTA = YELLOW = WHITE = ''
    
    _STRING_CAPABILITIES = """
    BOL=cr UP=cuu1 DOWN=cud1 LEFT=cub1 RIGHT=cuf1 REVERSE=rev 
    CLEAR_EOL=el BOLD=bold UNDERLINE=smul NORMAL=sgr0""".split()
    _COLORS = """BLACK BLUE GREEN CYAN RED MAGENTA YELLOW WHITE""".split()
    _ANSICOLORS = "BLACK RED GREEN YELLOW BLUE MAGENTA CYAN WHITE".split()

    #: If this is set to true, then new TerminalControllers will
    #: assume that the terminal is not capable of doing manipulation
    #: of any kind.
    FORCE_SIMPLE_TERM = False

    def __init__(self, term_stream=sys.stdout):
        # If the stream isn't a tty, then assume it has no capabilities.
        if not term_stream.isatty(): return
        if self.FORCE_SIMPLE_TERM: return

        # Curses isn't available on all platforms
        try: import curses
        except:
            # If it's not available, then try faking enough to get a
            # simple progress bar.
            self.BOL = '\r'
            self.CLEAR_LINE = '\r' + ' '*self.COLS + '\r'
            
        # Check the terminal type.  If we fail, then assume that the
        # terminal has no capabilities.
        try: curses.setupterm()
        except: return

        # Look up numeric capabilities.
        self.COLS = curses.tigetnum('cols')
        
        # Look up string capabilities.
        for capability in self._STRING_CAPABILITIES:
            (attrib, cap_name) = capability.split('=')
            setattr(self, attrib, self._tigetstr(cap_name) or '')
        if self.BOL and self.CLEAR_EOL:
            self.CLEAR_LINE = self.BOL+self.CLEAR_EOL

        # Colors
        set_fg = self._tigetstr('setf')
        if set_fg:
            for i,color in zip(range(len(self._COLORS)), self._COLORS):
                setattr(self, color, curses.tparm(set_fg, i) or '')
        set_fg_ansi = self._tigetstr('setaf')
        if set_fg_ansi:
            for i,color in zip(range(len(self._ANSICOLORS)), self._ANSICOLORS):
                setattr(self, color, curses.tparm(set_fg_ansi, i) or '')

    def _tigetstr(self, cap_name):
        # String capabilities can include "delays" of the form "$<2>".
        # For any modern terminal, we should be able to just ignore
        # these, so strip them out.
        import curses
        cap = curses.tigetstr(cap_name) or ''
        return re.sub(r'\$<\d+>[/*]?', '', cap)
    
    def render(self, template):
        """
        Replace each $-substitutions in the given template string with
        the corresponding terminal control string (if it's defined) or
        '' (if it's not).
        """
        return re.sub(r'\$\$|\${\w+}', self._render_sub, template)

    def _render_sub(self, match):
        s = match.group()
        if s == '$$': return s
        else: return getattr(self, s[2:-1])

