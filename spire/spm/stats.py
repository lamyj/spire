import itertools

from .. import TaskFactory
from . import model_estimation, utils

class Stats(TaskFactory):
    """ Perform statistical analyses with SPM using given design and contrasts.
    """
    
    def __init__(self, name, design, contrasts):
        TaskFactory.__init__(self, name)
        
        estimation = model_estimation.ModelEstimation(design)
        
        steps = [design, estimation, contrasts]
        
        self.file_dep = design.file_dep
        self.targets = list(set(itertools.chain(*[x.targets for x in steps])))
        self.actions = [
            # Make sure SPM.mat is not there when we start
            ["rm", "-f", design.spmmat],
            (utils.run, (steps,))
        ]
