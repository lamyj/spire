from codecs import open
import glob
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

try:
    # Symlink to module source so that we can use package_data and keep data
    # out of source directory
    os.symlink("../modules", "spire/modules")

    setup(
        name="spire-pipeline",
        version="0.5.2",
        
        description="Run software pipelines using YAML files",
        long_description=long_description,
        
        url="https://github.com/lamyj/spire/",
        
        author="Julien Lamy",
        author_email="lamy@unistra.fr",
        
        license="MIT",
        
        classifiers=[
            "Development Status :: 4 - Beta",
            
            "Environment :: Console",
            
            "Intended Audience :: Developers",
            "Intended Audience :: Science/Research",
            
            "Topic :: Software Development :: Build Tools",
            "Topic :: Scientific/Engineering",
            
            "License :: OSI Approved :: MIT License",
            
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
        ],
        
        keywords="pipeline, workflow, task execution",

        packages=["spire"],
        install_requires=["jinja2", "pyyaml"],
        package_data={ "spire": ["modules/*.yml.j2"] },
        
        entry_points={ "console_scripts": [ "spire=spire:main"] },
    )
finally:
    os.unlink("spire/modules")
