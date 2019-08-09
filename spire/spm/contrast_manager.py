import itertools
import textwrap

import numpy

from .spm_object import SPMObject

class Contrast(object):
    """ T-constrast of F-contrast.
    """
    
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
    """ Specify T and F contrasts
    """
    
    @staticmethod
    def pairwise(design, levels):
        """ Return all pairwise contrasts of factor with specified levels.
        """
        
        permutations = itertools.permutations(range(len(levels)), 2)
        contrasts = []
        for x,y in permutations:
            name = "{} < {}".format(levels[x], levels[y]) 
            
            weights = [0]*len(levels)
            weights[x] = -1
            weights[y] = +1
            
            contrasts.append(Contrast(name, weights))
        
        return ContrastManager(design, contrasts)
    
    def __init__(self, design, contrasts=None):
        SPMObject.__init__(self, "spm.stats.con")
        
        self.design = design
        self.contrasts = contrasts or []
        
        self.template = textwrap.dedent("""\
            {{ id(index, name) }}.spmmat = {'{{ design.spmmat }}'};
            {% for contrast in contrasts -%}
            {{ id(index, name) }}.consess{{ "{"+(loop.index|string)+"}" }}.tcon.name = '{{ contrast.name }}';
            {{ id(index, name) }}.consess{{ "{"+(loop.index|string)+"}" }}.tcon.weights = [{{ contrast.weights|join(" ") }}];
            {{ id(index, name) }}.consess{{ "{"+(loop.index|string)+"}" }}.tcon.sessrep = '{{ contrast.replication }}';
            {% endfor -%}
            {{ id(index, name) }}.delete = 1;""")
    
    def _get_file_dep(self):
        return [self.design.spmmat]
    
    def _get_targets(self):
        targets = [self.design.spmmat]
        
        directory = self.design.spmmat.parent
        for index, contrast in enumerate(self.contrasts):
            type_ = "F" if numpy.squeeze(contrast.weights).ndim > 1 else "T"
            targets.extend([
                directory/"con_{:04d}.nii".format(1+index),
                directory/"spm{}_{:04d}.nii".format(type_, 1+index)])
        return targets
