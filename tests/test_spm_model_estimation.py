import textwrap
import unittest

import spire.spm

class TestSPMModelEstimation(unittest.TestCase):
    def setUp(self):
        self.expected = textwrap.dedent("""\
            matlabbatch{1}.spm.stats.fmri_est.spmmat = {'/output/SPM.mat'};
            matlabbatch{1}.spm.stats.fmri_est.write_residuals = 0;
            matlabbatch{1}.spm.stats.fmri_est.method.Classical = 1;""")
    
    def test_default(self):
        estimation = spire.spm.ModelEstimation("/output/SPM.mat")
        self.assertEqual(estimation(1), self.expected)
    
    def test_write_residuals(self):
        estimation = spire.spm.ModelEstimation("/output/SPM.mat", True)
        self.assertEqual(
            estimation(1), 
            self.expected.replace("write_residuals = 0", "write_residuals = 1"))
    
    def test_method(self):
        estimation = spire.spm.ModelEstimation(
            "/output/SPM.mat", method="Bayesian2")
        self.assertEqual(
            estimation(1), 
            self.expected.replace("Classical = 1", "Bayesian2 = 1"))
    
if __name__ == "__main__":
    unittest.main()
