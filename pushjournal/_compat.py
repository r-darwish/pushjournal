import sys

PY2 = sys.version_info[0] == 2

if PY2:
    from urllib import urlopen
else:
    from urllib.request import urlopen
