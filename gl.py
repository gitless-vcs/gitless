#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git
# Licensed under MIT

# This file is for PyInstaller

import sys

from gitless.cli import gl


if __name__ == '__main__':
  sys.exit(gl.main())
