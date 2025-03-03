import collections.abc
import functools
import inspect
import pathlib
import typing

import spire

path = typing.Union[str, pathlib.Path]

#: Type hint for file_dep arguments to a function
file_dep = typing.NewType("file_dep", path)

#: Type hint for target arguments to a function
target = typing.NewType("target", path)

def _get_task_info(action, *args, **kwargs):
    """Return the file_dep and targets of a bound function"""
    
    signature = inspect.signature(action)
    parameters = signature.parameters
    arguments = signature.bind(*args, **kwargs).arguments
    
    # Check if argument is a "true" sequence, i.e. not a string/Path
    is_iterable = lambda x: (
        (
            isinstance(x, collections.abc.Iterable)
            or isinstance(x, collections.abc.Sequence))
        and not isinstance(x, (str, pathlib.Path)))
    
    file_deps = []
    targets = []
    for name, value in parameters.items():
        if value.annotation in [file_dep, target]:
            if name not in arguments:
                continue
            
            argument = arguments[name]
            
            target_list = file_deps if value.annotation is file_dep else targets
            
            if is_iterable(argument):
                target_list.extend(argument)
            elif argument is not None:
                target_list.append(argument)
    
    return file_deps, targets

def _create_factory_class(
        function, get_action, extra={},
        file_dep_modifier=None, targets_modifier=None):
    """Create a wrapper TaskFactory-derived class around function
    
    :param get_action: function creating the task action
    :param extra: extra members to be added to the class
    """
    def __init__(self, *args, **kwargs):
        file_dep, targets = _get_task_info(function, *args, **kwargs)
        
        spire.TaskFactory.__init__(self, str(targets[0]))
        self.file_dep = file_dep_modifier(file_dep) if file_dep_modifier else file_dep
        self.targets = targets_modifier(targets) if targets_modifier else targets
        self.actions = [get_action(*args, **kwargs)]
    
    cls = type(
        function.__name__, (spire.TaskFactory, ),
        {"__init__": __init__, "__doc__": function.__doc__} | extra)
    
    functools.update_wrapper(cls.__init__, function)
    # Update the original signature to include "self"
    signature = inspect.signature(function)
    cls.__init__.__signature__ = signature.replace(
        parameters=[
            inspect.Parameter("self", inspect.Parameter.POSITIONAL_OR_KEYWORD),
            *signature.parameters.values()])
    cls.__module__ = function.__module__
    
    return cls

def task_factory(action=None, /, file_dep=None, targets=None):
    """Convert a function to a TaskFactory having the function as its only
    action. The file_dep and targets are extracted from the type hints of
    the function"""
    
    def decorator(action):
        return _create_factory_class(
            action, lambda *args, **kwargs: (action, args, kwargs),
            {"action": action},
            file_dep_modifier=file_dep, targets_modifier=targets)
    
    if action is not None:
        return decorator(action)
    else:
        return decorator

def command_factory(action=None, /, file_dep=None, targets=None):
    """Convert a function to a TaskFactory having the command returned as a
    list by the function as its only action. The file_dep and targets are
    extracted from the type hints of the function"""
    
    def decorator(action):
        return _create_factory_class(
            action, lambda *args, **kwargs: action(*args, **kwargs),
            file_dep_modifier=file_dep, targets_modifier=targets)
    
    if action is not None:
        return decorator(action)
    else:
        return decorator
