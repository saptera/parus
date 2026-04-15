# Project version setting SCRIPT

import os
import argparse
import re


def version_type(value):
    """ Check and parse version input. """
    pattern = re.compile(r'^(\d+)\.(\d+)\.(\d+)(?:rc(\d+))?$')
    match = pattern.fullmatch(value)
    if not match:
        raise argparse.ArgumentTypeError("Version must match X.Y.Z or X.Y.ZrcN (example: 1.2.3 or 1.2.3rc4)")
    major, minor, patch, rc = match.groups()
    return value, {'major': int(major), 'minor': int(minor), 'patch': int(patch), 'rc': int(rc) if rc else None}


# CLI inputs parser  ------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(prog="SetVer", description="Set version and release values in corresponding files")
parser.add_argument('version', type=version_type, metavar="projVer", help="[%(type)s] Project build version")
args = parser.parse_args()
# -------------------------------------------------------------------------------------------------------------------- #

ver_str, ver_prt = args.version
cwd = os.path.dirname(__file__)


def update_version(file, doc=False):
    """ Update version information line in file.

    Args:
        file (str): Project file has version declaration
        doc (bool): Flag for Sphinx config file, which has separate `[version]` and `[release]` keys (default: False).
    """
    with open(file, 'r', encoding='utf-8', newline='') as fp:
        lines = fp.readlines()

    with open(file, 'w', encoding='utf-8', newline='') as fp:
        for l in lines:
            s = l.lstrip()
            if doc:
                if s.startswith('version = '):
                    fp.write('%sversion = "%d.%d"\n' % (l[:len(l) - len(s)], ver_prt['major'], ver_prt['minor']))
                elif s.startswith('release = '):
                    fp.write('%srelease = "%s"\n' % (l[:len(l) - len(s)], ver_str))
                else:
                    fp.write(l)
            else:
                if s.startswith('version = '):
                    fp.write('%sversion = "%s"\n' % (l[:len(l) - len(s)], ver_str))
                else:
                    fp.write(l)


# Build full paths of required files
proj_def = os.path.realpath(os.path.join(cwd, "../../pyproject.toml"))
pkg_init = os.path.realpath(os.path.join(cwd, "../../parus/__init__.py"))
doc_conf = os.path.realpath(os.path.join(cwd, "../../doc/API/source/conf.py"))

# Update files
update_version(proj_def, doc=False)
update_version(pkg_init, doc=False)
update_version(doc_conf, doc=True)
