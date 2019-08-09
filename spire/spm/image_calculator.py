import textwrap

from .spm_object import SPMObject

class ImageCalculator(SPMObject):
    """ The image calculator is for performing user-specified algebraic 
        manipulations on a set of images. The result is being written out as an 
        image. The user is prompted to supply images to work on, a filename for 
        the output  image, and the expression to evaluate. The expression should 
        be a standard MATLAB expression, within which the images should be 
        referred to as i1, i2, i3,... etc.
    """
    
    def __init__(self, inputs, output, expression, dtype="int16"):
        SPMObject.__init__(self, "spm.util.imcalc")
        
        self.inputs = inputs
        self.output = output
        self.expression = expression
        self.dtype = dtype
        
        self._dtypes_map = {
            "uint8": 2,
            "int16": 4,
            "int32": 8,
            "float32": 16,
            "float64": 64,
            "int8": 256,
            "uint16": 512,
            "uint32": 768,
        }
        
        self.template = textwrap.dedent("""\
            {{ id(index, name) }}.input = {
            {% for input in inputs -%}
            {{ ((id(index, name)+".input = {")|length)*" " }}'{{ input }}'
            {% endfor -%}
            {{ ((id(index, name)+".input = {")|length)*" " }}};
            {{ id(index, name) }}.output = '{{ output.name }}';
            {{ id(index, name) }}.outdir = {'{{ output.parent }}'};
            {{ id(index, name) }}.expression = '{{ expression }}';
            {{ id(index, name) }}.var = struct('name', {}, 'value', {});
            {{ id(index, name) }}.options.dmtx = 0;
            {{ id(index, name) }}.options.mask = 0;
            {{ id(index, name) }}.options.interp = 1;
            {{ id(index, name) }}.options.dtype = {{ _dtypes_map[dtype] }};""")
    
    def _get_file_dep(self):
        return sorted(set(seilf.inputs))
    
    def _get_targets(self):
        return [self.output]
