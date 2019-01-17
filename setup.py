#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
The setup script for napalm-logs
'''
import codecs
from setuptools import setup, find_packages

__author__ = 'Mircea Ulinic <ping@mirceaulinic.net>'

with codecs.open('README.md', 'r', encoding='utf8') as file:
    long_description = file.read()

with open("requirements.txt", "r") as fs:
    reqs = [r for r in fs.read().splitlines() if (len(r) > 0 and not r.startswith("#"))]

setup(
    name='salt-napalm',
    version='2019.1.0a1',
    namespace_packages=['salt_napalm'],
    package_dir={'': 'lib'},
    packages=find_packages('lib'),
    author='Mircea Ulinic',
    author_email='mircea.ulinic@gmail.com',
    description='Salt plugin for interacting with network devices through NAPALM, without running Minions',
    long_description=long_description,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Topic :: Utilities',
        'Topic :: System :: Networking',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Intended Audience :: Developers'
    ],
    url='https://github.com/napalm-automation/napalm-salt',
    license="Apache License 2.0",
    keywords=('napalm', 'salt', 'network', 'automation', 'cli'),
    include_package_data=True,
    install_requires=reqs,
    entry_points={
        'console_scripts': [
            'salt-napalm=salt_napalm.scripts:salt_napalm'
        ],
    }
)
