import os
import subprocess
import tempfile

def find(matlab="matlab", matlab_path=None):
    """ Return the root directory of SPM. matlab, if given, is the path to the
        MATLAB executable. matlab_path, if given, is a MATLAB expression fed to
        addpath.
    """
    
    script = ("if isempty(which('spm'));"
              "fprintf(1, '');"
              "exit();"
              "end;"
              "fprintf(1, '%s', spm('dir'));"
              "exit();")

    if matlab_path:
        script = "addpath({});".format(matlab_path)+script

    try:
        output = subprocess.check_output([
            matlab, "-nodisplay", "-nosplash", "-nojvm", "-r", script])
    except subprocess.CalledProcessError as e:
        raise Exception("Could not find SPM: {}".format(e))
    last_line = output.splitlines()[-1]
    # Weird data at the end of the line
    if b"\x1b" in last_line :
        last_line = last_line[:last_line.index(b"\x1b")]
    if last_line == "" :
        raise Exception("Could not find SPM")
    
    return last_line.decode()

def get_script(tools, standalone=True, exit=True, modality="fmri"):
    """ Return a Matlab script running the provided tools. If standalone is 
        True, then the script will include SPM initialization commands and the
        resulting script can be directly fed to Matlab. If standalone is False,
        the resulting script can be loaded in SPM Batch Editor.
    """
    
    script = []
    
    if standalone:
        script.extend([
            "spm('defaults','{}');".format(modality),
            "spm_jobman('initcfg');"
        ])
    
    for index, tool in enumerate(tools):
        script.append(tool.get_script(1+index))
    
    if standalone:
        script.append("spm_jobman('run',matlabbatch);")
        if exit:
            script.append("exit();")
    
    return "\n".join(script)

def run(jobs, matlab="matlab"):
    """ Run a list of jobs in Matlab. The ``matlab`` argument, if specified,
        is the path to the MATLAB executable.
    """
    
    fd, path = tempfile.mkstemp(suffix=".m")
    os.write(fd, "cd {}; {}".format(os.getcwd(), get_script(jobs)).encode())
    os.close(fd)

    try:
        subprocess.check_call([
            matlab, "-nodisplay", "-nosplash", "-r", "run('{}');".format(path)])
    finally:
        os.remove(path)
