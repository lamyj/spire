import jinja2

class SPMObject(object):
    def __init__(self, name):
        self.name = name
        self.environment = jinja2.Environment()
        self.environment.globals.update(id=__class__._get_id)
    
    def __call__(self, index):
        return self.template.render(index=index, **vars(self))
    
    @staticmethod
    def _get_id(index, name):
        return "matlabbatch{"+str(index)+"}."+name
