import os
import shutil
import tempfile
import unittest

class TestBase(unittest.TestCase):
    def setUp(self):
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.directory = tempfile.mkdtemp()
        
        for path in self.file_dep:
            with open(os.path.join(self.directory, path), "w"):
                pass
    
    def tearDown(self):
        shutil.rmtree(self.directory)
