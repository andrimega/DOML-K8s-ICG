from jinja2 import Environment

env = Environment()
path = "template_path"
path = "templates/terraform/aws/network.tpl"
with open(path) as template:
    env.parse(template.read())