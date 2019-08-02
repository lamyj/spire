import textwrap
import unittest

import spire.spm

class TestSPMContrastManager(unittest.TestCase):
    def test_contrast_manager(self):
        manager = spire.spm.contrast_manager.ContrastManager(
            "/output/SPM.mat",
            [spire.spm.contrast_manager.Contrast("foo", [1, -1, 0])])
        expected = textwrap.dedent("""\
            matlabbatch{1}.spm.stats.con.spmmat = {'/output/SPM.mat'};
            matlabbatch{1}.spm.stats.con.consess{1}.tcon.name = 'foo';
            matlabbatch{1}.spm.stats.con.consess{1}.tcon.weights = [1 -1 0];
            matlabbatch{1}.spm.stats.con.consess{1}.tcon.sessrep = 'none';
            matlabbatch{1}.spm.stats.con.delete = 1;""")
        self.assertEqual(manager.get_script(1), expected)
        
        for replication in ["repl", "replsc", "sess", "both", "bothsc"]:
            manager = spire.spm.contrast_manager.ContrastManager(
                "/output/SPM.mat",
                [spire.spm.contrast_manager.Contrast("foo", [1, -1, 0], replication)])
            self.assertEqual(
                manager.get_script(1), 
                expected.replace(
                    "sessrep = 'none'", "sessrep = '{}'".format(replication)))
    
if __name__ == "__main__":
    unittest.main()
