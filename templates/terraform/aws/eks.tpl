module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "19.15.1"
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    metrics-server = {
      most_recent = true
    }
  }

  # cluster identifier
  cluster_name                   = "{{infra_element_name}}"

  # allows public access to the public endpoint of the cluster
  cluster_endpoint_public_access = {{publicAccess | lower}}
  # list of ip that can access the public endpoint
  cluster_endpoint_public_access_cidrs = "{{acceptedAddress}}"

  # id of the security group for the cluster
  cluster_security_group_id = {% if clusterSecurityGroup %} aws_security_group.{{ clusterSecurityGroup }}.id {% else %} {{ [] }} {% endif %}
  # id of the vpc and subnets in which the cluster is deployed
  vpc_id                   = awc_vpc.{{deploymentNetwork}}.id

  # id of the security group for the nodes
  node_security_group_id   = {% if nodeSecurityGroup %} aws_security_group.{{ nodeSecurityGroup }}.id {% else %} {{ [] }} {% endif %}

  # defaults for the node groups
  eks_managed_node_group_defaults = {
    ami_type       = "AL2_x86_64"
    instance_types = ["t2.micro"]

    attach_cluster_primary_security_group = true
  }

  # node groups
  eks_managed_node_groups = {
    # list of node groups
    {% for key, value in context().items() %}{%if key.startswith('KubernetesNodeGroup') %}
    {{value.name}} = {
      min_size     = {{value.minSize}}
      max_size     = {{value.maxSize}}
      desired_size = {{value.desiredSize}}

     instance_types = [{{value.type}}]
     capacity_type  = "SPOT"
    }{% endif %}{% endfor %}
  }
}