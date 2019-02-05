import spire

class TestSingularAction(spire.Task):
    file_dep = ["dependency"]
    targets = ["target"]
    action = ["touch", targets[0]] # Single action
