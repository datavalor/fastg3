docker build -t manylinux2_gcc8.3.0 .
docker container run -it \
      -v "$(pwd)/..":/io \
      manylinux2_gcc8.3.0 /bin/bash

# python3.8 setup.py sdist bdist_wheel