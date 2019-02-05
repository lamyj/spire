import argparse
import codecs
import glob
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree

import bs4
import markdown

configuration = {}

def main():
    parser = argparse.ArgumentParser(
        description="Build and run the code samples in the documentation")
    parser.add_argument("files", nargs="*", metavar="file")
    arguments = parser.parse_args()
    
    if not arguments.files:
        arguments.files = ["README.md"]
    
    for path in sorted(arguments.files):
        check_file(path)
    
def check_file(markdown_path):
    with codecs.open(markdown_path, encoding="utf-8") as fd:
        html = markdown.markdown(fd.read(), extensions=["fenced_code"])
    document = bs4.BeautifulSoup(html, "html.parser")

    languages = {"python": (check_python, ".py")}
    for language, (action, suffix) in languages.items():
        for code_sample in document.find_all("code", class_=language):
            fd, path = tempfile.mkstemp(suffix=suffix)
            os.write(fd, code_sample.text.encode())
            os.close(fd)
            try:
                action(path)
            except Exception:
                print(markdown_path)
                print(code_sample.text)
                raise
            os.unlink(path)

def check_python(path):
    environment = os.environ.copy()
    environment["PYTHONPATH"] = "{}:{}".format(
        os.path.dirname(__file__), os.environ.get("PYTHONPATH"))
    subprocess.check_call(["python3", path], env=environment)

if __name__ == "__main__":
    sys.exit(main())
