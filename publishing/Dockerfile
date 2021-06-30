FROM quay.io/pypa/manylinux_2_24_x86_64
ENV PLAT "manylinux_2_24_x86_64"

ARG GCC_VERSION=8.3.0
ARG GCC_PATH=/usr/local/gcc-$GCC_VERSION

RUN python3.8 -m pip install cython numpy --no-warn-script-location

RUN cd /tmp \
    && curl -L -o gcc.tar.gz "https://ftp.gnu.org/gnu/gcc/gcc-${GCC_VERSION}/gcc-${GCC_VERSION}.tar.gz" \
    && tar xf gcc.tar.gz \
    && cd /tmp/gcc-$GCC_VERSION \
    && contrib/download_prerequisites \
    # && apt -y install build-essential \
    && mkdir build \
    && cd build \
    && ../configure -v \
        --build=x86_64-linux-gnu \
        --host=x86_64-linux-gnu \
        --target=x86_64-linux-gnu \
        --prefix=/usr/local/gcc-$GCC_VERSION \
        --enable-checking=release \
        --enable-languages=c,c++,fortran \
        --disable-multilib \
        --program-suffix=-$GCC_VERSION \
    && make -j4 \
    && make install-strip \
    && cd /tmp \
    && rm -rf /tmp/gcc-$GCC_VERSION /tmp/gcc.tar.gz

ENV CFLAGS "-static-libstdc++"
ENV CC /usr/local/gcc-$GCC_VERSION/bin/gcc-$GCC_VERSION
ENV CXX /usr/local/gcc-$GCC_VERSION/bin/g++-$GCC_VERSION

CMD ["/bin/bash"]