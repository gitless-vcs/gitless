#!/bin/sh

cd ~

git clone --depth=1 -b maint/v0.23 https://github.com/libgit2/libgit2.git
cd libgit2/

mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../_install -DBUILD_CLAR=OFF  # don't build unit tests
cmake --build . --target install
ls -la ..

cd ~
