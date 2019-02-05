import spire

class TestTask(spire.Task):
    # Everything is pluralized and a list
    file_dep = ["dependency"]
    targets = ["target"]
    actions = (
        [["test", "-f", x] for x in file_dep] 
        + [["touch", x] for x in targets])
