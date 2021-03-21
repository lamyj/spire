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
    caller = inspect.getouterframes(inspect.currentframe())[1][0]
    tasks = doit.loader.load_tasks(caller.f_globals)
    
    graph = TaskGraph(tasks)
    
    to_skip = []
    for name, doit_task in graph.doit_tasks.items():
        if "" in doit_task.file_dep:
            to_skip.append(name)
    
    while len(to_skip) > 0:
        root = to_skip.pop()
        spire_task = graph.spire_tasks.get(root)
        if spire_task is None:
            logging.info("Not a spire task: {}".format(root))
            continue
        if not getattr(spire_task, "skipped", False):
            logging.warning("Skipping {}".format(root))
            spire_task.skipped = True
            to_skip.extend(graph.children.get(root, []))

################################################################################
# Representation of the task graph in the Graphviz format                      #
################################################################################

def graph(name_mapper=None):
    caller = inspect.getouterframes(inspect.currentframe())[1][0]
    tasks = doit.loader.load_tasks(caller.f_globals)
    
    graph = TaskGraph(tasks)
    
    if name_mapper is None:
        name_mapper = lambda x: x
    
    def quote(name):
        return "\"{}\"".format(name_mapper(name).replace("\"", "\\\""))
    
    lines = ["digraph {"]
    
    file_deps = set()
    targets = set()
    nodes = set()
    for task in graph.doit_tasks.values():
        file_deps.update(task.file_dep)
        targets.update(task.targets)
    for name, doit_task in graph.doit_tasks.items():
        if name not in nodes:
            lines.append("    {}[shape=box];".format(quote(name)))
        for entry in graph.doit_tasks[name].file_dep:
            if entry not in targets:
                if entry not in nodes:
                    lines.append(
                        "    {}[shape=box,color=blue];".format(quote(entry)))
                    nodes.add(entry)
                lines.append("    {} -> {};".format(quote(entry), quote(name)))
        for entry in graph.doit_tasks[name].targets:
            if entry not in file_deps and entry != name:
                if entry not in nodes:
                    lines.append(
                        "    {}[shape=box,color=blue];".format(quote(entry)))
                    nodes.add(entry)
                lines.append("    {} -> {};".format(quote(name), quote(entry)))
    
    for name, doit_task in graph.doit_tasks.items():
        for child in graph.children[name]:
            lines.append("    {} -> {};".format(quote(name), quote(child)))
    
    lines.extend(["}", ""])
    
    return "\n".join(lines)
