import textwrap

from .spm_object import SPMObject

class ModelReview(SPMObject):
    def __init__(self, spmmat, display="matrix", output_format="pdf"):
        super().__init__("spm.stats.review")
        
        self.spmmat = spmmat
        
        if display not in ["matrix", "orth", "factors", "covariates", "covariance"]:
            raise Exception("Unknown display mode: {}".format(display))
        self.display = display
        
        if output_format not in ["ps", "eps", "pdf", "jpg", "png", "tif", "fig"]:
            raise Exception("Unknown output format: {}".format(output_format))
        self.output_format = output_format
        
        self.template = self.environment.from_string(textwrap.dedent("""\
            {{ id(index, name) }}.spmmat = {'{{ spmmat }}'};
            {{ id(index, name) }}.display.{{ display }} = 1;
            {{ id(index, name) }}.print = '{{ output_format }}';"""))
