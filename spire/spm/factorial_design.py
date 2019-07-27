import numpy

from .tool import Tool

class FactorialDesign(Tool):
    """ Factorial design specification
    
        cf. https://github.com/spm/spm12/blob/master/config/spm_cfg_factorial_design.m
    """
    
    name = "stats.factorial_design"
    
    class OneSampleTTest(Tool.Config):
        """ One-sample t-test, containing:
            - the scans
        """
        
        name = "t1"
        
        def __init__(self, scans=None):
            self.scans = scans or []
        
        def _get_parameters(self):
            result = {"scans": self.scans}
            return result
    
    class TwoSampleTTest(Tool.Config):
        """ Two-sample t-test, containing:
            - The scans forming the two groups,
            - The independance between measurements
            - The equality of variance between measurements
            - The grand mean scaling
            - The ANCOVA-by-factor regressors
        """
        
        name = "t2"
        
        def __init__(
                self, scans1=None, scans2=None, independance=True,
                variance_equality=False, grand_mean_scaling=False,
                ancova=False):
            self.scans1 = scans1 or []
            self.scans2 = scans2 or []
            self.independance = independance
            self.variance_equality = variance_equality
            self.grand_mean_scaling = grand_mean_scaling
            self.ancova = ancova
        
        def _get_parameters(self):
            result = {
                "scans1": self.scans1,
                "scans2": self.scans2,
                "dept": int(not self.independance),
                "variance": int(not self.variance_equality),
                "gmsca": int(self.grand_mean_scaling),
                "ancova": int(self.ancova)
            }
            return result
    
    class PairedTTest(Tool.Config):
        """ Two-sample t-test, containing:
            - The pairs of scans,
            - The grand mean scaling
            - The ANCOVA-by-factor regressors
        """
        
        name = "pt"
        
        def __init__(
                self, pairs=None, grand_mean_scaling=False,
                ancova=False):
            self.pairs = pairs or []
            self.grand_mean_scaling = grand_mean_scaling
            self.ancova = ancova
        
        def _get_parameters(self):
            result = {
                "pair": [{"scans": pair} for pair in self.pairs],
                "gmsca": int(self.grand_mean_scaling),
                "ancova": int(self.ancova)
            }
            return result
    
#    class MultipleRegression(Tool.Config):
#        pass
#    
#    class OneWayANOVA(Tool.Config):
#        pass
#    
#    class OneWayANOVAWithinSubject(Tool.Config):
#        pass
#    

    class Factor(Tool.Config):
        """ Factor of experimental design, containing:
            
            * The name of the factor
            * The number of levels
            * The independance between measurements
            * The equality of variance between measurements
            * The grand mean scaling
            * The ANCOVA-by-factor regressors
        """
        
        name = "fact"
        
        def __init__(self, name, levels, independance=True,
                     variance_equality=False, grand_mean_scaling=False,
                     ancova=False):
            self.name = name
            self.levels = levels
            self.independance = independance
            self.variance_equality = variance_equality
            self.grand_mean_scaling = grand_mean_scaling
            self.ancova = ancova
        
        def _get_parameters(self):
            result = {
                "name" : self.name,
                "levels" : self.levels,
                "dept" : int(not self.independance),
                "variance" : int(not self.variance_equality),
                "gmsca" : int(self.grand_mean_scaling),
                "ancova" : int(self.ancova)
            }
            return result
    
    class Cell(Tool.Config):
        """ Group a scans
        """
        
        name = "icell"
        
        def __init__(self, levels, scans):
            self.levels = levels
            self.scans = scans
        
        def _get_parameters(self):
            result = {
                "levels" : numpy.asarray(self.levels, int),
                "scans" : self.scans, 
            }
            return result

    class FullFactorial(Tool.Config):
        name = "fd"
        
        def __init__(self, factors, cells):
            self.factors = factors
            self.cells = cells
        
        def _get_parameters(self):
            result = { 
                FactorialDesign.Factor.name: [x.parameters for x in self.factors],
                FactorialDesign.Cell.name: [x.parameters for x in self.cells]
            }
            return result
#    
#    class FlexibleFactorial(Tool.Config):
#        pass
    
    class Covariate(Tool.Config):
        """ Covariate/nuisance variable, containing :
        
            * The name of the covariate
            * A vector of values
            * The eventual interaction between the covariate and a chosen
              experimental factor
            * The centering method
        """
        
        Interaction = {
            "None": 1, 
            "With Factor 1": 2, "With Factor 2": 3, "With Factor 3": 4 }
        
        Centering = {
            "Overall mean": 1, 
            "Factor 1 mean": 2, "Factor 2 mean": 3, "Factor 3 mean": 4, 
            "No centering": 5, "User specified value": 6, 
            "As implied by ANCOVA": 7, "GM": 8 }
        
        def __init__(self, name, values, interaction="None", centering="Overall mean"):
            self.name = name
            self.values = values
            self.interaction = interaction
            self.centering = centering 
        
        def _get_parameters(self):
            result = {
                "cname" : self.name,
                "c" : numpy.asarray(self.values),
                "iCFI" : self.Interaction[self.interaction],
                "iCC" : self.Centering[self.centering],
            }
            
            return result
    
    class Masking(Tool.Config):
        """ Masking options, containing :
        
            * The type and eventual value of threshold masking
            * The implicit mask value
            * The explicit mask image
        """
        
        def __init__(self, threshold_masking=None, threshold_value=None, 
                     implicit_mask=True, explicit_mask=None):
            self.threshold_masking = threshold_masking
            if threshold_masking == None :
                self.threshold_value = 1
            elif threshold_masking == "absolute" :
                self.threshold_value = threshold_value
            elif threshold_masking == "relative" :
                self.threshold_value = threshold_value
            self.implicit_mask = implicit_mask
            self.explicit_mask = explicit_mask or ""
        
        def _get_parameters(self):
            result = {
                "im" : int(self.implicit_mask),
                "em" : [self.explicit_mask]
            }
            
            if self.threshold_masking is None :
                result["tm.tm_none"] = self.threshold_value
            elif self.threshold_masking == "absolute" :
                result["tma.athresh"] = self.threshold_value
            elif self.threshold_masking == "relative" :
                result["tmr.rthresh"] = self.threshold_value
            
            return result
    
    class GlobalCalculation(Tool.Config):
        """ Estimation of the global effects, containing :
        
            * The estimation mode
            * The eventual estimation value
        """
        
        def __init__(self, mode=None, values=None):
            self.mode = mode
            self.values = values or []
        
        def _get_parameters(self):
            result = {}
            
            if self.mode is None :
                result["g_omit"] = 1
            elif self.mode == "user" :
                result["g_user.global_uval"] = numpy.asarray(self.values)
            elif self.mode == "mean" :
                result["g_mean"] = 1
            
            return result
    
    class GlobalNormalization(Tool.Config):
        """ Global normalization options, containing :
        
            * The grand mean scaling value
            * The normalization flag
        """
        
        def __init__(self, grand_mean_scaled_value=None, normalization=None):
            self.grand_mean_scaled_value = grand_mean_scaled_value
            self.normalization = normalization
        
        def _get_parameters(self):
            result = {}
            
            if self.grand_mean_scaled_value is None :
                result["gmsca.gmsca_no"] = 1
            else :
                result["gmsca.gmsca_yes.gmscv"] = self.grand_mean_scaled_value
            
            if self.normalization is None :
                result["glonorm"] = 1
            elif self.normalization == "proportional" :
                result["glonorm"] = 2
            elif self.normalization == "ancova" :
                result["glonorm"] = 3
            
            return result
    
    def __init__(self, root, output_directory, design, covariates=None, 
                 masking=None, global_calculation=None, global_normalization=False) :
        Tool.__init__(self, root)
        self.output_directory = output_directory
        self.design = design
        self.covariates = covariates or []
        self.masking = masking or FactorialDesign.Masking()
        self.global_calculation = global_calculation or FactorialDesign.GlobalCalculation()
        self.global_normalization = global_normalization or FactorialDesign.GlobalNormalization()
    
    def _get_script(self):
        script = []
        
        script.extend(Tool._generate_script(
            self.name, {"dir" : [self.output_directory]}))
        script.extend(Tool._generate_script(
            "{}.des.{}".format(self.name, self.design.name), 
            self.design.parameters))
        
        if self.covariates :
            covariates = [x.parameters for x in self.covariates]
        else :
            covariates = numpy.empty(
                (), [(x, object) for x in ["c", "cname", "iCFI", "iCC"]])
        script.extend(Tool._generate_script(self.name, {"cov": covariates}))
        
        script.extend(Tool._generate_script(
            self.name,
            {"multi_cov": numpy.empty( 
                (), [(x, object) for x in ["files", "iCFI", "iCC"]])}))
        
        script.extend(Tool._generate_script(
            "{}.masking".format(self.name), self.masking.parameters))
        script.extend(Tool._generate_script(
            "{}.globalc".format(self.name), self.global_calculation.parameters))
        script.extend(Tool._generate_script(
            "{}.globalm".format(self.name), 
            self.global_normalization.parameters))
        
        return script
