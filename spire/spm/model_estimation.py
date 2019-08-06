import textwrap

from .spm_object import SPMObject

class ModelEstimation(SPMObject):
    def __init__(self, design, write_residuals=False, method="Classical"):
        super().__init__("spm.stats.fmri_est")
        
        self.design = design
        self.write_residuals = write_residuals
        
        if method not in ["Classical", "Bayesian2"]:
            raise Exception("Unknown method: {}".format(method))
        self.method = method
        
        self.template = textwrap.dedent("""\
            {{ id(index, name) }}.spmmat = {'{{ design.spmmat }}'};
            {{ id(index, name) }}.write_residuals = {{ write_residuals|int }};
            {{ id(index, name) }}.method.{{ method }} = 1;""")
    
    def _get_targets(self):
        directory = self.design.spmmat.parent
        targets = [
            self.design.spmmat, 
            directory/"mask.nii", directory/"ResMS.nii", directory/"RPV.nii"]
        
        # FIXME: the parameter maps ("beta_XXXX.nii") are missing from the list.
        # How can we compute the from self.design.design?
            
        return targets
