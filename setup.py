# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# pmort is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

# -----------------------------------------------------------------------------
import sys
import traceback

if sys.version_info.major < 3:
    import ConfigParser
    configparser_name = 'ConfigParser'
else:
    import configparser
    configparser_name = 'configparser'

original_sections = sys.modules[configparser_name].ConfigParser.sections

def monkey_sections(self):
    '''Return a list of sections available; DEFAULT is not included in the list.

    Monkey patched to exclude the nosetests section as well.

    '''

    _ = original_sections(self)

    if any([ 'distutils/dist.py' in frame[0] for frame in traceback.extract_stack() ]) and _.count('nosetests'):
        _.remove('nosetests')

    return _

sys.modules[configparser_name].ConfigParser.sections = monkey_sections
# -----------------------------------------------------------------------------

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup

from pmort import information

PARAMS = {}

PARAMS['name'] = information.NAME
PARAMS['version'] = information.VERSION
PARAMS['description'] = information.DESCRIPTION

with open('README.rst', 'r') as fh:
    PARAMS['long_description'] = fh.read()

PARAMS['author'] = information.AUTHOR
PARAMS['author_email'] = information.AUTHOR_EMAIL
PARAMS['url'] = information.URL
PARAMS['license'] = information.LICENSE

PARAMS['classifiers'] = [
        'Development Status :: 3 - Alpha',
        'Environment :: No Input/Output (Daemon)',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: System :: Logging',
        ]

PARAMS['keywords'] = [
        'pmort',
        'post-mortem',
        ]

PARAMS['provides'] = [
        'pmort',
        ]

with open('requirements.txt', 'r') as req_fh:
    PARAMS['install_requires'] = req_fh.readlines()

with open('test_pmort/requirements.txt', 'r') as req_fh:
    PARAMS['tests_require'] = req_fh.readlines()

PARAMS['test_suite'] = 'nose.collector'

PARAMS['entry_points'] = {
        'console_scripts': [
            'pmort = pmort:main',
            ],
        }

PARAMS['packages'] = [
        'pmort',
        'pmort.collectors',
        'pmort.learners',
        ]

PARAMS['package_data'] = {
        'pmort.collectors': [
            '*.sh',
            ],
        }

PARAMS['data_files'] = [
        ('share/doc/{P[name]}-{P[version]}'.format(P = PARAMS), [
            'README.rst',
            ]),
        ('share/doc/{P[name]}-{P[version]}/conf/cron.daily'.format(P = PARAMS), [
            'conf/cron.daily/pmort.cron',
            ]),
        ('share/doc/{P[name]}-{P[version]}/conf/init.d'.format(P = PARAMS), [
            'conf/init.d/pmort.gentoo',
            ]),
        ('share/doc/{P[name]}-{P[version]}/conf/logrotate.d'.format(P = PARAMS), [
            'conf/logrotate.d/pmort.conf',
            ]),
        ('share/doc/{P[name]}-{P[version]}/conf/pmort'.format(P = PARAMS), [
            'conf/pmort/pmort.ini',
            ]),
        ]

setup(**PARAMS)
