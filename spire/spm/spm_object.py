import jinja2

class SPMObject(object):
    def __init__(self, name):
        self.name = name
        self.environment = jinja2.Environment()
        self.environment.globals.update(id=__class__._get_id)
    
    def get_script(self, index):
        template = self.environment.from_string(self.template)
        return template.render(index=index, **vars(self))
    
    @property
    def targets(self):
        return self._get_targets()
    
    @staticmethod
    def _get_id(index, name):
        return "matlabbatch{"+str(index)+"}."+name
    
    def _get_targets(self):
        return []
    
    def __getstate__(self):
        state = self.__dict__.copy()
        del state["environment"]
        return state
    
    def __setstate__(self, state):
        self.__dict__.update(state)
        self.environment = jinja2.Environment()
        self.environment.globals.update(id=__class__._get_id)
