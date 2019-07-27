import textwrap
import unittest

import numpy
import spire.spm

class TestSPMFactorialDesign(unittest.TestCase):
    def test_one_sample_t_test(self):
        test = spire.spm.FactorialDesign.OneSampleTTest(
            ["scan1.nii,1", "scan2.nii,1"])
        design = spire.spm.FactorialDesign("spm", "study", test)
        
        self.assertEqual(
            spire.spm.script([design], False, False),
            textwrap.dedent("""\
                matlabbatch{1}.spm.stats.factorial_design.dir = { 'study' };
                matlabbatch{1}.spm.stats.factorial_design.des.t1.scans = { 'scan1.nii,1' 'scan2.nii,1' };
                matlabbatch{1}.spm.stats.factorial_design.cov = struct('c', {  }, 'cname', {  }, 'iCFI', {  }, 'iCC', {  });
                matlabbatch{1}.spm.stats.factorial_design.multi_cov = struct('files', {  }, 'iCFI', {  }, 'iCC', {  });
                matlabbatch{1}.spm.stats.factorial_design.masking.im = 1;
                matlabbatch{1}.spm.stats.factorial_design.masking.em = { '' };
                matlabbatch{1}.spm.stats.factorial_design.masking.tm.tm_none = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalc.g_omit = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalm.gmsca.gmsca_no = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalm.glonorm = 1;"""))
    
    def test_two_samples_t_test(self):
        test = spire.spm.FactorialDesign.TwoSampleTTest(
            ["scan1.nii,1", "scan2.nii,1"], ["scan3.nii,1", "scan4.nii,1"])
        design = spire.spm.FactorialDesign("spm", "study", test)
        
        self.assertEqual(
            spire.spm.script([design], False, False),
            textwrap.dedent("""\
                matlabbatch{1}.spm.stats.factorial_design.dir = { 'study' };
                matlabbatch{1}.spm.stats.factorial_design.des.t2.scans1 = { 'scan1.nii,1' 'scan2.nii,1' };
                matlabbatch{1}.spm.stats.factorial_design.des.t2.scans2 = { 'scan3.nii,1' 'scan4.nii,1' };
                matlabbatch{1}.spm.stats.factorial_design.des.t2.dept = 0;
                matlabbatch{1}.spm.stats.factorial_design.des.t2.variance = 1;
                matlabbatch{1}.spm.stats.factorial_design.des.t2.gmsca = 0;
                matlabbatch{1}.spm.stats.factorial_design.des.t2.ancova = 0;
                matlabbatch{1}.spm.stats.factorial_design.cov = struct('c', {  }, 'cname', {  }, 'iCFI', {  }, 'iCC', {  });
                matlabbatch{1}.spm.stats.factorial_design.multi_cov = struct('files', {  }, 'iCFI', {  }, 'iCC', {  });
                matlabbatch{1}.spm.stats.factorial_design.masking.im = 1;
                matlabbatch{1}.spm.stats.factorial_design.masking.em = { '' };
                matlabbatch{1}.spm.stats.factorial_design.masking.tm.tm_none = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalc.g_omit = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalm.gmsca.gmsca_no = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalm.glonorm = 1;"""))
    
    def test_paired_t_test(self):
        test = spire.spm.FactorialDesign.PairedTTest(
            [["scan1.nii,1", "scan2.nii,1"], ["scan3.nii,1", "scan4.nii,1"]])
        design = spire.spm.FactorialDesign("spm", "study", test)
        
        self.assertEqual(
            spire.spm.script([design], False, False),
            textwrap.dedent("""\
                matlabbatch{1}.spm.stats.factorial_design.dir = { 'study' };
                matlabbatch{1}.spm.stats.factorial_design.des.pt.pair = struct('scans', { { 'scan1.nii,1' 'scan2.nii,1' } { 'scan3.nii,1' 'scan4.nii,1' } });
                matlabbatch{1}.spm.stats.factorial_design.des.pt.gmsca = 0;
                matlabbatch{1}.spm.stats.factorial_design.des.pt.ancova = 0;
                matlabbatch{1}.spm.stats.factorial_design.cov = struct('c', {  }, 'cname', {  }, 'iCFI', {  }, 'iCC', {  });
                matlabbatch{1}.spm.stats.factorial_design.multi_cov = struct('files', {  }, 'iCFI', {  }, 'iCC', {  });
                matlabbatch{1}.spm.stats.factorial_design.masking.im = 1;
                matlabbatch{1}.spm.stats.factorial_design.masking.em = { '' };
                matlabbatch{1}.spm.stats.factorial_design.masking.tm.tm_none = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalc.g_omit = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalm.gmsca.gmsca_no = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalm.glonorm = 1;"""))
    
    def test_full_factorial(self):
        factors = [
            spire.spm.FactorialDesign.Factor("foo", [1, 2]),
            spire.spm.FactorialDesign.Factor("bar", [3, 4, 5])]
        cells = [
            spire.spm.FactorialDesign.Cell([1, 4], ["scan1", "scan2"]),
            spire.spm.FactorialDesign.Cell([2, 3], ["scan3"])
        ]
        test = spire.spm.FactorialDesign.FullFactorial(factors, cells)
        
        design = spire.spm.FactorialDesign("spm", "study", test)
        
        self.assertEqual(
            spire.spm.script([design], False, False),
            textwrap.dedent("""\
                matlabbatch{1}.spm.stats.factorial_design.dir = { 'study' };
                matlabbatch{1}.spm.stats.factorial_design.des.fd.fact = struct('name', { 'foo' 'bar' }, 'levels', { [ 1 2 ] [ 3 4 5 ] }, 'dept', { 0 0 }, 'variance', { 1 1 }, 'gmsca', { 0 0 }, 'ancova', { 0 0 });
                matlabbatch{1}.spm.stats.factorial_design.des.fd.icell = struct('levels', { [ 1 4 ] [ 2 3 ] }, 'scans', { { 'scan1' 'scan2' } { 'scan3' } });
                matlabbatch{1}.spm.stats.factorial_design.cov = struct('c', {  }, 'cname', {  }, 'iCFI', {  }, 'iCC', {  });
                matlabbatch{1}.spm.stats.factorial_design.multi_cov = struct('files', {  }, 'iCFI', {  }, 'iCC', {  });
                matlabbatch{1}.spm.stats.factorial_design.masking.im = 1;
                matlabbatch{1}.spm.stats.factorial_design.masking.em = { '' };
                matlabbatch{1}.spm.stats.factorial_design.masking.tm.tm_none = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalc.g_omit = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalm.gmsca.gmsca_no = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalm.glonorm = 1;"""))
    
    def test_covariates(self):
        covariates = [
            spire.spm.FactorialDesign.Covariate("foo", [1,2]),
            spire.spm.FactorialDesign.Covariate(
                "bar", [3,4], "With Factor 1", "No centering")]
        design = spire.spm.FactorialDesign(
            "", "", spire.spm.FactorialDesign.OneSampleTTest([]), covariates)
        self.assertEqual(
            spire.spm.script([design], False, False),
            textwrap.dedent("""\
                matlabbatch{1}.spm.stats.factorial_design.dir = { '' };
                matlabbatch{1}.spm.stats.factorial_design.des.t1.scans = {  };
                matlabbatch{1}.spm.stats.factorial_design.cov = struct('cname', { 'foo' 'bar' }, 'c', { [ 1 2 ] [ 3 4 ] }, 'iCFI', { 1 2 }, 'iCC', { 1 5 });
                matlabbatch{1}.spm.stats.factorial_design.multi_cov = struct('files', {  }, 'iCFI', {  }, 'iCC', {  });
                matlabbatch{1}.spm.stats.factorial_design.masking.im = 1;
                matlabbatch{1}.spm.stats.factorial_design.masking.em = { '' };
                matlabbatch{1}.spm.stats.factorial_design.masking.tm.tm_none = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalc.g_omit = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalm.gmsca.gmsca_no = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalm.glonorm = 1;"""))
    
    def test_masking(self):
        absolute_masking = spire.spm.FactorialDesign.Masking(
            "absolute", 90, False, "mask.nii")
        relative_masking = spire.spm.FactorialDesign.Masking(
            "relative", 0.9, False, "mask.nii")
        design = spire.spm.FactorialDesign(
            "", "", spire.spm.FactorialDesign.OneSampleTTest([]))
        
        design.masking = absolute_masking
        self.assertEqual(
            spire.spm.script([design], False, False),
            textwrap.dedent("""\
                matlabbatch{1}.spm.stats.factorial_design.dir = { '' };
                matlabbatch{1}.spm.stats.factorial_design.des.t1.scans = {  };
                matlabbatch{1}.spm.stats.factorial_design.cov = struct('c', {  }, 'cname', {  }, 'iCFI', {  }, 'iCC', {  });
                matlabbatch{1}.spm.stats.factorial_design.multi_cov = struct('files', {  }, 'iCFI', {  }, 'iCC', {  });
                matlabbatch{1}.spm.stats.factorial_design.masking.im = 0;
                matlabbatch{1}.spm.stats.factorial_design.masking.em = { 'mask.nii' };
                matlabbatch{1}.spm.stats.factorial_design.masking.tma.athresh = 90;
                matlabbatch{1}.spm.stats.factorial_design.globalc.g_omit = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalm.gmsca.gmsca_no = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalm.glonorm = 1;"""))
        
        design.masking = relative_masking
        self.assertEqual(
            spire.spm.script([design], False, False),
            textwrap.dedent("""\
                matlabbatch{1}.spm.stats.factorial_design.dir = { '' };
                matlabbatch{1}.spm.stats.factorial_design.des.t1.scans = {  };
                matlabbatch{1}.spm.stats.factorial_design.cov = struct('c', {  }, 'cname', {  }, 'iCFI', {  }, 'iCC', {  });
                matlabbatch{1}.spm.stats.factorial_design.multi_cov = struct('files', {  }, 'iCFI', {  }, 'iCC', {  });
                matlabbatch{1}.spm.stats.factorial_design.masking.im = 0;
                matlabbatch{1}.spm.stats.factorial_design.masking.em = { 'mask.nii' };
                matlabbatch{1}.spm.stats.factorial_design.masking.tmr.rthresh = 0.9;
                matlabbatch{1}.spm.stats.factorial_design.globalc.g_omit = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalm.gmsca.gmsca_no = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalm.glonorm = 1;"""))
    
    def test_global_calculation(self):
        mean = spire.spm.FactorialDesign.GlobalCalculation("mean")
        user = spire.spm.FactorialDesign.GlobalCalculation("user", [1, 2])
        design = spire.spm.FactorialDesign(
            "", "", spire.spm.FactorialDesign.OneSampleTTest([]))
        
        design.global_calculation = mean
        self.assertEqual(
            spire.spm.script([design], False, False),
            textwrap.dedent("""\
                matlabbatch{1}.spm.stats.factorial_design.dir = { '' };
                matlabbatch{1}.spm.stats.factorial_design.des.t1.scans = {  };
                matlabbatch{1}.spm.stats.factorial_design.cov = struct('c', {  }, 'cname', {  }, 'iCFI', {  }, 'iCC', {  });
                matlabbatch{1}.spm.stats.factorial_design.multi_cov = struct('files', {  }, 'iCFI', {  }, 'iCC', {  });
                matlabbatch{1}.spm.stats.factorial_design.masking.im = 1;
                matlabbatch{1}.spm.stats.factorial_design.masking.em = { '' };
                matlabbatch{1}.spm.stats.factorial_design.masking.tm.tm_none = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalc.g_mean = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalm.gmsca.gmsca_no = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalm.glonorm = 1;"""))
        
        design.global_calculation = user
        self.assertEqual(
            spire.spm.script([design], False, False),
            textwrap.dedent("""\
                matlabbatch{1}.spm.stats.factorial_design.dir = { '' };
                matlabbatch{1}.spm.stats.factorial_design.des.t1.scans = {  };
                matlabbatch{1}.spm.stats.factorial_design.cov = struct('c', {  }, 'cname', {  }, 'iCFI', {  }, 'iCC', {  });
                matlabbatch{1}.spm.stats.factorial_design.multi_cov = struct('files', {  }, 'iCFI', {  }, 'iCC', {  });
                matlabbatch{1}.spm.stats.factorial_design.masking.im = 1;
                matlabbatch{1}.spm.stats.factorial_design.masking.em = { '' };
                matlabbatch{1}.spm.stats.factorial_design.masking.tm.tm_none = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalc.g_user.global_uval = [ 1 2 ];
                matlabbatch{1}.spm.stats.factorial_design.globalm.gmsca.gmsca_no = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalm.glonorm = 1;"""))
    
    def test_global_normalisation(self):
        gms = spire.spm.FactorialDesign.GlobalNormalization(42)
        normalization = spire.spm.FactorialDesign.GlobalNormalization(
            normalization="ancova")
        design = spire.spm.FactorialDesign(
            "", "", spire.spm.FactorialDesign.OneSampleTTest([]))
        
        design.global_normalization = gms
        self.assertEqual(
            spire.spm.script([design], False, False),
            textwrap.dedent("""\
                matlabbatch{1}.spm.stats.factorial_design.dir = { '' };
                matlabbatch{1}.spm.stats.factorial_design.des.t1.scans = {  };
                matlabbatch{1}.spm.stats.factorial_design.cov = struct('c', {  }, 'cname', {  }, 'iCFI', {  }, 'iCC', {  });
                matlabbatch{1}.spm.stats.factorial_design.multi_cov = struct('files', {  }, 'iCFI', {  }, 'iCC', {  });
                matlabbatch{1}.spm.stats.factorial_design.masking.im = 1;
                matlabbatch{1}.spm.stats.factorial_design.masking.em = { '' };
                matlabbatch{1}.spm.stats.factorial_design.masking.tm.tm_none = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalc.g_omit = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalm.gmsca.gmsca_yes.gmscv = 42;
                matlabbatch{1}.spm.stats.factorial_design.globalm.glonorm = 1;"""))
        
        design.global_normalization = normalization
        self.assertEqual(
            spire.spm.script([design], False, False),
            textwrap.dedent("""\
                matlabbatch{1}.spm.stats.factorial_design.dir = { '' };
                matlabbatch{1}.spm.stats.factorial_design.des.t1.scans = {  };
                matlabbatch{1}.spm.stats.factorial_design.cov = struct('c', {  }, 'cname', {  }, 'iCFI', {  }, 'iCC', {  });
                matlabbatch{1}.spm.stats.factorial_design.multi_cov = struct('files', {  }, 'iCFI', {  }, 'iCC', {  });
                matlabbatch{1}.spm.stats.factorial_design.masking.im = 1;
                matlabbatch{1}.spm.stats.factorial_design.masking.em = { '' };
                matlabbatch{1}.spm.stats.factorial_design.masking.tm.tm_none = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalc.g_omit = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalm.gmsca.gmsca_no = 1;
                matlabbatch{1}.spm.stats.factorial_design.globalm.glonorm = 3;"""))

if __name__ == "__main__":
    unittest.main()
