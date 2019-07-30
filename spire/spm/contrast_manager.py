import textwrap

import numpy

from .spm_object import SPMObject

class Contrast(object):
    def __init__(self, name, weights, replication="none"):
        self.name = name
        self.weights = numpy.asarray(weights)
        if len(self.weights.shape) > 1:
            raise NotImplementedError("F-contrast not implemented")
        
        if replication not in ["none", "repl", "replsc", "sess", "both", "bothsc"]:
            raise NotImplementedError(
                "Unknown replication mode: {}".format(replication))
        self.replication = replication

class ContrastManager(SPMObject):
    def __init__(self, spmmat, contrasts=None):
        super().__init__("spm.stats.con")
        
        self.spmmat = spmmat
        self.contrasts = contrasts or []
        
        self.template = self.environment.from_string(textwrap.dedent("""\
            {{ id(index, name) }}.spmmat = {'{{ spmmat }}'};
            {% for contrast in contrasts -%}
            {{ id(index, name) }}.consess{{ "{"+(loop.index|string)+"}" }}.tcon.name = '{{ contrast.name }}';
            {{ id(index, name) }}.consess{{ "{"+(loop.index|string)+"}" }}.tcon.weights = [{{ contrast.weights|join(" ") }}];
            {{ id(index, name) }}.consess{{ "{"+(loop.index|string)+"}" }}.tcon.sessrep = '{{ contrast.replication }}';
            {% endfor -%}
            {{ id(index, name) }}.delete = 1;"""))
