from codecs import open
import glob
import os

from setuptools import setup, find_packages

here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="spire-pipeline",
    version="0.7.0",
    
    description="Run software pipelines using doit",
    long_description=long_description,
    
    url="https://github.com/lamyj/spire",
    
    author="Julien Lamy",
    author_email="lamy@unistra.fr",
    
    license="MIT",
    
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        
        "Environment :: Console",
        
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        
        "Topic :: Software Development :: Build Tools",
        "Topic :: Scientific/Engineering",
        
        "License :: OSI Approved :: MIT License",
        
        "Programming Language :: Python :: 3",
    ],
    
    keywords="pipeline, workflow, task execution",

    packages=find_packages(exclude=["tests"]),
    install_requires=["doit"],
)
