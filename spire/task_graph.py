import inspect

import doit

class TaskGraph(object):
    def __init__(self):
        self.tasks = {}
        self.children = {}
    
    def build(self, creators):
        self.tasks = self._get_tasks(creators)
        
        for name, (doit_task, spire_task) in self.tasks.items():
            dependencies = doit_task.setup_tasks + doit_task.task_dep
            for dependency in dependencies:
                self.children.setdefault(dependency, []).append(doit_task.name)
    
    def _get_tasks(self, creators):
        doit_tasks = []
        spire_tasks = {}
        for name, creator, line in creators:
            result = creator()
            
            if isinstance(result, dict):
                dicts = [result]
            elif inspect.isgenerator(result):
                dicts = [x for x in result]
            elif result is None:
                continue
            
            for dict_ in dicts:
                dict_["name"] = dict_.pop("basename", creator.__name__)
                # Replace None with "" to avoid an error on task creation
                dict_["file_dep"] = [x or "" for x in dict_["file_dep"]]
                
                doit_tasks.append(doit.task.dict_to_task(dict_))
                spire_tasks[dict_["name"]] = creator.__self__
        
        doit_tasks = doit.control.TaskControl(doit_tasks).tasks
        if sorted(list(doit_tasks.keys())) != sorted(list(spire_tasks.keys())):
            raise Exception("doit tasks and Spire tasks do not match")
        
        tasks = {
            key: (doit_tasks[key], spire_tasks[key]) 
            for key in doit_tasks.keys()}
        
        return tasks
