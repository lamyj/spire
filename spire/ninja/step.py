from . import Rule, Build

class Step(Rule, Build):
    def __init__(self, name, description, command, inputs, outputs):
        Rule.__init__(self, name, description, command)
        Build.__init__(self, name, inputs, outputs)
