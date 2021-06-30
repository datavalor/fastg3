#!/usr/bin/env python3

from setuptools import setup, find_packages
from distutils.extension import Extension
from distutils.sysconfig import get_python_lib
from Cython.Build import cythonize
import numpy as np
import glob

cython_packages  = ["crisp", "ncrisp"]
pyx_files = []
for package in cython_packages:
    paths = glob.glob(f"fastg3/{package}/*.pyx")
    for path in paths:
        name = path.split("/")[-1][:-4]
        pyx_files.append((name, path[0:], package))

# print(cython_src)
extensions=[]
for f in pyx_files:
    extensions.append(
        Extension(
            f"fastg3.{f[2]}.{f[0]}",
            sources=[f[1]], 
            include_dirs=[np.get_include()],
            language="c++",
            extra_compile_args=["-std=c++17", "-O3", "-fopenmp"],
            extra_link_args=["-std=c++17", "-O3", "-fopenmp"],
            define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        )
    )

setup(
    name="fastg3",
    packages=find_packages(),
    zip_safe=False,
    # inplace=True,
    ext_modules = cythonize(
        extensions, 
        compiler_directives={'language_level' : "3", 'boundscheck': False, 'wraparound': False}
    ),
    install_requires=[
        "numpy>=1.13.0",
        "pandas>=1,<2"
    ],
    python_requires=">=3.7",
)
