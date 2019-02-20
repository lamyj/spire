import os
import unittest
import shutil
import subprocess
import sys
import time

from test_base import TestBase

pipeline = """
import spire

class FactoryTask(spire.TaskFactory):
    def __init__(self):
        spire.TaskFactory.__init__(self, "TaskFactory")
        self.file_dep = ["dependency"]
        self.targets = ["target.cli", "target.py"]
        self.actions = [
            ["touch", self.targets[0]],
            self.python_action
        ]
    
    def python_action(self, *args, **kwargs):
        with open(self.targets[1], "w") as fd:
            pass

task_object = FactoryTask()
"""

class TestTaskFactoryModification(TestBase):
    
    file_dep = ["dependency"]
    targets = ["target.cli", "target.py"]
    
    def test_no_change(self):
        with open(os.path.join(self.directory, "pipeline.py"), "w") as fd:
            fd.write(pipeline)
        
        stats_1 = self._run_and_stat()
        
        time.sleep(1)
        
        stats_2 = self._run_and_stat()
        
        for stat_1, stat_2 in zip(stats_1, stats_2):
            for name in ["st_atime", "st_mtime", "st_ctime"]:
                self.assertEqual(getattr(stat_1, name), getattr(stat_2, name))
    
    def test_change_command(self):
        with open(os.path.join(self.directory, "pipeline.py"), "w") as fd:
            fd.write(pipeline)
        
        stats_1 = self._run_and_stat()
        
        time.sleep(1)
        
        with open(os.path.join(self.directory, "pipeline.py")) as fd:
            data = fd.read()
        data = data.replace(
            """["touch", self.targets[0]]""", 
            """["touch", "-f", self.targets[0]]""")
        with open(os.path.join(self.directory, "pipeline.py"), "w") as fd:
            fd.write(data)
        
        stats_2 = self._run_and_stat()
        
        for stat_1, stat_2 in zip(stats_1, stats_2):
            self.assertNotEqual(stat_1.st_mtime, stat_2.st_mtime)
    
    def test_change_python(self):
        with open(os.path.join(self.directory, "pipeline.py"), "w") as fd:
            fd.write(pipeline)
        
        stats_1 = self._run_and_stat()
        
        time.sleep(1)
        
        with open(os.path.join(self.directory, "pipeline.py")) as fd:
            data = fd.read()
        data = data.replace(
            """pass""", 
            """fd.write("foo")""")
        with open(os.path.join(self.directory, "pipeline.py"), "w") as fd:
            fd.write(data)
        
        stats_2 = self._run_and_stat()
        
        for stat_1, stat_2 in zip(stats_1, stats_2):
            self.assertNotEqual(stat_1.st_mtime, stat_2.st_mtime)
    
    def _run_and_stat(self):
        subprocess.check_output([
            "doit", "run", "-f", os.path.join(self.directory, "pipeline.py"), 
            "-d", self.directory])
        return [os.stat(os.path.join(self.directory, x)) for x in self.targets]
    
if __name__ == "__main__":
    sys.exit(unittest.main())
