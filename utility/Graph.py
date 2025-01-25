# Copyright 2023 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#-------------------------------------------------------------------------

class Graph:
    # Contructor (given graph is optional)
    def __init__(self, givengraph=None, f=print):
        if givengraph is None:
            self.nodes = {}
        else:
            self.nodes = givengraph
        self.visited = []
        self.nodefunc = f
    # Add node (adds a node with no dependencies)
    def add_node(self, node):
        self.nodes[node] = []
    # Add edge (adds a dependency to a node, if the node does not exist adds the node first)
    def add_edge(self, fromnode, tonode):
        if not fromnode in self.nodes:
            self.add_node(fromnode)
        if not tonode in self.nodes:
            self.add_node(tonode)
        self.nodes[fromnode].append(tonode)
    # Method to visit graph or node
    def visit(self, node=None):
        if node is None:
            if self.nodes:  # if the graph is not empty
                for nodekey in self.nodes.keys():
                    self.visit(nodekey)
            self.visited = []
        else:
            if self.nodes[node]:  # if the current node has dependencies
                for dependency in self.nodes[node]:
                    self.visit(dependency)
            if not node in self.visited:
                self.nodefunc(node)
                self.visited.append(node)
    # Add a function to be executed for each node visited
    def set_function(self, f=print):
        self.nodefunc = f
