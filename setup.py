#!/usr/bin/env python

import sys

from setuptools import setup

import gitless.cli.gl as gl


reqs = ['gitpylib>=0.5']
if sys.version_info < (2, 7) or (
    sys.version_info < (3, 3) and sys.version_info > (3, 0)):
  reqs.append('argparse')


setup(
    name='gitless',
    version=gl.VERSION,
    description='A version control system built on top of Git',
    long_description=open('README.md').read(),
    author='Santiago Perez De Rosso',
    author_email='sperezde@csail.mit.edu',
    url=gl.URL,
    packages=['gitless', 'gitless.cli', 'gitless.core'],
    install_requires=reqs,
    license='GPLv2',
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Software Development :: Version Control'),
    entry_points={
        'console_scripts': [
            'gl = gitless.cli.gl:main'
        ]},
    test_suite='gitless.tests')
