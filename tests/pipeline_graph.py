import spire

class A(spire.Task):
    file_dep = ["A.dep"]
    targets = ["A.target"]
    actions = ["foo"]

class B(spire.Task):
    file_dep = A.targets
    targets = ["B.target"]
    actions = ["bar"]
