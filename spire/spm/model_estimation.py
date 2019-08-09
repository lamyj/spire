import textwrap

from .spm_object import SPMObject

class ModelEstimation(SPMObject):
    """ Estimation of model parameters using classical (ReML - Restricted 
        Maximum Likelihood) or Bayesian algorithms. After  parameter estimation,
        the 'Results' button can be used to specify contrasts that will produce 
        Statistical Parametric Maps (SPMs) or Posterior Probability Maps (PPMs) 
        and tables of statistics.
    """
    
    def __init__(self, design, write_residuals=False, method="Classical"):
        SPMObject.__init__(self, "spm.stats.fmri_est")
        
        self.design = design
        self.write_residuals = write_residuals
        
        if method not in ["Classical", "Bayesian2"]:
            raise Exception("Unknown method: {}".format(method))
        self.method = method
        
        self.template = textwrap.dedent("""\
            {{ id(index, name) }}.spmmat = {'{{ design.spmmat }}'};
            {{ id(index, name) }}.write_residuals = {{ write_residuals|int }};
            {{ id(index, name) }}.method.{{ method }} = 1;""")
    
    def _get_file_dep(self):
        return [self.design.spmmat]
    
    def _get_targets(self):
        directory = self.design.spmmat.parent
        targets = [
            self.design.spmmat, 
            directory/"mask.nii", directory/"ResMS.nii", directory/"RPV.nii"]
        
        # FIXME: the parameter maps ("beta_XXXX.nii") are missing from the list.
        # How can we compute the from self.design.design?
            
        return targets
