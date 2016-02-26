import os
import sys
from setuptools import setup, find_packages, Extension

VERSION_FILENAME = os.path.join(os.path.dirname(__file__), '.version')
BUILD_VERSION_FILENAME = os.path.join(os.path.dirname(__file__), '.build')

def get_version():
    with open(VERSION_FILENAME) as vf:
        version = vf.read().strip()
    try:
        bvf = open(BUILD_VERSION_FILENAME)
        build = bvf.read().strip()
        build = int(build)
    except OSError:
        build = 0
    build += 1
    with open(BUILD_VERSION_FILENAME, "w") as bvf:
        bvf.write(str(build))
    return "%s.%d" % (version, build)

parser_source = os.path.join(os.path.dirname(__file__), 'native_ext/parser_native.cpp')
config = {
        'name': 'watchhog',
        'version': get_version(),
        'description': 'WatchHog is a fast log watcher and parser',
        'packages': find_packages(),
        'scripts': ['watchhog.py']
}

if sys.platform.startswith('linux'):
    include_dirs = [
            '/usr/local/include'
    ]
    parser_native = Extension('hog/parser/parser_native',
                          sources=[parser_source],
                          include_dirs=include_dirs)
    config['ext_modules'] = [parser_native]

setup ( **config )
