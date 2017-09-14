"""
The Bestory Project
"""

from distutils.core import setup


def content(filename, splitlines=False):
    c = open(filename, "r").read()
    return c.splitlines() if splitlines else c


long_description = content("README.md")

install_requires = content("requirements.txt", splitlines=True)
tests_requires = content("requirements-test.txt", splitlines=True)

setup(
    name="thebestory",
    description="The Bestory Magic-Powered API Server",
    version="2017.8.1",
    url="thebestory.com",

    author="The Bestory Team",
    author_email="team@thebestory.com",

    license="",
    long_description=long_description,

    packages=["tbs"],

    install_requires=install_requires,
    tests_require=install_requires + tests_requires,

    classifiers=(
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Natural Language :: Russian",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
    ),
)
