"""Discovery phase - find and parse all embeds without executing."""

import os
import re
from typing import List, Tuple

from .models import EmbedDirective
from .parsing import parse_yaml_embed_block


def discover_files(source_path: str) -> List[str]:
    """
    Discover all markdown files to process.

    Args:
        source_path: File or directory path

    Returns:
        List of absolute paths to markdown files
    """
    absolute_path = os.path.abspath(source_path)

    if os.path.isfile(absolute_path):
        if absolute_path.endswith('.md'):
            return [absolute_path]
        return []

    if os.path.isdir(absolute_path):
        files = []
        for filename in os.listdir(absolute_path):
            if filename.endswith('.md'):
                files.append(os.path.join(absolute_path, filename))
        return sorted(files)

    return []


def discover_embeds_in_file(file_path: str) -> List[EmbedDirective]:
    """
    Discover all embed directives in a single file without executing them.

    Args:
        file_path: Absolute path to markdown file

    Returns:
        List of discovered embed directives
    """
    if not os.path.exists(file_path):
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    embeds = []
    current_file_dir = os.path.dirname(file_path)

    # Find all YAML code blocks
    yaml_regex = re.compile(r'^```yaml\s*\n([\s\S]*?)```', re.MULTILINE)

    for match in yaml_regex.finditer(content):
        yaml_content = match.group(1)
        line_number = content[:match.start()].count('\n') + 1

        # Try to parse as embed block
        parsed = parse_yaml_embed_block(yaml_content)
        if not parsed:
            continue

        embed_type, properties = parsed

        # Resolve source file path if present
        source_file = None
        if 'source' in properties:
            source = properties['source']
            source_file = os.path.abspath(os.path.join(current_file_dir, source))

        embed = EmbedDirective(
            file_path=file_path,
            line_number=line_number,
            embed_type=embed_type,
            properties=properties,
            source_file=source_file
        )

        embeds.append(embed)

    return embeds


def discover_all_embeds(files: List[str]) -> List[EmbedDirective]:
    """
    Discover all embeds across multiple files.

    Args:
        files: List of file paths

    Returns:
        List of all discovered embeds
    """
    all_embeds = []

    for file_path in files:
        embeds = discover_embeds_in_file(file_path)
        all_embeds.extend(embeds)

    return all_embeds


def build_dependency_graph(embeds: List[EmbedDirective]) -> dict:
    """
    Build a dependency graph from discovered embeds.

    The graph maps each file to the set of files it depends on (embeds from).

    Args:
        embeds: List of discovered embeds

    Returns:
        Dict mapping file_path -> set of dependency file paths
    """
    graph = {}

    for embed in embeds:
        # Only file embeds create dependencies
        if embed.embed_type == 'file' and embed.source_file:
            if embed.file_path not in graph:
                graph[embed.file_path] = set()

            graph[embed.file_path].add(embed.source_file)

            # If the dependency is also a markdown file, it might have its own embeds
            if embed.source_file.endswith('.md'):
                if embed.source_file not in graph:
                    graph[embed.source_file] = set()

    return graph


def detect_cycles(graph: dict) -> List[List[str]]:
    """
    Detect circular dependencies in the dependency graph.

    Args:
        graph: Dependency graph from build_dependency_graph

    Returns:
        List of cycles, where each cycle is a list of file paths
    """
    cycles = []

    def dfs(node: str, path: List[str], visited: set):
        if node in path:
            # Found a cycle
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            cycles.append(cycle)
            return

        if node in visited:
            return

        visited.add(node)
        path.append(node)

        for neighbor in graph.get(node, set()):
            dfs(neighbor, path.copy(), visited)

    visited = set()
    for node in graph.keys():
        if node not in visited:
            dfs(node, [], visited)

    return cycles


def calculate_max_depth(graph: dict) -> int:
    """
    Calculate the maximum depth of the dependency graph.

    Args:
        graph: Dependency graph from build_dependency_graph

    Returns:
        Maximum depth of dependencies
    """
    if not graph:
        return 0

    def get_depth(node: str, visited: set = None) -> int:
        if visited is None:
            visited = set()

        if node in visited:
            # Circular dependency, return 0 to avoid infinite recursion
            return 0

        visited = visited.copy()
        visited.add(node)

        deps = graph.get(node, set())
        if not deps:
            return 1

        return 1 + max(get_depth(dep, visited) for dep in deps)

    return max(get_depth(node) for node in graph.keys())
