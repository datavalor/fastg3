#!/usr/bin/env python3

from setuptools import setup
from distutils.extension import Extension
from distutils.sysconfig import get_python_lib
from Cython.Build import cythonize
import numpy as np

cython_packages  = ["crisp"]
# print(cython_src)
extensions=[]
for package in cython_packages:
    extensions.append(
        Extension(
            f"fastg3/{package}/*.pyx",
            sources=[f"fastg3/{package}/*.pyx"], 
            include_dirs=[np.get_include(), ".", "fastg3/"],
            library_dirs=[get_python_lib()],
            language="c++",
            extra_compile_args=["-std=c++17", "-O3", "-fopenmp"],
            extra_link_args=["-std=c++17", "-O3", "-fopenmp"],
            define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        )
    )

setup(
    name="fastg3",
    zip_safe=False,
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
