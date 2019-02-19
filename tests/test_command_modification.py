import os
import unittest
import shutil
import subprocess
import sys
import time

from test_base import TestBase

pipeline = """
import spire

class CLIAction(spire.Task):
    file_dep = ["dependency"]
    targets = ["target.cli", "target.py"]
    
    def python_action(*args, **kwargs):
        with open(CLIAction.targets[1], "w") as fd:
            pass
    
    actions = [
        ["touch", targets[0]],
        python_action
    ]
"""

class TestCLIModification(TestBase):
    
    file_dep = ["dependency"]
    targets = ["target.cli", "target.py"]
    
    def test_no_change(self):
        with open(os.path.join(self.directory, "pipeline.py"), "w") as fd:
            fd.write(pipeline)
        
        subprocess.check_output([
            "doit", "run", "-f", os.path.join(self.directory, "pipeline.py"), 
            "-d", self.directory])
        stats_1 = [os.stat(os.path.join(self.directory, x)) for x in self.targets]
        
        time.sleep(1)
        
        subprocess.check_output([
            "doit", "run", "-f", os.path.join(self.directory, "pipeline.py"), 
            "-d", self.directory])
        stats_2 = [os.stat(os.path.join(self.directory, x)) for x in self.targets]
        
        for stat_1, stat_2 in zip(stats_1, stats_2):
            for name in ["st_atime", "st_mtime", "st_ctime"]:
                self.assertEqual(getattr(stat_1, name), getattr(stat_2, name))
    
    def test_change_command(self):
        with open(os.path.join(self.directory, "pipeline.py"), "w") as fd:
            fd.write(pipeline)
        
        subprocess.check_output([
            "doit", "run", "-f", os.path.join(self.directory, "pipeline.py"), 
            "-d", self.directory])
        stats_1 = [os.stat(os.path.join(self.directory, x)) for x in self.targets]
        
        time.sleep(1)
        
        with open(os.path.join(self.directory, "pipeline.py")) as fd:
            data = fd.read()
        data = data.replace(
            """["touch", targets[0]]""", 
            """["touch", "-f", targets[0]]""")
        with open(os.path.join(self.directory, "pipeline.py"), "w") as fd:
            fd.write(data)
        
        subprocess.check_output([
            "doit", "run", "-f", os.path.join(self.directory, "pipeline.py"), 
            "-d", self.directory])
        stats_2 = [os.stat(os.path.join(self.directory, x)) for x in self.targets]
        
        for stat_1, stat_2 in zip(stats_1, stats_2):
            self.assertNotEqual(stat_1.st_mtime, stat_2.st_mtime)
    
    def test_change_python(self):
        with open(os.path.join(self.directory, "pipeline.py"), "w") as fd:
            fd.write(pipeline)
        
        subprocess.check_output([
            "doit", "run", "-f", os.path.join(self.directory, "pipeline.py"), 
            "-d", self.directory])
        stats_1 = [os.stat(os.path.join(self.directory, x)) for x in self.targets]
        
        time.sleep(1)
        
        with open(os.path.join(self.directory, "pipeline.py")) as fd:
            data = fd.read()
        data = data.replace(
            """pass""", 
            """fd.write("foo")""")
        with open(os.path.join(self.directory, "pipeline.py"), "w") as fd:
            fd.write(data)
        
        subprocess.check_output([
            "doit", "run", "-f", os.path.join(self.directory, "pipeline.py"), 
            "-d", self.directory])
        stats_2 = [os.stat(os.path.join(self.directory, x)) for x in self.targets]
        
        for stat_1, stat_2 in zip(stats_1, stats_2):
            self.assertNotEqual(stat_1.st_mtime, stat_2.st_mtime)
        
if __name__ == "__main__":
    sys.exit(unittest.main())
