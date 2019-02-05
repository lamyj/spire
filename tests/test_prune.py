import itertools
import os
import subprocess
import sys
import unittest

from test_base import TestBase

class TestPrune(TestBase):
    
    suffixes = ["", "_object", "_list"]
    file_dep = [
        "{}root{}.dep".format(prefix, suffix) 
        for prefix, suffix in itertools.product(["", "skipped_"], suffixes)]
    
    def test(self):
        subprocess.check_output([
            "doit", "run", "-f", os.path.join(self.here, "pipeline_prune.py"), 
            "-d", self.directory])
        entries = os.listdir(self.directory)
        
        prefixes = ["root", "leaf"]
        
        targets = [
            "{}{}.target".format(prefix, suffix) 
            for prefix, suffix in itertools.product(prefixes, self.suffixes)]
        for target in targets:
            self.assertTrue(target in entries)
        
        skipped_targets = [
            "skipped_{}{}.target".format(prefix, suffix) 
            for prefix, suffix in itertools.product(prefixes, self.suffixes)]
        for target in skipped_targets:
            self.assertTrue(target not in entries)

if __name__ == "__main__":
    sys.exit(unittest.main())
