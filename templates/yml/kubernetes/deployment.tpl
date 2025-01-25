apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{component.name}}-deployment
  labels:
    app: {{component.name}}
  namespace: {{namespace}}
spec:
  replicas: {{replicas}}
  selector:
    matchLabels:
      app: {{component.name}}
  template:
    metadata:
      labels:
        app: {{component.name}}
    spec:
      containers:
      - name: {{image.name}}
        image: {{image.url}}
        ports:
        {% for port in image.ports %}- containerPort: {{port.containerPort}}
          name: {{port.name}}
        {% endfor %}
{% if image.ports|selectattr("public") | list | length %}---

apiVersion: v1
kind: Service
metadata:
  name: {{component.name}}-service-lb
  namespace: {{namespace}}
spec:
  type: LoadBalancer
  selector:
    app: {{component.name}}
  ports:
  {% for port in image.ports %}{% if port.public %}- name: {{port.name}}
    protocol: TCP
    port: {{port.externalPort}}
    targetPort: {{port.containerPort}}
  {% endif %}{% endfor %}{% endif%}
{% if image.ports|selectattr("public","false") | list | length %}---

apiVersion: v1
kind: Service
metadata:
  name: {{component.name}}-service-ip
  namespace: {{namespace}}
spec:
  selector:
    app: {{component.name}}
  ports:
  {% for port in image.ports %}{% if not port.public %}- name: {{port.name}}
    protocol: TCP
    port: {{port.externalPort}}
    targetPort: {{port.containerPort}}
  {% endif %}{% endfor %}{% endif %}
{% if autoscaler %}---

apiVersion: autoscaling/v1
kind: HorizontalPodAutoscaler
metadata:
  name: {{component.name}}-hpa
  namespace: {{namespace}}
spec:
 scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{component.name}}-deployment
 minReplicas: {{autoscaler.minSize}}
 maxReplicas: {{autoscaler.maxSize}}
metrics:
- type: Resource
  resource:
    name: {{autoscaler.metric}}
    target:
      type: {{autoscaler.metricType}}
      averageUtilization: {{autoscaler.threshold}}
{% endif %}
