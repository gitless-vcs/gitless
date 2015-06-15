#!/bin/sh

cd ~

git clone --depth=1 -b maint/v0.22 https://github.com/libgit2/libgit2.git
cd libgit2/

mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../_install -DBUILD_CLAR=OFF  # don't build unit tests
cmake --build . --target install

# We temporarily use our modified pygit2 until v0.22.1 is released
pip install git+https://github.com/spderosso/pygit2.git@tmp
