import hashlib
import pickle

import doit.action

def _command_digest(action):
    hash = hashlib.sha1()
    for item in action.action:
        hash.update(str(item).encode())
    return hash.hexdigest()

def _python_digest(action):
    hash = hashlib.sha1()
    hash.update(action.py_callable.__code__.co_code)
    hash.update(pickle.dumps(action.args))
    hash.update(pickle.dumps(action.kwargs))
    return hash.hexdigest()

_digest = {
    doit.action.CmdAction: _command_digest,
    doit.action.PythonAction: _python_digest
}

def _check(task, values):
    digests = [_digest[type(action)](action) for action in task.actions]
    task.value_savers.append(lambda: {"actions_hash": digests})
    return values.get("actions_hash", None) == digests

def uptodate(self):
    return [_check]

class classproperty(object):
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, _, class_):
        return self.fget(class_)
