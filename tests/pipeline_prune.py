import logging

import spire

def get_actions(file_dep, targets):
    return [["test", "-f", x] for x in file_dep] + [["touch", x] for x in targets]

class Root(spire.Task):
    file_dep = ["root.dep"]
    target = "root.target"
    actions = get_actions(file_dep, [target])

class Leaf(spire.Task):
    file_dep = Root.target
    target = "leaf.target"
    actions = get_actions([file_dep], [target])

class SkippedRoot(spire.Task):
    file_dep = [None, "skipped_root.dep"]
    target = "skipped_root.target"
    actions = get_actions(file_dep, [target])

class SkippedLeaf(spire.Task):
    file_dep = SkippedRoot.target
    target = "skipped_leaf.target"
    actions = get_actions([file_dep], [target])

class RootObject(spire.TaskFactory):
    def __init__(self):
        spire.TaskFactory.__init__(self, "RootObject")
        self.file_dep = ["root_object.dep"]
        self.targets = ["root_object.target"]
        self.actions = get_actions(self.file_dep, self.targets)

class LeafObject(spire.TaskFactory):
    def __init__(self, root):
        spire.TaskFactory.__init__(self, "LeafObject")
        self.file_dep = root.targets
        self.targets = ["leaf_object.target"]
        self.actions = get_actions(self.file_dep, self.targets)

class MyTask(spire.TaskFactory):
    def __init__(self, file_dep, targets):
        spire.TaskFactory.__init__(self, targets[0])
        self.file_dep = file_dep
        self.targets = targets
        self.actions = get_actions(self.file_dep, self.targets)

# Top-level task objects
root_object = MyTask(["root_object.dep"], ["root_object.target"])
leaf_object = MyTask(root_object.targets, ["leaf_object.target"])

skipped_root_object = MyTask(
    ["skipped_root_object.dep", None], ["skipped_root_object.target"])
skipped_leaf_object = MyTask(
    skipped_root_object.targets, ["skipped_leaf_object.target"])

# Task objects in lists
root_list = [MyTask(["root_list.dep"], ["root_list.target"])]
leaf_list = [MyTask(root_list[0].targets, ["leaf_list.target"])]

skipped_root_list = [MyTask([None], ["skipped_root_list.target"])]
skipped_leaf_list = [MyTask(skipped_root_list[0].targets, ["skipped_leaf_list.target"])]

logging.basicConfig(level=logging.ERROR)
spire.prune()
