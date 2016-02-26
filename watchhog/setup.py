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

parser_native = Extension('parser_native',
                          sources=[parser_source],
                          include_dirs=include_dirs,
                          extra_compile_args=['-std=c++11'])
setup ( name = 'watchhog',
        version = '1.0',
        description = 'WatchHog is a fast log watcher and parser',
        ext_modules = [parser_native])
