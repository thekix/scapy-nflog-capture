#!/usr/bin/env python

import os
from setuptools import setup

# Error-handling here is to allow package to be built w/o README included
try:
    readme = open(os.path.join(
        os.path.dirname(__file__), 'README.md')).read()
except IOError:
    readme = ''

from nflog_cffi import NFLOG

setup(
    name = 'scapy-nflog-capture3',
    version = '22.11.2',
    author = 'Rodolfo García Peñas (kix)',
    author_email = 'kix@kix.es',
    license = 'WTFPL',
    keywords = ['nflog', 'scapy', 'plugin', 'driver', 'traffic', 'analysis',
                'analyze', 'capture', 'dump', 'network', 'linux', 'security',
                'sniffer', 'spoof', 'netfilter', 'iptables', 'xtables',
                'filter', 'filtering', 'firewall', 'audit', 'cffi',
                'libnetfilter_log', 'socket'],
    url = 'http://github.com/mk-fg/scapy-nflog-capture',

    description = 'Driver for scapy to allow capturing packets via Linux NFLOG interface (Python 3)',
    long_description = readme,
    long_description_content_type='text/markdown',

    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Security',
        'Topic :: System :: Networking :: Monitoring',
        'Topic :: System :: Operating System Kernels :: Linux'],

    ext_modules = [NFLOG().ffi.verifier.get_extension()],

    py_modules = ['nflog_cffi', 'scapy_nflog'],
    package_data = {'': ['README.md']})
