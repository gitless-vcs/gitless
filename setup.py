#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys

from setuptools import setup


VERSION = '0.8.5'


# Build helper
if sys.argv[-1] == 'gl-build':
  from sh import pyinstaller
  import shutil
  import tarfile
  import platform

  rel = 'gl-v{0}-{1}-{2}'.format(
      VERSION, platform.system().lower(), platform.machine())

  print('running pyinstaller...')
  pyinstaller(
      'gl.spec', clean=True, distpath=rel, _out=sys.stdout, _err=sys.stderr)
  print('success!! gl binary should be at {0}/gl'.format(rel))

  print('creating tar.gz file')
  shutil.copy('README.md', rel)
  shutil.copy('LICENSE.md', rel)
  
  with tarfile.open(rel + '.tar.gz', 'w:gz') as tar:
    tar.add(rel)
  print('success!! binary release at {0}'.format(rel + '.tar.gz'))

  sys.exit()


reqs = ['pygit2>=0.24.0', 'clint>=0.3.6']

if sys.platform != 'win32':
  reqs.append('sh>=1.11')
else:
  reqs.append('pbs>=0.11')

if sys.version_info < (2, 7) or (
    sys.version_info < (3, 3) and sys.version_info > (3, 0)):
  reqs.append('argparse')


ld = """
Gitless is an experimental version control system built on top of Git.
Many people complain that Git is hard to use. We think the problem lies
deeper than the user interface, in the concepts underlying Git. Gitless
is an experiment to see what happens if you put a simple veneer on an
app that changes the underlying concepts. Because Gitless is implemented
on top of Git (could be considered what Git pros call a \"porcelain\" of
Git), you can always fall back on Git. And of course your coworkers you
share a repo with need never know that you're not a Git aficionado.

More info, downloads and documentation @ `Gitless's
website <http://gitless.com>`__.
"""

setup(
    name='gitless',
    version=VERSION,
    description='A version control system built on top of Git',
    long_description=ld,
    author='Santiago Perez De Rosso',
    author_email='sperezde@csail.mit.edu',
    url='http://gitless.com',
    packages=['gitless', 'gitless.cli'],
    install_requires=reqs,
    license='GPLv2',
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Version Control'),
    entry_points={
        'console_scripts': [
            'gl = gitless.cli.gl:main'
        ]},
    test_suite='gitless.tests')
