FROM ubuntu:16.04
MAINTAINER Vlad Zagorodniy

RUN apt-get update && apt-get install --yes \
    git \
    automake \
    gcc \
    llvm \
    clang \
    python3 \
    python3-pip \
    python3-dev \
    cmake \
    zlib1g-dev

# build llvmlite
RUN cd / && \
    git clone https://github.com/numba/llvmlite.git && \
    cd /llvmlite && \
    git checkout tags/v0.15.0 && \
    python3 setup.py build
ENV PYTHONPATH $PYTHONPATH:/llvmlite

# attach project directory
ADD . /dumbc

# build libstddumb
RUN cd /dumbc && \
    mkdir build && cd build && \
    cmake .. && \
    make && \
    make install
RUN ldconfig

# install dumbc
RUN cd /dumbc && \
    pip3 install --upgrade .
