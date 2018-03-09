import random

import yaml

from . import logger

try:
    unicode
except NameError:
    # 'unicode' is undefined: Python 3
    basestring = (str,bytes)
else:
    # 'unicode' exists: Python 2
    pass

class Placeholder(object):
    def __init__(self, name):
        self.name = name
    
    def __getattr__(self, name):
        return self._get_random_string()
    
    def __getitem__(self, index):
        # Avoid infinite loops in some filters (e.g. join)
        if index > 10:
            raise IndexError()
        return self._get_random_string()
    
    def __str__(self):
        return self._get_random_string()
    
    def _get_random_string(self, length=8):
        return "__SPIRE_PLACEHOLDER_{}_{}".format(
            self.name, 
            "".join(
                random.choice("abcdefghijklmnopqrstuvwxyz") 
                for _ in range(length)))

def get_step_objects(kind, pipeline, step):
    if step not in pipeline["steps_dictionary"]:
        return Placeholder("{}_{}".format(kind, step))
    else:
        objects = pipeline["steps_dictionary"][step].get(kind)
        if any("__SPIRE_PLACEHOLDER_" in x for x in objects):
            return Placeholder("{}_{}".format(kind, step))
        else:
            return objects

def parse_pipeline(arguments, jinja_arguments, environment):
    """ Parse the Jinja+YAML pipeline description, normalize scalar items to 
        lists, and add a mapping from step ids to steps.
    """
    
    steps = {}
    
    environment.globals.update({
        "inputs": lambda x: get_step_objects("inputs", pipeline, x), 
        "outputs": lambda x: get_step_objects("outputs", pipeline, x) })
    
    pipeline = {"steps_dictionary": {}}
    done = False
    index = 0
    while not done:
        template = environment.get_template(arguments.pipeline)
        rendered = template.render(**jinja_arguments)
        pipeline = yaml.load(rendered)
        
        for step in pipeline["steps"]:
            for member in ["inputs", "outputs", "commands"]:
                if isinstance(step.get(member, None), basestring):
                    step[member] = [step[member]]
        
        pipeline["steps_dictionary"] = {}
        for step in pipeline["steps"]:
            if step["id"] in pipeline["steps_dictionary"]:
                raise Exception("Duplicate step: {}".format(step["id"]))
            else:
                pipeline["steps_dictionary"][step["id"]] = step
        
        done = True
        for step in pipeline["steps"]:
            for member in ["inputs", "outputs", "commands"]:
                if any("__SPIRE_PLACEHOLDER_" in x for x in step.get(member, [])):
                    done = False
                    break
            if not done:
                break
    
    logger.debug("Final pipeline:\n{}\n{}\n{}".format(
        40*"-", yaml.safe_dump(pipeline["steps"]), 40*"-"))
    
    return pipeline

def parse_references(pipeline, current_step, data, environment):
    """Parse the references contained in data to other parts of the pipeline."""
    
    return environment.from_string(data).render(
        inputs=current_step["inputs"],
        outputs=current_step["outputs"],
        commands=current_step.get("commands", ""),
        **pipeline["steps_dictionary"])
