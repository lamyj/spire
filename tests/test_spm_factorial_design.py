import pathlib
import textwrap
import unittest

import spire.spm

class TestSPMFactorialDesign(unittest.TestCase):
    
    def test_masking(self):
        masking = spire.spm.factorial_design.Masking()
        expected = textwrap.dedent("""\
            matlabbatch{1}.spm.stats.factorial_design.masking.tm.tm_none = 1;
            matlabbatch{1}.spm.stats.factorial_design.masking.im = 1;
            matlabbatch{1}.spm.stats.factorial_design.masking.em = {''};""")
        self.assertEqual(masking.get_script(1), expected)
        
        masking = spire.spm.factorial_design.Masking(
            threshold_mode="absolute", threshold=123)
        self.assertEqual(
            masking.get_script(1), 
            expected.replace("tm.tm_none = 1", "tma.athresh = 123"))
        
        masking = spire.spm.factorial_design.Masking(
            threshold_mode="relative", threshold=0.99)
        self.assertEqual(
            masking.get_script(1), 
            expected.replace("tm.tm_none = 1", "tmr.rthresh = 0.99"))
        
        masking = spire.spm.factorial_design.Masking(implicit=False)
        self.assertEqual(
            masking.get_script(1), expected.replace("im = 1", "im = 0"))
        
        masking = spire.spm.factorial_design.Masking(explicit="foo.nii,1")
        self.assertEqual(
            masking.get_script(1), 
            expected.replace("em = {''}", "em = {'foo.nii,1'}"))
    
    def test_global_calculation(self):
        global_calculation = spire.spm.factorial_design.GlobalCalculation()
        expected = "matlabbatch{1}.spm.stats.factorial_design.globalc.g_omit = 1;"
        self.assertEqual(global_calculation.get_script(1), expected)
        
        global_calculation = spire.spm.factorial_design.GlobalCalculation(
            "user", [12, 34])
        self.assertEqual(
            global_calculation.get_script(1), 
            expected.replace("g_omit = 1", "g_user.global_uval = [12;34]"))
        
        global_calculation = spire.spm.factorial_design.GlobalCalculation("mean")
        self.assertEqual(
            global_calculation.get_script(1), 
            expected.replace("g_omit = 1", "g_mean = 1"))
    
    def test_global_normalization(self):
        global_normalization = spire.spm.factorial_design.GlobalNormalization()
        expected = textwrap.dedent("""\
            matlabbatch{1}.spm.stats.factorial_design.globalm.gmsca.gmsca_no = 1;
            matlabbatch{1}.spm.stats.factorial_design.globalm.glonorm = 1;""")
        self.assertEqual(global_normalization.get_script(1), expected)
        
        global_normalization = spire.spm.factorial_design.GlobalNormalization(42)
        self.assertEqual(
            global_normalization.get_script(1), 
            expected.replace("gmsca_no = 1", "gmsca_yes.gmscv = 42"))
        
        global_normalization = spire.spm.factorial_design.GlobalNormalization(
            mode="proportional")
        self.assertEqual(
            global_normalization.get_script(1), 
            expected.replace("glonorm = 1", "glonorm = 2"))
        
        global_normalization = spire.spm.factorial_design.GlobalNormalization(
            mode="ancova")
        self.assertEqual(
            global_normalization.get_script(1), 
            expected.replace("glonorm = 1", "glonorm = 3"))
    
    def test_covariates(self):
        covariates = spire.spm.factorial_design.Covariates([])
        self.assertEqual(
            covariates.get_script(1), 
            "matlabbatch{1}.spm.stats.factorial_design.cov = "
                "struct('c', {}, 'cname', {}, 'iCFI', {}, 'iCC', {});")
        
        covariates = spire.spm.factorial_design.Covariates([
            spire.spm.factorial_design.Covariate("foo", [1, 2, 3]),
            spire.spm.factorial_design.Covariate("bar", [4, 5])
        ])
        expected = textwrap.dedent("""\
            matlabbatch{1}.spm.stats.factorial_design.cov(1).c = [
                                                                  1
                                                                  2
                                                                  3
                                                                  ];
            matlabbatch{1}.spm.stats.factorial_design.cov(1).cname = 'foo';
            matlabbatch{1}.spm.stats.factorial_design.cov(1).iCFI = 1;
            matlabbatch{1}.spm.stats.factorial_design.cov(1).iCC = 1;
            matlabbatch{1}.spm.stats.factorial_design.cov(2).c = [
                                                                  4
                                                                  5
                                                                  ];
            matlabbatch{1}.spm.stats.factorial_design.cov(2).cname = 'bar';
            matlabbatch{1}.spm.stats.factorial_design.cov(2).iCFI = 1;
            matlabbatch{1}.spm.stats.factorial_design.cov(2).iCC = 1;
            """)
        self.assertEqual(covariates.get_script(1), expected)
        
        known_interactions = ["With Factor 1", "With Factor 2", "With Factor 3"]
        self.maxDiff = None
        for index, interactions in enumerate(known_interactions):
            covariates = spire.spm.factorial_design.Covariates([
                spire.spm.factorial_design.Covariate(
                    "foo", [1, 2, 3], interactions=interactions),
                spire.spm.factorial_design.Covariate("bar", [4, 5])
            ])
            self.assertEqual(
                covariates.get_script(1), 
                expected.replace("(1).iCFI = 1", "(1).iCFI = {}".format(2+index)))
        
        known_centering = [
            "Factor 1 mean", "Factor 2 mean", "Factor 3 mean",
            "No centering", "User specified value", "As implied by ANCOVA", 
            "GM"]
        self.maxDiff = None
        for index, centering in enumerate(known_centering):
            covariates = spire.spm.factorial_design.Covariates([
                spire.spm.factorial_design.Covariate(
                    "foo", [1, 2, 3], centering=centering),
                spire.spm.factorial_design.Covariate("bar", [4, 5])
            ])
            self.assertEqual(
                covariates.get_script(1), 
                expected.replace("(1).iCC = 1", "(1).iCC = {}".format(2+index)))
    
    def test_one_sample_t_test(self):
        test = spire.spm.factorial_design.OneSampleTTest(
            ["scan1.nii,1", "scan2.nii,1"])
        self.assertEqual(
            test.get_script(1),
            textwrap.dedent("""\
                matlabbatch{1}.spm.stats.factorial_design.des.t1.scans = {
                                                                          'scan1.nii,1'
                                                                          'scan2.nii,1'
                                                                          };"""))
    
    def test_two_samples_t_test(self):
        scans = ["scan1.nii,1", "scan2.nii,1"], ["scan3.nii,1", "scan4.nii,1"]
        expected = textwrap.dedent("""\
            matlabbatch{1}.spm.stats.factorial_design.des.t2.scans1 = {
                                                                       'scan1.nii,1'
                                                                       'scan2.nii,1'
                                                                       };
            matlabbatch{1}.spm.stats.factorial_design.des.t2.scans2 = {
                                                                       'scan3.nii,1'
                                                                       'scan4.nii,1'
                                                                       };
            matlabbatch{1}.spm.stats.factorial_design.des.t2.dept = 0;
            matlabbatch{1}.spm.stats.factorial_design.des.t2.variance = 1;
            matlabbatch{1}.spm.stats.factorial_design.des.t2.gmsca = 0;
            matlabbatch{1}.spm.stats.factorial_design.des.t2.ancova = 0;""")
        test = spire.spm.factorial_design.TwoSamplesTTest(*scans)
        self.assertEqual(test.get_script(1), expected)
        
        test = spire.spm.factorial_design.TwoSamplesTTest(
             *scans, independence=False)
        self.assertEqual(test.get_script(1), expected.replace("dept = 0", "dept = 1"))
        
        test = spire.spm.factorial_design.TwoSamplesTTest(
            *scans, equal_variance=True)
        self.assertEqual(test.get_script(1), expected.replace("variance = 1", "variance = 0"))
        
        test = spire.spm.factorial_design.TwoSamplesTTest(
            *scans, grand_mean_scaling=True)
        self.assertEqual(test.get_script(1), expected.replace("gmsca = 0", "gmsca = 1"))
        
        test = spire.spm.factorial_design.TwoSamplesTTest(*scans, ancova=True)
        self.assertEqual(test.get_script(1), expected.replace("ancova = 0", "ancova = 1"))
        
    def test_paired_t_test(self):
        scans = [
            ["scan1.nii,1", "scan2.nii,1"], ["scan3.nii,1", "scan4.nii,1"],
            ["scan5.nii,1", "scan6.nii,1"]]
        expected = textwrap.dedent("""\
            matlabbatch{1}.spm.stats.factorial_design.des.pt.pair(1) = {
                                                                        'scan1.nii,1'
                                                                        'scan2.nii,1'
                                                                        };
            matlabbatch{1}.spm.stats.factorial_design.des.pt.pair(2) = {
                                                                        'scan3.nii,1'
                                                                        'scan4.nii,1'
                                                                        };
            matlabbatch{1}.spm.stats.factorial_design.des.pt.pair(3) = {
                                                                        'scan5.nii,1'
                                                                        'scan6.nii,1'
                                                                        };
            matlabbatch{1}.spm.stats.factorial_design.des.pt.gmsca = 0;
            matlabbatch{1}.spm.stats.factorial_design.des.pt.ancova = 0;""")
        
        test = spire.spm.factorial_design.PairedTTest(scans)
        self.assertEqual(test.get_script(1), expected)
        
        test = spire.spm.factorial_design.PairedTTest(
            scans, grand_mean_scaling=True)
        self.assertEqual(
            test.get_script(1), expected.replace("gmsca = 0", "gmsca = 1"))
        
        test = spire.spm.factorial_design.PairedTTest(
            scans, ancova=True)
        self.assertEqual(
            test.get_script(1), expected.replace("ancova = 0", "ancova = 1"))

    def test_anova(self):
        scans = [
            ["scan1.nii,1", "scan2.nii,1"], ["scan3.nii,1", "scan4.nii,1"],
            ["scan5.nii,1", "scan6.nii,1"]]
        expected = textwrap.dedent("""\
            matlabbatch{1}.spm.stats.factorial_design.des.anova.icell(1).scans = {
                                                                                  'scan1.nii,1'
                                                                                  'scan2.nii,1'
                                                                                  };
            matlabbatch{1}.spm.stats.factorial_design.des.anova.icell(2).scans = {
                                                                                  'scan3.nii,1'
                                                                                  'scan4.nii,1'
                                                                                  };
            matlabbatch{1}.spm.stats.factorial_design.des.anova.icell(3).scans = {
                                                                                  'scan5.nii,1'
                                                                                  'scan6.nii,1'
                                                                                  };
            matlabbatch{1}.spm.stats.factorial_design.des.anova.dept = 0;
            matlabbatch{1}.spm.stats.factorial_design.des.anova.variance = 1;
            matlabbatch{1}.spm.stats.factorial_design.des.anova.gmsca = 0;
            matlabbatch{1}.spm.stats.factorial_design.des.anova.ancova = 0;""")
        
        test = spire.spm.factorial_design.ANOVA(scans)
        self.assertEqual(test.get_script(1), expected)
        
        test = spire.spm.factorial_design.ANOVA(scans, independance=False)
        self.assertEqual(
            test.get_script(1), expected.replace("dept = 0", "dept = 1"))
        
        test = spire.spm.factorial_design.ANOVA(scans, equal_variance=True)
        self.assertEqual(
            test.get_script(1), 
            expected.replace("variance = 1", "variance = 0"))
        
        test = spire.spm.factorial_design.ANOVA(scans, grand_mean_scaling=True)
        self.assertEqual(
            test.get_script(1), expected.replace("gmsca = 0", "gmsca = 1"))
        
        test = spire.spm.factorial_design.ANOVA(scans, ancova=True)
        self.assertEqual(
            test.get_script(1), expected.replace("ancova = 0", "ancova = 1"))
    
    def test_factorial_design(self):
        design = spire.spm.factorial_design.FactorialDesign(
            "/output",
            spire.spm.factorial_design.TwoSamplesTTest(
                ["foo", "bar", "baz"], ["plip", "plop"]))
        
        self.assertEqual(design.spmmat, pathlib.Path("/output/SPM.mat"))
        self.assertEqual(
            design.get_script(1),
            textwrap.dedent("""\
                matlabbatch{1}.spm.stats.factorial_design.dir = {'/output'};
                matlabbatch{1}.spm.stats.factorial_design.des.t2.scans1 = {
                                                                           'foo'
                                                                           'bar'
                                                                           'baz'
                                                                           };
                matlabbatch{1}.spm.stats.factorial_design.des.t2.scans2 = {
                                                                           'plip'
                                                                           'plop'
                                                                           };
                matlabbatch{1}.spm.stats.factorial_design.des.t2.dept = 0;
                matlabbatch{1}.spm.stats.factorial_design.des.t2.variance = 1;
                matlabbatch{1}.spm.stats.factorial_design.des.t2.gmsca = 0;
                matlabbatch{1}.spm.stats.factorial_design.des.t2.ancova = 0;
                matlabbatch{1}.spm.stats.factorial_design.cov = struct('c', {}, 'cname', {}, 'iCFI', {}, 'iCC', {});
                matlabbatch{1}.spm.stats.factorial_design.multi_cov = struct('files', {}, 'iCFI', {}, 'iCC', {});
                matlabbatch{1}.spm.stats.factorial_design.masking.tm.tm_none = 1;
                matlabbatch{1}.spm.stats.factorial_design.masking.im = 1;
                matlabbatch{1}.spm.stats.factorial_design.masking.em = {''};
                matlabbatch{1}.spm.stats.factorial_design.globalc.g_omit = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalm.gmsca.gmsca_no = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalm.glonorm = 1;"""))
    
if __name__ == "__main__":
    unittest.main()
