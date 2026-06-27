from jinja2 import Environment, FileSystemLoader
from fastapi.responses import HTMLResponse

env = Environment(loader=FileSystemLoader("app/templates"))


def render(template_name: str, **context) -> HTMLResponse:
    template = env.get_template(template_name)
    return HTMLResponse(template.render(**context))
