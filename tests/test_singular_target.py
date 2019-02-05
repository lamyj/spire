import os
import unittest
import subprocess
import sys

from test_base import TestBase

class TestSingularTarget(TestBase):
    file_dep = ["root.dep"]
    
    def test(self):
        subprocess.check_output([
            "doit", "run", 
            "-f", os.path.join(self.here, "pipeline_singular_target.py"), 
            "-d", self.directory])
        entries = os.listdir(self.directory)
        for target in ["root.target", "leaf.target"]:
            self.assertTrue(target in entries)

if __name__ == "__main__":
    sys.exit(unittest.main())
