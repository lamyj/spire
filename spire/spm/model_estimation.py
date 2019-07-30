import textwrap

from .spm_object import SPMObject

class ModelEstimation(SPMObject):
    def __init__(self, spmmat, write_residuals=False, method="Classical"):
        super().__init__("spm.stats.fmri_est")
        
        self.spmmat = spmmat
        self.write_residuals = write_residuals
        
        if method not in ["Classical", "Bayesian2"]:
            raise Exception("Unknown method: {}".format(method))
        self.method = method
        
        self.template = self.environment.from_string(textwrap.dedent("""\
            {{ id(index, name) }}.spmmat = {'{{ spmmat }}'};
            {{ id(index, name) }}.write_residuals = {{ write_residuals|int }};
            {{ id(index, name) }}.method.{{ method }} = 1;"""))
