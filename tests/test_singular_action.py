import os
import unittest
import subprocess
import sys

from test_base import TestBase

class TestSingularAction(TestBase):
    
    file_dep = ["dependency"]
    
    def test(self):
        subprocess.check_output([
            "doit", "run", 
            "-f", os.path.join(self.here, "pipeline_singular_action.py"), 
            "-d", self.directory])
        entries = os.listdir(self.directory)
        self.assertTrue("target" in entries)

if __name__ == "__main__":
    sys.exit(unittest.main())
