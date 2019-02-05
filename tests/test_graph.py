import os
import sys
import unittest

import spire.__main__

from test_base import TestBase

class TestGraph(TestBase):
    file_dep = []
    
    def test(self):
        spire.__main__.graph(
            os.path.join(self.here, "pipeline_graph.py"),
            os.path.join(self.directory, "pipeline.dot"), 
            False, [])
        with open(os.path.join(self.directory, "pipeline.dot")) as fd:
            dot = fd.read()
        self.assertEqual(
            dot,
            "digraph {\n"
            "    \"A\"[shape=box];\n"
            "    \"A.dep\"[shape=parallelogram];\n"
            "    \"A.target\"[shape=parallelogram];\n"
            "    \"A.dep\" -> \"A\";\n"
            "    \"A\" -> \"A.target\";\n"
            "    \"B\"[shape=box];\n"
            "    \"B.target\"[shape=parallelogram];\n"
            "    \"A.target\" -> \"B\";\n"
            "    \"B\" -> \"B.target\";\n"
            "}\n"
        )
    
    def test_tasks_only(self):
        spire.__main__.graph(
            os.path.join(self.here, "pipeline_graph.py"),
            os.path.join(self.directory, "pipeline.dot"), 
            True, [])
        with open(os.path.join(self.directory, "pipeline.dot")) as fd:
            dot = fd.read()
        self.assertEqual(
            dot,
            "digraph {\n"
            "    \"A\"[shape=box];\n"
            "    \"B\"[shape=box];\n"
            "    \"A\" -> \"B\";\n"
            "}\n"
        )

if __name__ == "__main__":
    sys.exit(unittest.main())
