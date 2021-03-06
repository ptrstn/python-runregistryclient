from setuptools import setup

setup(
    name="python-runregistryclient",
    version="0.1",
    description="A simple Python client that accesses the CMS Run Registry",
    url="https://github.com/ptrstn/python-runregistryclient",
    author="Peter Stein",
    author_email="peterstein@cern.ch",
    packages=["runregistry"],
    install_requires=["requests"],
    zip_safe=False,
    entry_points={"console_scripts": ["runreg=runregistry.cli:main"]},
)
