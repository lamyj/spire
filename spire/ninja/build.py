class Build(object):
    def __init__(self, rule, inputs, outputs, **kwargs):
        self.rule = rule
        self.inputs = inputs
        self.outputs = outputs
        self.variables = kwargs
