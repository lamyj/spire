import argparse
import csv
import glob
import json
import logging
import os
import sys

import jinja2
import pkg_resources
import yaml

logger = logging.getLogger(__name__)

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
    main_parser.add_argument(
        "--modules-path", "-m", action="append", default=[],
        help="Additional search path for modules")
    main_parser.add_argument(
        "--verbosity", "-v", 
        choices=["warning", "info", "debug"], default="warning")
    
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
    
    verbosity = arguments.__dict__.pop("verbosity")
    logging.basicConfig(
        level=verbosity.upper(), 
        format="%(levelname)s - %(name)s: %(message)s")
    
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
        * can load templates from (in order of priority) user-defined search 
          paths, absolute paths, the directory of the pipeline description and 
          the directory of this script
        * contains a `glob` function mapping to `glob.glob`
        * has filters to transform to JSON and YAML
    """
    
    loader = jinja2.FileSystemLoader(arguments.modules_path + [
        "/",
        os.path.abspath(os.path.dirname(arguments.pipeline)),
        pkg_resources.resource_filename(
            pkg_resources.Requirement.parse("spire-pipeline"), 
            os.path.join(__name__, "modules"))
    ])
       
    environment = jinja2.Environment(loader=loader, keep_trailing_newline=True)
    environment.globals.update(
        basename=os.path.basename,
        build_directory=known_ninja_arguments.directory,
        dirname=os.path.dirname,
        glob=lambda pathname: sorted(
            x if os.path.isabs(pathname) 
            else os.path.relpath(x, known_ninja_arguments.directory) 
            for x in glob.glob(
                os.path.join(known_ninja_arguments.directory, pathname))),
        load_csv=load_csv, load_json=load_json, load_yaml=load_yaml,
        pipeline_directory=os.path.abspath(os.path.dirname(arguments.pipeline)),
    )
    environment.filters["json"] = lambda x: json.dumps(x)
    environment.filters["yaml"] = lambda x: yaml.dump(x, default_flow_style=False)
    
    return environment

def load_csv(path, *args, **kwargs):
    """ Load data from a CSV file. Extra arguments are passed to the CSV 
        reader (e.g. dialect).
    """

    if not os.path.isfile(path):
        raise Exception("No such file: \"{}\"".format(path))
    
    with open(path) as fd:
        reader = csv.DictReader(fd, *args, **kwargs)
        data = list(reader)
    
    return data

def load_json(path, *args, **kwargs):
    """ Load data from a JSON file. Extra arguments are passed to the JSON 
        loader.
    """
    
    if not os.path.isfile(path):
        raise Exception("No such file: \"{}\"".format(path))
    
    with open(path) as fd:
        data = json.load(fd)
    
    return data

def load_yaml(path, *args, **kwargs):
    """ Load data from a JSON file. Extra arguments are passed to the JSON 
        loader.
    """
    
    if not os.path.isfile(path):
        raise Exception("No such file: \"{}\"".format(path))
    
    with open(path) as fd:
        data = yaml.load(fd)
    
    return data
