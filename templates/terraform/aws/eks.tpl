module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "20.33.1"
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
    metrics-server = {}
    eks-pod-identity-agent = {}
  }

  # cluster identifier
  cluster_name                   = "{{infra_element_name}}"

  # allows public access to the public endpoint of the cluster
  cluster_endpoint_public_access = {{publicAccess | lower}}
  # list of ip that can access the public endpoint
  cluster_endpoint_public_access_cidrs = [{{acceptedAddress}}]
  enable_cluster_creator_admin_permissions = true


  # id of the security group for the cluster
  {% if clusterSecurityGroup %}cluster_security_group_id =  aws_security_group.{{ clusterSecurityGroup }}_security_group.id{% endif %}
  
  # id of the vpc and subnets in which the cluster is deployed
  vpc_id                   = aws_vpc.{{deploymentNetwork}}.id
  subnet_ids               = [{% for subnet in deploymentSubnet %}aws_subnet.{{ subnet.name }}_subnet.id{% if not loop.last %}, {% endif %}{% endfor %}]

  # id of the security group for the nodes
 {% if nodeSecurityGroup %} 
  node_security_group_id   = aws_security_group.{{ nodeSecurityGroup }}_security_group.id 
  {% else %} {% if clusterSecurityGroup %}node_security_group_id   = aws_security_group.{{ clusterSecurityGroup }}_security_group.id {% endif %} {% endif %}
  

  # defaults for the node groups
  eks_managed_node_group_defaults = {
    ami_type       = "AL2_x86_64"
    instance_types = ["t2.micro"]
  }

  # node groups
  eks_managed_node_groups = {
    # list of node groups {% for key, value in context().items() %}{%if key.startswith('KubernetesNodeGroup') %}
    {{value.name}} = {
      min_size     = {{value.minSize}}
      max_size     = {{value.maxSize}}
      desired_size = {{value.desiredSize}}

      instance_types = ["{{value.type}}"]
      capacity_type  = "ON_DEMAND"
    }{% endif %}{% endfor %}
  }
}