apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{name}}-deployment
  labels:
    app: {{name}}
  namespace: {{namespace}}
spec:
  replicas: {{replicas}}
  selector:
    matchLabels:
      app: {{name}}
  template:
    metadata:
      labels:
        app: {{name}}
    spec:
      containers:
      - name: {{image.name}}
        image: {{image.url}}
        {% if image.ports %}ports:
        {% for port in image.ports %}- containerPort: {{port.containerPort}}
          name: {{port.name}}
        {% endfor %}{% endif %}resources:
          requests:
            cpu: 100m
          limits:
            cpu: 200m
{% if image.ports|selectattr("public") | list | length %}---

apiVersion: v1
kind: Service
metadata:
  name: {{name}}-service-lb
  namespace: {{namespace}}
spec:
  type: LoadBalancer
  selector:
    app: {{name}}
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
  name: {{name}}-service-ip
  namespace: {{namespace}}
spec:
  selector:
    app: {{name}}
  ports:
  {% for port in image.ports %}{% if not port.public %}- name: {{port.name}}
    protocol: TCP
    port: {{port.externalPort}}
    targetPort: {{port.containerPort}}
  {% endif %}{% endfor %}{% endif %}
{% if autoscaler %}---

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{name}}-hpa
  namespace: {{namespace}}
spec:
 scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{name}}-deployment
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
