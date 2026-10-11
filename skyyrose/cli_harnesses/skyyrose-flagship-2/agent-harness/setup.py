"""
cli-anything-skyyrose-flagship-2 — agent CLI for the SkyyRose Flagship 2 theme.

Runs the theme's own npm gates under the pinned V2 toolchain and exports
evidence that God Mode X validates and the Fashion Theme Team reviews.
"""

from setuptools import find_namespace_packages, setup

setup(
    name="cli-anything-skyyrose-flagship-2",
    version="1.0.0",
    description="Agent CLI for the SkyyRose Flagship 2 theme gates and shared evidence",
    author="The-Skyy-Rose-Collection",
    python_requires=">=3.10",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    package_data={
        "cli_anything.skyyrose_flagship_2": ["skills/*.md", "README.md", "tests/TEST.md"]
    },
    install_requires=[
        "click>=8.1,<9.0",
        "prompt-toolkit>=3.0,<4.0",
    ],
    extras_require={"dev": ["pytest>=7"]},
    entry_points={
        "console_scripts": [
            "cli-anything-skyyrose-flagship-2=cli_anything.skyyrose_flagship_2.skyyrose_flagship_2_cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
)
