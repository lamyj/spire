import numpy

def to_matlab(obj, name=None):
    """ Convert a Python object to a string which can be parsed by Matlab.
        The following types are supported :
        
          * numpy.ndarray of dimensions 1 and 2 : converted to a matrix
          * list : converted to a cell array
          * string and scalar types : converted to litterals
          
        For nested structures (arrays and lists), the elements are 
        recursively converted.
    """
    
    obj = normalize(obj)
    
    result = ""
    if isinstance(obj, numpy.ndarray):
        if obj.dtype.fields:
            result = []
            for index, item in zip(numpy.ndindex(*obj.shape), numpy.nditer(obj, ["refs_ok"])):
                for field in obj.dtype.fields:
                    result.append("{}({}).{} = {};".format(
                        name, 
                        ", ".join(str(1+x) for x in index), 
                        field, to_matlab(item[field].item())
                    ))
            result = "\n".join(result)
        else:
            normalized = obj
            if normalized.ndim == 1:
                normalized = normalized.reshape((1, normalized.shape[0]))
            
            # Strings are stored as cells array
            use_cell_array = (
                normalized.dtype == numpy.object
                or numpy.issubdtype(normalized.dtype, numpy.unicode_)
                or numpy.issubdtype(normalized.dtype, numpy.string_))
            
            if use_cell_array:
                result += "{ "
            else :
                result += "[ "
            
            if normalized.shape[0] > 1:
                result += "\n"
            
            for row in normalized :
                result += " ".join(to_matlab(x) for x in row)
                if normalized.shape[0] > 1:
                    result += "\n";
            
            if use_cell_array:
                result += " }"
            else :
                result += " ]"
    elif isinstance(obj, str):
        result = "'{}'".format(obj)
    elif numpy.isscalar(obj):
        result = "{}".format(obj)
    else :
        raise Exception(
            "Cannot convert an object of type {}".format(
                repr(type(obj).__name__)))

    return result

def normalize(obj):
    """ Normalize a Python object with the following rules:
        - list of dictionaries are mapped to a numpy record array
        - other lists are mapped to a numpy array of objects
    """
    
    if isinstance(obj, list):
        array = numpy.asarray(obj, object)
        
        if len(array) > 0:
            items = list(x.item() for x in numpy.nditer(array, ["refs_ok"]))
            
            if all(isinstance(x, dict) for x in items):
                fields = [x.keys() for x in items]
                if not all(x == fields[0] for x in fields):
                    raise Exception(
                        "Cannot normalize array of dicts with inhomogeneous fields")
                dtype = [(x, object) for x in fields[0]]
                
                recarray = numpy.empty(len(items), dtype)
                for index, item in enumerate(items):
                    for field in fields[0]:
                        recarray[field][index] = item[field]
                return recarray.reshape(array.shape)
            else:
                first = next(array.flat)
                if all(type(first) == type(x) for x in array.flat):
                    array = array.astype(type(first))
                return array
        else:
            return array
    else:
        return obj
