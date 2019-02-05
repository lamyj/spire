import argparse
import os
import subprocess
import sys
import tempfile

def graph(tasks_path, dot_path, tasks_only, doit_arguments):
    temp_fd, temp_path = tempfile.mkstemp(suffix=".py")
    try:
        with open(tasks_path) as fd:
            os.write(temp_fd, fd.read().encode())
        os.write(
            temp_fd, 
            "\n"
            "import spire\n"
            "graph = spire.graph({})\n"
            "with open(\"{}\", \"w\") as fd:\n"
            "    fd.write(graph)\n".format(tasks_only, dot_path).encode())
        os.close(temp_fd)
        subprocess.check_call(["doit", "list", "-f", temp_path]+doit_arguments)
    finally:
        os.remove(temp_path)

if __name__ == "__main__":
    action = sys.argv[1]
    if action == "graph":
        parser = argparse.ArgumentParser(
            description="Generate a Graphviz representation of the task graph")
        parser.add_argument(
            "tasks_path", metavar="tasks.py", help="Path to the task graph")
        parser.add_argument(
            "dot_path", metavar="tasks.dot", help="Path to the task graph")
        parser.add_argument(
            "--tasks-only", action="store_true", help="Create nodes for tasks only")
        arguments, doit_arguments = parser.parse_known_args(sys.argv[2:])
        
        arguments.dot_path = os.path.abspath(arguments.dot_path)
        
        sys.exit(graph(doit_arguments=doit_arguments, **vars(arguments)))
        
