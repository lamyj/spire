import os
import unittest
import subprocess
import sys

from test_base import TestBase

class TestTaskFactory(TestBase):
    
    file_dep = ["{}.dep".format(x) for x in ["foo", "bar", "baz", "plip"]]
    
    def test(self):
        subprocess.check_output([
            "doit", "run", 
            "-f", os.path.join(self.here, "pipeline_task_factory.py"), 
            "-d", self.directory])
        
        entries = os.listdir(self.directory)
        for name in self.file_dep:
            self.assertTrue(name.replace(".dep", ".target") in entries)

if __name__ == "__main__":
    sys.exit(unittest.main())
