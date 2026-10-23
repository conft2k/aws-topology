"""Let cairosvg find Homebrew's cairo on Apple Silicon without any shell setup.

cairocffi locates cairo with ctypes.util.find_library, which on macOS searches
DYLD_FALLBACK_LIBRARY_PATH as read from os.environ at call time. Homebrew on Apple
Silicon installs into /opt/homebrew/lib, which is not on the default search path, so
importing this module before cairosvg adds it. Setting the variable replaces the
defaults (~/lib, /usr/local/lib, /lib, /usr/lib), so they are kept in the list. The
library is then opened by its absolute path, so SIP stripping DYLD_* variables from
child processes does not matter. A no-op on other platforms or without Homebrew there.
"""
import os
import sys

HOMEBREW_LIB = "/opt/homebrew/lib"

if sys.platform == "darwin" and os.path.isdir(HOMEBREW_LIB):
    from ctypes.macholib.dyld import DEFAULT_LIBRARY_FALLBACK

    current = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH")
    paths = current.split(":") if current else list(DEFAULT_LIBRARY_FALLBACK)
    if HOMEBREW_LIB not in paths:
        os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = ":".join([HOMEBREW_LIB] + paths)
