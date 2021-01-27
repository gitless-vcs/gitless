#!/bin/sh
# Based on pygit2's .travis.sh

PREFIX=/home/travis/install

# Build libssh2 1.9.0 (Ubuntu only has 1.8.0, which doesn't work)
cd ~
wget https://www.libssh2.org/download/libssh2-1.9.0.tar.gz
tar xf libssh2-1.9.0.tar.gz
cd libssh2-1.9.0
./configure --prefix=/usr --disable-static && make
sudo make install

# Build libgit2
cd ~
git clone --depth=1 -b "maint/v1.1" https://github.com/libgit2/libgit2.git
cd libgit2/

mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../_install -DBUILD_CLAR=OFF  # don't build unit tests
cmake --build . --target install
ls -la ..

cd ~
