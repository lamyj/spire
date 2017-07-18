import subprocess

def run_ninja(ninja_file, raw_ninja_arguments):
    """ Run Ninja using the file generated from the pipeline and the 
        command-line arguments.
    """
    
    process = subprocess.Popen(
        ["ninja", "-f", "/dev/stdin"]+raw_ninja_arguments, 
        stdin=subprocess.PIPE)
    process.communicate(ninja_file)
    
    return process.returncode
