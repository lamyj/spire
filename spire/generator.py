try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from . import ninja

def render_ninja(pipeline, environment):
    """Render the Ninja file (rules, builds, and references)."""
    
    fd = StringIO()
    writer = ninja.Writer(fd)
    
    for step in pipeline.get("steps", []):
        if step.get("phony"):
            # Phony build steps have no rule
            writer.build(step["targets"], "phony", step["prerequisites"])
        else: 
            writer.rule(step["id"], " ; ".join(step["recipe"]))
            writer.build(step["targets"], step["id"], step["prerequisites"])

    data = fd.getvalue()
    writer.close()
    
    return data
