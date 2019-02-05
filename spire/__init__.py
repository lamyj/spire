import inspect
import itertools
import logging

import doit

from .task import Task
from .task_factory import TaskFactory
from .task_graph import TaskGraph

################################################################################
# Replace doit's task loader to include objects created by TaskFactory         #
################################################################################

doit_loader_load_tasks = None
def spire_load_tasks(*args, **kwargs):
    tasks = doit_loader_load_tasks(*args, **kwargs)
    
    for object_ in TaskFactory._task_registry:
        if getattr(object_, "skipped", False):
            continue
        
        dict_ = object_.as_task_dict()
        if dict_ is None:
            continue
        
        dict_["name"] = dict_.pop("basename")
        # Replace None with "" to avoid an error on task creation
        dict_["file_dep"] = [x or "" for x in dict_["file_dep"]]
            
        tasks.append(doit.task.dict_to_task(dict_))
            
    return tasks
    
if doit.loader.load_tasks != spire_load_tasks:
    doit_loader_load_tasks = doit.loader.load_tasks
    doit.loader.load_tasks = spire_load_tasks

################################################################################
# Prune the task graph from tasks having None in their file_dep                #
################################################################################

def prune():
    task_list = []
    spire_task_dict = {}
    
    # Look at creators in the caller's globals 
    caller = inspect.getouterframes(inspect.currentframe())[1][0]
    
    # https://github.com/pydoit/doit/blob/0.31.1/doit/loader.py#L129-L133
    creators = doit.loader._get_task_creators(caller.f_globals, [])
    creators.sort(key=lambda obj: obj[2])
    creators.extend(
        [(None, x.as_task_dict, None) for x in TaskFactory._task_registry])
    
    graph = TaskGraph()
    graph.build(creators)
    
    to_skip = []
    for (doit_task, spire_task) in graph.tasks.values():
        if "" in doit_task.file_dep:
            to_skip.append(doit_task.name)
    
    # Breadth-first traversal of the dependency tree, marking request tasks and
    # their descendents as skipped
    while len(to_skip) > 0:
        root = to_skip.pop()
        doit_task, spire_task = graph.tasks[root]
        if not getattr(spire_task, "skipped", False):
            logging.warning("Skipping {}".format(root))
            spire_task.skipped = True
            to_skip.extend(graph.children.get(root, []))

################################################################################
# Representation of the task graph in the Graphviz format                      #
################################################################################

def graph(tasks_only=False):
    task_list = []
    spire_task_dict = {}
    
    # Look at creators in the caller's globals 
    caller = inspect.getouterframes(inspect.currentframe())[1][0]
    
    # https://github.com/pydoit/doit/blob/0.31.1/doit/loader.py#L129-L133
    creators = doit.loader._get_task_creators(caller.f_globals, [])
    creators.sort(key=lambda obj: obj[2])
    creators.extend(
        [(None, x.as_task_dict, None) for x in TaskFactory._task_registry])
    
    graph = TaskGraph()
    graph.build(creators)
    
    def quote(name):
        return "\"{}\"".format(name.replace("\"", "\\\""))
    
    lines = ["digraph {"]
    
    deps_and_targets = set()
    for name, (doit_task, _) in graph.tasks.items():
        lines.append("    {}[shape=box];".format(quote(name)))
        if not tasks_only:
            for entry in itertools.chain(doit_task.file_dep, doit_task.targets):
                if entry not in deps_and_targets:
                    deps_and_targets.add(entry)
                    lines.append(
                        "    {}[shape=parallelogram];".format(quote(entry)))
        
            # We can create the edges now: the task, deps and targets node are
            # already present
            for entry in doit_task.file_dep:
                lines.append("    {} -> {};".format(quote(entry), quote(name)))
            for entry in doit_task.targets:
                lines.append("    {} -> {};".format(quote(name), quote(entry)))
    
    if tasks_only:
        # We need to wait for all task nodes to be created
        for name, children in graph.children.items():
            lines.extend(
                "    {} -> {};".format(quote(name), quote(x)) 
                for x in children)
            

    lines.extend(["}", ""])
    
    return "\n".join(lines)
