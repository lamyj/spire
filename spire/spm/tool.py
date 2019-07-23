import numpy

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
    def _to_matlab(self, obj):
        """ Convert a Python object to a string which can be parsed by Matlab.
            The following types are supported :
            
              * numpy.ndarray of dimensions 1 and 2 : converted to a matrix
              * list : converted to a cell array
              * string and scalar types : converted to litterals
              
            For nested structures (arrays and lists), the elements are 
            recursively converted.
        """
        
        result = ""
        if isinstance(obj, numpy.ndarray):
            
            normalized = obj
            if normalized.ndim == 1:
                normalized = normalized.reshape((1, normalized.shape[0]))
            
            if normalized.dtype == numpy.object:
                result += "{ "
            else :
                result += "[ "
            
            if normalized.shape[0] > 1:
                result += "\n"
            
            for row in normalized :
                result += " ".join(Tool._to_matlab(x) for x in row)
                if normalized.shape[0] > 1:
                    result += "\n";
            
            if normalized.dtype == numpy.object:
                result += " }"
            else :
                result += " ]"
        elif isinstance(obj, list):
            result = "{{ {} }}".format(
                " ".join(Tool._to_matlab(x) for x in obj))
        elif isinstance(obj, str):
            result = "'{}'".format(obj)
        elif numpy.isscalar(obj):
            result = "{}".format(obj)
        else :
            raise Exception(
                "Cannot convert an object of type {}".format(
                    repr(type(obj).__name__)))
    
        return result
    
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
                    prefix, key, Tool._to_matlab(value)))
        
        return script
