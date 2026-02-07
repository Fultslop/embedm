"""Data models for embedm validation and processing pipeline."""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
import re


@dataclass
class Limits:
    """Configuration for processing limits."""
    max_file_size: int = 1_048_576      # 1MB in bytes
    max_recursion: int = 8
    max_embeds_per_file: int = 100
    max_output_size: int = 10_485_760   # 10MB in bytes
    max_embed_text: int = 2_048         # 2KB in bytes

    @staticmethod
    def parse_size(size_str: str) -> int:
        """
        Parse size string like '1MB', '2KB', '1024' into bytes.

        Examples:
            '1024' -> 1024
            '1KB' or '1K' -> 1024
            '1MB' or '1M' -> 1048576
        """
        size_str = str(size_str).strip().upper()

        # Match number and optional unit
        match = re.match(r'^(\d+(?:\.\d+)?)\s*([KMG]B?)?$', size_str)
        if not match:
            raise ValueError(f"Invalid size format: {size_str}")

        number = float(match.group(1))
        unit = match.group(2) or ''

        # Convert to bytes
        multipliers = {
            '': 1,
            'K': 1024,
            'KB': 1024,
            'M': 1024 * 1024,
            'MB': 1024 * 1024,
            'G': 1024 * 1024 * 1024,
            'GB': 1024 * 1024 * 1024,
        }

        return int(number * multipliers.get(unit, 1))

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format bytes into human-readable string."""
        if size_bytes == 0:
            return "unlimited"

        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f}TB"


@dataclass
class EmbedDirective:
    """Represents a discovered embed directive."""
    file_path: str              # File containing this embed
    line_number: int            # Where the embed appears
    embed_type: str             # 'file', 'toc', 'table_of_contents'
    properties: Dict            # Parsed YAML properties
    source_file: Optional[str]  # Resolved absolute path to source file (if applicable)

    def __hash__(self):
        """Make hashable for use in sets."""
        return hash((self.file_path, self.line_number, self.embed_type))


@dataclass
class ValidationError:
    """Represents a validation error or warning."""
    file_path: Optional[str]
    line_number: Optional[int]
    error_type: str             # 'missing_file', 'limit_exceeded', 'circular_dep', etc.
    message: str
    severity: str = 'error'     # 'error' or 'warning'

    def format(self) -> str:
        """Format error for display."""
        location = ""
        if self.file_path:
            location = self.file_path
            if self.line_number:
                location += f":{self.line_number}"

        symbol = "❌" if self.severity == 'error' else "⚠️ "

        if location:
            return f"  {location}\n    └─ {self.message}"
        return f"  {self.message}"


@dataclass
class ValidationResult:
    """Results from the validation phase."""
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    embeds_discovered: List[EmbedDirective] = field(default_factory=list)
    files_to_process: List[str] = field(default_factory=list)
    dependency_graph: Dict[str, Set[str]] = field(default_factory=dict)

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0

    def format_report(self, verbose: bool = False) -> str:
        """Format validation results for display."""
        lines = []

        # Summary header
        lines.append("\n🔍 Validation Phase")
        lines.append("━" * 60)
        lines.append(f"  Discovered: {len(self.files_to_process)} files, {len(self.embeds_discovered)} embeds")

        if self.dependency_graph:
            max_depth = self._calculate_max_depth()
            lines.append(f"  Dependencies: max depth {max_depth}")

        # Errors section
        if self.errors:
            lines.append(f"\n❌ Errors Found ({len(self.errors)})")
            lines.append("━" * 60)
            for error in self.errors:
                lines.append(error.format())

        # Warnings section
        if self.warnings:
            lines.append(f"\n⚠️  Warnings ({len(self.warnings)})")
            lines.append("━" * 60)
            for warning in self.warnings:
                lines.append(warning.format())

        # Success or failure message
        if self.has_errors():
            lines.append("\n❌ Validation failed. Fix errors and try again.")
        elif self.warnings:
            lines.append("\n⚠️  Validation passed with warnings.")
        else:
            lines.append("\n✅ All validations passed")

        return "\n".join(lines)

    def _calculate_max_depth(self) -> int:
        """Calculate maximum dependency depth in the graph."""
        if not self.dependency_graph:
            return 0

        def get_depth(node: str, visited: Set[str] = None) -> int:
            if visited is None:
                visited = set()

            if node in visited:
                return 0

            visited.add(node)
            deps = self.dependency_graph.get(node, set())

            if not deps:
                return 1

            return 1 + max(get_depth(dep, visited.copy()) for dep in deps)

        return max(get_depth(node) for node in self.dependency_graph.keys())


@dataclass
class ProcessingStats:
    """Statistics from the processing phase."""
    files_processed: int = 0
    embeds_resolved: int = 0
    total_output_size: int = 0
    duration_seconds: float = 0.0

    def format_summary(self) -> str:
        """Format processing summary."""
        size_str = Limits.format_size(self.total_output_size)
        return f"✅ Processing complete ({self.files_processed} files, {size_str}, {self.duration_seconds:.1f}s)"
