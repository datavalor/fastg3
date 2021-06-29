DOCKER_IMAGE='quay.io/pypa/manylinux_2_24_x86_64'
PLAT='manylinux1_x86_64'
docker pull "$DOCKER_IMAGE"
docker container run -it --rm \
      -e PLAT=$PLAT \
      -v "$(pwd)":/io \
      "$DOCKER_IMAGE" /bin/bash

python3.8 -m pip install cython numpy
python3.8 setup.py sdist bdist_wheel