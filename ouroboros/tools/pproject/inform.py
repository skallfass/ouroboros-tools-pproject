# -*- coding: utf-8 -*-

"""
Copyright (C) 2018 Simon Kallfass

Provides the functions used for visual output for the user inside the
pproject-tool.
"""


import inspect
import sys


CYAN = '\033[0;94m'
"""str: Color cyan used for visual output for the user."""
GREEN = '\033[1;92m'
"""str: Color green used for visual output for the user."""
RED = '\033[1;91m'
"""str: Color red used for visual output for the user."""
NCOLOR = '\033[0m'
"""str: Resets the color used for visual output for the user."""
BOLD = '\033[1;37m'
"""str: Bold-style used for visual output for the user."""


# -----------------------------------------------------------------------------
def info(msg=None):
    """
    Generates output in defined info-style for the user.

    Parameters
    ----------
    msg: str
        (default=None) Message to output for the user in info-style.
    """
    tool = inspect.getouterframes(inspect.currentframe(), 2)[1][3]
    toolstr = f'  {tool.upper()} '.rjust(22, ' ')
    if not msg:
        msg = ''
    print(f' {BOLD}\u2139{NCOLOR}{CYAN}{toolstr}{NCOLOR}{msg}')


# -----------------------------------------------------------------------------
def error(msg=None):
    """
    Generates output in defined error-style for the user.

    Parameters
    ----------
    msg: str
        (default=None) Message to output for the user in info-style.
    """
    tool = inspect.getouterframes(inspect.currentframe(), 2)[1][3]
    toolstr = f'  {tool.upper()} '.rjust(22, ' ')
    if not msg:
        msg = ''
    print(f' {RED}E{NCOLOR}{CYAN}{toolstr}{NCOLOR}{msg}')


# -----------------------------------------------------------------------------
def finished(msg=None):
    """
    Generates output in defined finished-style for the user.

    Parameters
    ----------
    msg: str
        (default=None) Message to output for the user in info-style.
    """
    tool = inspect.getouterframes(inspect.currentframe(), 2)[1][3]
    toolstr = f'  {tool.upper()} '.rjust(22, ' ')
    if not msg:
        msg = ''
    print(f' {GREEN}\u2714{NCOLOR}{CYAN}{toolstr}{NCOLOR}{msg}')


# -----------------------------------------------------------------------------
def critical(msg=None):
    """
    Generates output in defined critical-style for the user.
    Stops the pproject-script with sys.exit(1).

    Parameters
    ----------
    msg: str
        (default=None) Message to output for the user in info-style.
        Before existing.
    """
    tool = inspect.getouterframes(inspect.currentframe(), 2)[1][3]
    toolstr = f'  {tool.upper()} '.rjust(22, ' ')
    if not msg:
        msg = ''
    print(f' {RED}\u2718{NCOLOR}{CYAN}{toolstr}{NCOLOR}{msg}')
    sys.exit(1)
