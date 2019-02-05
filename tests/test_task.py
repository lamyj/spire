import os
import unittest
import subprocess
import sys

from test_base import TestBase

class TestTask(TestBase):
    
    file_dep = ["dependency"]
    targets = ["target"]
    
    def test_list(self):
        self.assertTrue(
            b"TestTask"
            in subprocess.check_output([
                "doit", "list", 
                "-f", os.path.join(self.here, "pipeline_task.py"), 
                "-d", self.directory]))
    
    def test_run(self):
        subprocess.check_output([
            "doit", "run", "-f", os.path.join(self.here, "pipeline_task.py"), 
            "-d", self.directory])
        entries = os.listdir(self.directory)
        for target in self.targets:
            self.assertTrue(target in entries)
    
    def test_clean(self):
        subprocess.check_output([
            "doit", "run", "-f", os.path.join(self.here, "pipeline_task.py"), 
            "-d", self.directory])
        
        # Spire tasks are automatically cleanable
        subprocess.check_output([
            "doit", "clean", "-f", os.path.join(self.here, "pipeline_task.py"), 
            "-d", self.directory])
        entries = os.listdir(self.directory)
        for target in self.targets:
            self.assertTrue(target not in entries)

if __name__ == "__main__":
    sys.exit(unittest.main())
