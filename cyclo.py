import ast
import os
import re

class FlowGraph:
    def __init__(self, name):
        self.name = name
        self.nodes = []
        self.edges = []

    def add_node(self, label):
        self.nodes.append(label)

    def add_edge(self, source, target):
        self.edges.append((source, target))

    def cyclomatic_complexity(self):
        return len(self.edges) - len(self.nodes) + 2 * (1)  # Assuming a single connected component

def generate_flow_graph(code):
    """Generates a control flow graph for Python code."""

    tree = ast.parse(code)
    graph = FlowGraph("Control Flow Graph")
    node_counter = 0

    def add_node_with_increment(label):
        nonlocal node_counter
        graph.add_node(f"{node_counter}: {label}")
        node_counter += 1
        return node_counter -1


    def traverse(node, parent_node_index=None):
        nonlocal node_counter
        current_node_index = None

        if isinstance(node, ast.FunctionDef):
            current_node_index = add_node_with_increment(f"Function: {node.name}")

        elif isinstance(node, ast.If):
            current_node_index = add_node_with_increment(f"If: {ast.unparse(node.test)}")


        elif isinstance(node, ast.For):
            current_node_index = add_node_with_increment(f"For: {ast.unparse(node.target)} in {ast.unparse(node.iter)}")


        elif isinstance(node, ast.While):
            current_node_index = add_node_with_increment(f"While: {ast.unparse(node.test)}")
            

        elif isinstance(node, ast.Try):
            current_node_index = add_node_with_increment("Try")


        elif isinstance(node, ast.ExceptHandler):
            current_node_index = add_node_with_increment(f"Except: {ast.unparse(node.type) if node.type else 'all'} ")


        elif isinstance(node, ast.Return) :
             current_node_index = add_node_with_increment(f"Return: {ast.unparse(node.value) if node.value else ''}")


        elif isinstance(node, ast.Expr):  # For standalone expressions
            current_node_index = add_node_with_increment(f"Expr: {ast.unparse(node.value)}")


        else:
            current_node_index = add_node_with_increment(f"{type(node).__name__}")  # Generic node


        if parent_node_index is not None and current_node_index is not None:
            graph.add_edge(parent_node_index, current_node_index)

        for child in ast.iter_child_nodes(node):
            traverse(child, current_node_index)

        # Add edges for control flow structures after children are traversed
        if isinstance(node, ast.If) and current_node_index is not None:
            
            # Traverse orelse block, create dummy node to connect or else block if there is no else block
            else_start_node = add_node_with_increment("Start Else")
            for n in node.orelse:
                traverse(n, current_node_index)  
            
            if len(node.orelse) == 0:
                 graph.add_edge(current_node_index, else_start_node)
            else:
                 graph.add_edge(current_node_index, node_counter -1 ) 
                 else_start_node = node_counter - 1
            # Connect end of if and else block to the next node 

            
        if isinstance(node, (ast.For, ast.While)) and current_node_index is not None:
            graph.add_edge(node_counter -1, current_node_index)


        if isinstance(node, ast.Try) and current_node_index is not None:
            for handler in node.handlers:
                traverse(handler, current_node_index)
            for n in node.finalbody:
                traverse(n, current_node_index)  # Connect finally block
            # for n in node.body:
            #     traverse(n, current_node_index)  


    traverse(tree)
    return graph


def analyze_repo(repo_path):
    results = {}
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        code = f.read()
                        graph = generate_flow_graph(code)
                        complexity = graph.cyclomatic_complexity()
                        results[file_path] = {
                            "complexity": complexity,
                            "graph": graph,  # Store the graph object
                        }
                    except Exception as e: # Handle SyntaxError and other exceptions during file processing
                        print(f"Error analyzing {file_path}: {e}")
                        results[file_path] = {
                            "complexity": "Error",
                            "graph": None,
                        }

    return results


# Example usage (replace with your repo path):
repo_path = "."  # Current directory
analysis_results = analyze_repo(repo_path)

for file_path, data in analysis_results.items():
    print(f"File: {file_path}")
    print(f"  Cyclomatic Complexity: {data['complexity']}")
    #Access the graph object if needed:
    # graph = data['graph']
    # print(graph.nodes)
    # print(graph.edges)


total_complexity = 0
for file_path, data in analysis_results.items():
     if isinstance(data['complexity'], int): # Check if it is an integer
            total_complexity += data['complexity']



print("\nSystem-Level Cyclomatic Complexity:", total_complexity)