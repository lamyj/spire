from . import misc

class TaskMeta(type):
    def __new__(class_, name, bases, dict_):
        if bases[0] is not TaskBase:
            if "basename" not in dict_:
                dict_["basename"] = name
            
            for singular, plural in [["action", "actions"], ["target", "targets"]]:
                if plural not in dict_:
                    if singular not in dict_:
                        raise Exception(
                            "Neither \"{}\" nor \"{}\" exist".format(
                                singular, plural))
                    else:
                        dict_[plural] = [dict_[singular]]
                elif singular not in dict_:
                    if len(dict_[plural]) == 1:
                        dict_[singular] = dict_[plural][0]
            
            if "file_dep" not in dict_:
                raise Exception("No \"file_dep\" specified")
            elif not isinstance(dict_["file_dep"], (list, tuple)):
                dict_["file_dep"] = [dict_["file_dep"]]
            
        return type.__new__(class_, name, bases, dict_)

# Base class with the correct meta-class. Required to keep compatibility between
# Python 2 and Python 3; borrowed from six.
# https://bitbucket.org/gutworth/six/src/92e1c74/six.py?at=default&fileviewer=file-view-default#six.py-815:824
TaskBase = type.__new__(TaskMeta, "TaskBase", (), {})

class Task(TaskBase): 
    clean = True

    @misc.classproperty
    def uptodate(cls):
        return misc.uptodate(cls)

    @classmethod
    def create_doit_tasks(class_):
        if class_ is Task:
            return

        if getattr(class_, "skipped", False):
            return None
        else:
            fields = ["basename", "file_dep", "targets", "actions", "clean", "uptodate"]
            return {x: getattr(class_, x) for x in fields}
