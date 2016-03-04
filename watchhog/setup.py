import os
import sys
from setuptools import setup, find_packages, Extension

cdir = os.path.dirname(__file__)
VERSION_FILENAME = os.path.join(cdir, '.version')
BUILD_VERSION_FILENAME = os.path.join(cdir, '.build')

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

config = {
        'name': 'watchhog',
        'version': get_version(),
        'description': 'WatchHog is a fast log watcher and parser',
        'packages': find_packages(),
        'include_package_data': True,
        'package_data': { 
            'hog.web': [
                'static/*.html',
                'static/css/*.css',
                'static/js/*.js',
                'static/js/libs/*.js',
                'static/img/*.png',
                'static/templates/*.html'
            ] 
        },
        'scripts': [os.path.join(cdir, 'watchhog.py')],
        'author': 'Pavel Vorobyov',
        'author_email': 'aquavitale@yandex.ru',
        'license': 'MIT',
        'keywords': 'log parse index sysadmin'
}

if sys.platform.startswith('linux'):
    include_dirs = [
            '/usr/local/include'
    ]
    parser_source = os.path.join(os.path.dirname(__file__), 'native_ext/parser_native.cpp')
    parser_native = Extension('hog/parser/parser_native',
                          sources=[parser_source],
                          include_dirs=include_dirs)
    config['ext_modules'] = [parser_native]
else:
    print "WARNING! Native extensions are available on linux machines only yet"

setup ( **config )
