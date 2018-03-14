import os
import subprocess
import tempfile

def run_ninja(ninja_file, raw_ninja_arguments):
    """ Run Ninja using the file generated from the pipeline and the 
        command-line arguments.
    """
    
    with tempfile.NamedTemporaryFile() as fd:
        fd.write(ninja_file.encode("utf-8"))
        fd.flush()
        return subprocess.call(["ninja", "-f", fd.name]+raw_ninja_arguments)
