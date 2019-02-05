import spire

class Factory(spire.TaskFactory):
    def __init__(self, name):
        spire.TaskFactory.__init__(self, name)
        self.file_dep = ["{}.dep".format(name)]
        self.targets = ["{}.target".format(name)]
        self.actions = (
            [["test", "-f", x] for x in self.file_dep] 
            + [["touch", x] for x in self.targets])

class EmptyFactory(spire.TaskFactory):
    def __init__(self, name):
        spire.TaskFactory.__init__(self, name)
        self.file_dep = ["{}.dep".format(name)]
        self.targets = ["{}.target".format(name)]
        self.actions = (
            [["test", "-f", x] for x in self.file_dep] 
            + [["touch", x] for x in self.targets])

tasks = [Factory(x) for x in ["foo", "bar", "baz"]]
top_level_task = Factory("plip")
