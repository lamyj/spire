import spire

class Root(spire.Task):
    # targets is a list with a single item
    file_dep = ["root.dep"]
    targets = ["root.target"]
    actions = (
        [["test", "-f", x] for x in file_dep] 
        + [["touch", targets[0]]])

class TestSingularTarget(spire.Task):
    file_dep = [Root.target] # Access single target of Root
    target = "leaf.target" # target is a scalar
    actions = [["test", "-f", x] for x in file_dep] + [["touch", target]]
