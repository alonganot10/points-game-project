from setuptools import setup, Extension
import pybind11
import sys

if sys.platform == "win32":
    extra_compile_args = ["/O2", "/std:c++17"]
else:
    extra_compile_args = ["-O3", "-std=c++17"]

ext_modules = [
    Extension(
        "chain_cpp",
        ["chain_cpp.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++",
        extra_compile_args=extra_compile_args,
    )
]

setup(
    name="chain_cpp",
    version="1.0.0",
    ext_modules=ext_modules,
)