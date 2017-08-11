import yaml

try:
    unicode
except NameError:
    # 'unicode' is undefined: Python 3
    basestring = (str,bytes)
else:
    # 'unicode' exists: Python 2
    pass

def parse_pipeline(arguments, jinja_arguments, environment):
    """ Parse the Jinja+YAML pipeline description, normalize scalar items to 
        lists, and add a mapping from step ids to steps.
    """
    
    template = environment.get_template(arguments.pipeline)
    rendered = template.render(**jinja_arguments)
    pipeline = yaml.load(rendered)
    
    pipeline["steps_dictionary"] = {}
    for step in pipeline["steps"]:
        if step["id"] in pipeline["steps_dictionary"]:
            raise Exception("Duplicate step: {}".format(step["id"]))
        else:
            pipeline["steps_dictionary"][step["id"]] = step
    
    # Reconfigure the environment with the markup for second-stage templating.
    variable_string = (
        environment.variable_start_string, environment.variable_end_string)
    environment.variable_start_string = "$(("
    environment.variable_end_string = "))"
    
    # Parse references in prerequisites, targets and recipe, and normalize 
    # scalars to lists
    for step in pipeline.get("steps", []):
        for member in ["prerequisites", "targets", "recipe"]:
            transform = (
                yaml.load if member in ["prerequisites", "targets"]
                else lambda x: x)
            if member not in step:
                continue
            if isinstance(step[member], basestring):
                step[member] = transform(
                    parse_references(pipeline, step, step[member], environment))
                if isinstance(step[member], basestring):
                    step[member] = [step[member]]
            else:
                step[member] = [
                    transform(parse_references(pipeline, step, x, environment))
                    for x in step[member]]
    
    # Restore environment
    environment.variable_start_string = variable_string[0]
    environment.variable_end_string = variable_string[1]
    
    return pipeline

def parse_references(pipeline, current_step, data, environment):
    """Parse the references contained in data to other parts of the pipeline."""
    
    return environment.from_string(data).render(
        prerequisites=current_step["prerequisites"],
        targets=current_step["targets"],
        recipe=current_step.get("recipe", ""),
        **pipeline["steps_dictionary"])
