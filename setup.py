import glob
import os

from setuptools import setup, find_packages

here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "README.md")) as f:
    long_description = f.read()

setup(
    name="spire-pipeline",
    version="1.1.0",
    
    description="Run software pipelines using doit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
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
    install_requires=["doit", "jinja2", "numpy"],
)
