docker build -t manylinux2_gcc8.3.0 .
docker container run -it \
      -v "$(pwd)/..":/io \
      manylinux2_gcc8.3.0 /bin/bash

# python3.8 setup.py sdist bdist_wheel

# auditwheel show fastg3-0.0.1-cp38-cp38-linux_x86_64.whl 