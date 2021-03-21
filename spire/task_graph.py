import inspect

import doit

from .task_factory import TaskFactory

class TaskGraph(object):
    def __init__(self, tasks):
        # List of children for each Doit task
        self.children = {}
        # All Doit tasks (Spire and non-Spire)
        self.doit_tasks = {task.name: task for task in tasks}
        # Spire-only tasks
        self.spire_tasks = {
            task.basename: task for task in TaskFactory._task_registry}
        
        # NOTE: this is O(n^2).
        for task in tasks:
            children = []
            for other_task in tasks:
                if any(x in task.targets for x in other_task.file_dep):
                    children.append(other_task.name)
            
            self.children[task.name] = children
