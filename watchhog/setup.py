import os
import sys
from setuptools import setup, find_packages
from distutils.core import Extension

parser_source = os.path.join(os.path.dirname(__file__), 'hog/parser/parser_native.cpp')

if sys.platform == 'darwin':
    include_dirs = [
        # '/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator.sdk/usr/include/',
        # '/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.11.sdk/System/Library/Frameworks/Python.framework/Headers',
        '/usr/local/Cellar/boost/1.56.0/include'
    ]
elif sys.platform.startswith('linux'):
    include_dirs = [
            '/usr/local/include'
    ]

parser_native = Extension('hog/parser/parser_native',
                          sources=[parser_source],
                          include_dirs=include_dirs)
setup ( name = 'watchhog',
        version = '1.0',
        description = 'WatchHog is a fast log watcher and parser',
        packages = find_packages(),
        ext_modules = [parser_native])
