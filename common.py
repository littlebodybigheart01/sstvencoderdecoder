# common.py
"""Shared methods"""

import os
import sys
from os import get_terminal_size
from sys import stderr, stdout, platform


def log_message(message="", show=True, err=False, recur=False, prefix=True):
    """Simple print wrapper"""

    if not show:
        return
    out = stdout
    if err:
        out = stderr
    end = '\n'
    if recur:
        end = '\r'
        if platform == "win32":
            message = ''.join(['\r', message])
        # Adjust based on terminal size
        try:
            cols = get_terminal_size().columns
        except OSError:
            cols = 80  # Default value if terminal size cannot be detected
        except:
            cols = 80
        if cols < len(message):
            message = message[:cols]
    if prefix:
        message = ' '.join(["[sstv]", message])

    print(message, file=out, end=end)


