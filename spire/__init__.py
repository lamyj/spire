import argparse
import glob
import json
import os
import sys

import jinja2
import pkg_resources
import yaml

from .generator import render_ninja
from .parser import parse_pipeline
from .runner import run_ninja

def main():
    
    (
        arguments, jinja_arguments, 
        raw_ninja_arguments, known_ninja_arguments
    ) = parse_arguments()
    
    environment = get_jinja_environment(arguments, known_ninja_arguments)
    pipeline = parse_pipeline(arguments, jinja_arguments, environment)
    ninja_file = render_ninja(pipeline, environment)
    return run_ninja(ninja_file, raw_ninja_arguments)

def parse_arguments():
    """ Return the runner-specific, Jinja-specific and Ninja-specific (both raw
        and known) arguments parsed from the command line.
    """
    
    jinja_parser = argparse.ArgumentParser(
        description="Run Ninja from a pipeline description")
    jinja_parser.add_argument("pipeline", help="Path to pipeline description")
    jinja_parser.add_argument(
        "variables", nargs="*", 
        metavar="variable", help="Jinja variables (name=value)")
    
    main_parser = argparse.ArgumentParser(
        description="Run Ninja from a pipeline description",
        usage=jinja_parser.format_usage().strip()+" [-- ninja-option [ninja-option ...]]")
    main_parser.add_argument("pipeline", help="Path to pipeline description")
    main_parser.add_argument(
        "variables", nargs="*", 
        metavar="variable", help="Jinja variables (name=value)")
    
    if "--" in sys.argv:
        limit = sys.argv.index("--")
        arguments = main_parser.parse_args(sys.argv[1:limit])
        raw_ninja_arguments = sys.argv[1+limit:]
    else:
        arguments = main_parser.parse_args()
        raw_ninja_arguments = []
    
    try:
        jinja_arguments = {
            x.split("=", 1)[0]: x.split("=", 1)[1] 
            for x in arguments.variables}
    except Exception as e:
        main_parser.error(e)
    
    ninja_parser = argparse.ArgumentParser()
    ninja_parser.add_argument("--directory", "-C", default=os.getcwd())
    known_ninja_arguments, _ = ninja_parser.parse_known_args(raw_ninja_arguments)
    if known_ninja_arguments.directory:
        # Make sure it ends with a "/"
        known_ninja_arguments.directory = os.path.join(
            known_ninja_arguments.directory, "")
    
    return arguments, jinja_arguments, raw_ninja_arguments, known_ninja_arguments

def get_jinja_environment(arguments, known_ninja_arguments): 
    """ Return a Jinja environment which:
        * can load templates from absolute paths, from the directory of the 
          pipeline description and from the directory of this script
        * contains a `glob` function mapping to `glob.glob`
        * has filters to transform to JSON and YAML
    """
    
    loader = jinja2.FileSystemLoader([
        "/",
        os.path.abspath(os.path.dirname(arguments.pipeline)),
        pkg_resources.resource_filename(
            pkg_resources.Requirement.parse(__name__), 
            os.path.join(__name__, "modules"))
    ])
       
    environment = jinja2.Environment(loader=loader, keep_trailing_newline=True)
    environment.globals.update(
        glob=lambda x: sorted(
            x[len(known_ninja_arguments.directory):] for x in 
            glob.glob(os.path.join(known_ninja_arguments.directory, x)))
    )
    environment.filters["json"] = lambda x: json.dumps(x)
    environment.filters["yaml"] = lambda x: yaml.dump(x, default_flow_style=False)
    
    return environment
