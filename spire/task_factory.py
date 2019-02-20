from . import misc

class TaskFactory(object):
    """ Base class for task factory objects. Derived classes must follow this
        example:
        
        >>> class MyTask(TaskFactory):
        ...     def __init__(self, input, output):
        ...         # Initialize base class
        ...         TaskFactory.__init__(self, "my basename")
        ...         
        ...         # Define mandatory members
        ...         self.file_dep = [input]
        ...         self.targets = [output]
        ...         self.actions = ["touch {}".format(output)]
        
        A task can then be created as such:
        >>> task = MyTask("foo", "bar")
        
        If the task is not re-used, storing it in an object is not mandatory.
    """
    
    _task_registry = []
    
    def __init__(self, basename):
        self.basename = basename
        self.clean = True
        TaskFactory._task_registry.append(self)
    
    def as_task_dict(self):
        if getattr(self, "skipped", False):
            return None
        else:
            fields = ["basename", "file_dep", "targets", "actions", "clean", "uptodate"]
            return {x: getattr(self, x) for x in fields}
    
    @property
    def target(self):
        if len(self.targets) == 1:
            return self.targets[0]
        else:
            raise Exception(
                "Ambiguous call to \"target\" ({} target{})".format(
                    len(self.targets), "" if len(self.targets)==0 else "s"))
    
    uptodate = property(misc.uptodate)
