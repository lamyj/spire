import numpy

from . import matlab

class Tool(object):
    """ Base class for SPM tools.
    """
    
    class Config(object):
        """ Configuration element of an SPM tool.
        """
        
        def _get_parameters(self):
            """ Return a dictionary of configuration items using the names from 
                SPM batches as keys. This function must be implemented by all
                concrete subclasses.
            """
            
            raise NotImplementedError()
        
        @property
        def parameters(self):
            return self._get_parameters()
    
    # Name of the tool
    name = None
    
    def __init__(self, root):
        # SPM root directory
        self.root = root
    
    def _get_script(self):
        """ Return the Matlab script to run the tool. This function must be 
            implemented by all concrete subclasses.
        """
        
        raise NotImplementedError()
    
    @property
    def script(self):
        return self._get_script()
    
    @classmethod
    def _generate_script(self, prefix, obj):
        """ Recursively generate a Matlab script from a nested dictionary of
            configuration parameters.
        """
        
        script = []
        
        for key, value in obj.items():
            if isinstance(value, dict):
                sub_script = Tool._generate_script(
                   "{}.{}".format(prefix, key), value)
                script.extend(sub_script)
            else:
                script.append("{}.{} = {}".format(
                    prefix, key, matlab.to_matlab(value)))
        
        return script
