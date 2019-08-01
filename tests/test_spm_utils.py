import textwrap
import unittest

import spire.spm

class TestSPMUtils(unittest.TestCase):
    def test_script(self):
        script = spire.spm.script([
            spire.spm.factorial_design.FactorialDesign(
                "/output",
                spire.spm.factorial_design.TwoSamplesTTest(
                    ["foo", "bar", "baz"], ["plip", "plop"])),
            spire.spm.ModelEstimation("/output/SPM.mat")
        ])
        self.assertEqual(
            script,
            textwrap.dedent("""\
                spm('defaults','fmri');
                spm_jobman('initcfg');
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
                matlabbatch{1}.spm.stats.factorial_design.globalm.glonorm = 1;
                matlabbatch{2}.spm.stats.fmri_est.spmmat = {'/output/SPM.mat'};
                matlabbatch{2}.spm.stats.fmri_est.write_residuals = 0;
                matlabbatch{2}.spm.stats.fmri_est.method.Classical = 1;
                spm_jobman('run',matlabbatch);
                exit();"""))
    
if __name__ == "__main__":
    unittest.main()
