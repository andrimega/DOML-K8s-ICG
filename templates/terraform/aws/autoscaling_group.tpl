resource "aws_launch_template" "{{infra_element_name}}" {
  name_prefix   = "{{name}}_"
  {%- for key, value in context().items() %}{% if not callable(value)%}{%if key.lower().startswith('virtualmachine') %}
{% for image_el in extra_parameters["vmImages"] %}{%- if image_el["infra_element_name"] == value.generatedFrom %}  image_id= "{{ image_el.image_name }}"{%- endif %}{% endfor %}
  instance_type = "{% if 'sizeDescription' in value.keys() %}{{ sizeDescription }}{% elif 'vm_flavor' in context().keys() %}{{ vm_flavor }}{% else %}{{ instance_type }}{% endif %}"
  {%- endif %}{% endif %}{% endfor %}
{% for key, value in context().items() %}{% if not callable(value)%}{% if key.startswith('NetworkInterface') %}{% if value.associated is defined %}{% if value.associated is string %}  vpc_security_group_ids = [ aws_security_group.{{ value.associated }}_security_group.id ] {% else %}  vpc_security_group_ids = [ aws_security_group.{{ value.associated[0].name }}_security_group.id ] {% endif %}{% endif %}{% endif %}{% endif %}{% endfor %}
}

resource "aws_autoscaling_group" "{{infra_element_name}}" {
  desired_capacity    = {{min}}
  max_size            = {{max}}
  min_size            = {{min}}
{%- for key, value in context().items() %}{% if not callable(value)%}{%- if key.startswith('NetworkInterface') %}
  vpc_zone_identifier = [aws_subnet.{{ value.belongsTo ~ "_subnet"}}.id]
{%- endif %}{% endif %}{%- endfor %}
  launch_template {
    id      = aws_launch_template.{{infra_element_name}}.id
    version = "$Latest"
  }
}