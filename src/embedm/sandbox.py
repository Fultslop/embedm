"""File access sandbox for restricting source file paths."""

import os
import subprocess
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class SandboxConfig:
    """Configuration for the file access sandbox."""
    enabled: bool = True
    sandbox_root: str = ""
    allowed_paths: List[str] = field(default_factory=list)
    root_source: str = ""  # How the root was determined (e.g., "git", "config", "cwd")


def detect_sandbox_root(source_path: str, config_dir: Optional[str] = None) -> Tuple[str, str]:
    """
    Detect the sandbox root directory.

    Tries in order:
    1. Git repository root (from source_path's directory)
    2. Config file directory (if provided)
    3. Current working directory

    Args:
        source_path: The file or directory being processed
        config_dir: Directory containing the config file (if any)

    Returns:
        Tuple of (root_path, source_label) where source_label describes how it was found
    """
    # Determine the starting directory for git detection
    if os.path.isdir(source_path):
        start_dir = os.path.abspath(source_path)
    else:
        start_dir = os.path.dirname(os.path.abspath(source_path))

    # Try git root
    git_root = _get_git_root(start_dir)
    if git_root:
        return (git_root, "git")

    # Try config directory
    if config_dir:
        abs_config_dir = os.path.abspath(config_dir)
        if os.path.isdir(abs_config_dir):
            return (abs_config_dir, "config")

    # Fall back to CWD
    return (os.path.abspath(os.getcwd()), "cwd")


def _get_git_root(start_dir: str) -> Optional[str]:
    """
    Get the git repository root from a starting directory.

    Args:
        start_dir: Directory to start searching from

    Returns:
        Absolute path to git root, or None if not in a git repo
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=start_dir,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            root = result.stdout.strip()
            if root:
                return os.path.normcase(os.path.normpath(os.path.abspath(root)))
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def create_sandbox(
    source_path: str,
    config_dir: Optional[str] = None,
    allow_paths: Optional[List[str]] = None,
    no_sandbox: bool = False,
) -> SandboxConfig:
    """
    Create a sandbox configuration.

    Args:
        source_path: The file or directory being processed
        config_dir: Directory containing the config file (if any)
        allow_paths: Additional paths to allow (from --allow-path)
        no_sandbox: If True, disable the sandbox entirely

    Returns:
        SandboxConfig with resolved paths
    """
    if no_sandbox:
        return SandboxConfig(enabled=False, root_source="disabled")

    root, source_label = detect_sandbox_root(source_path, config_dir)
    root = os.path.normcase(os.path.normpath(os.path.abspath(root)))

    # Resolve and normalize allowed paths
    resolved_allowed = []
    if allow_paths:
        for p in allow_paths:
            abs_p = os.path.normcase(os.path.normpath(os.path.abspath(p)))
            resolved_allowed.append(abs_p)

    return SandboxConfig(
        enabled=True,
        sandbox_root=root,
        allowed_paths=resolved_allowed,
        root_source=source_label,
    )


def check_sandbox(file_path: str, sandbox: SandboxConfig) -> Optional[str]:
    """
    Check if a file path is allowed by the sandbox.

    Args:
        file_path: Absolute path to the file to check
        sandbox: Sandbox configuration

    Returns:
        None if allowed, error message string if blocked
    """
    if not sandbox.enabled:
        return None

    # Resolve symlinks and normalize
    real_path = os.path.normcase(os.path.normpath(os.path.realpath(file_path)))

    # Check against sandbox root
    root = sandbox.sandbox_root
    if _is_under_path(real_path, root):
        return None

    # Check against allowed paths
    for allowed in sandbox.allowed_paths:
        if _is_under_path(real_path, allowed):
            return None

    # Blocked
    try:
        rel = os.path.relpath(real_path, root)
    except ValueError:
        rel = real_path

    return (
        f"Access denied: '{rel}' is outside the sandbox root "
        f"({os.path.basename(root)}{os.sep}). "
        f"Use --allow-path to grant access or --no-sandbox to disable."
    )


def _is_under_path(child: str, parent: str) -> bool:
    """
    Check if child path is under (or equal to) parent path.

    Handles the prefix attack: /home/user does not match /home/userdata
    by comparing with parent + os.sep.

    Args:
        child: Normalized, resolved child path
        parent: Normalized parent path

    Returns:
        True if child is under or equal to parent
    """
    # Exact match
    if child == parent:
        return True

    # Prefix check with separator to prevent /home/user matching /home/userdata
    parent_prefix = parent + os.sep
    return child.startswith(parent_prefix)


def format_sandbox_info(sandbox: SandboxConfig) -> str:
    """
    Format sandbox configuration for display in validation output.

    Args:
        sandbox: Sandbox configuration

    Returns:
        Human-readable string describing the sandbox state
    """
    if not sandbox.enabled:
        return "disabled (--no-sandbox)"

    source_labels = {
        "git": "git repository root",
        "config": "config file directory",
        "cwd": "current working directory",
    }
    label = source_labels.get(sandbox.root_source, sandbox.root_source)
    info = f"{sandbox.sandbox_root} ({label})"

    if sandbox.allowed_paths:
        extras = ", ".join(os.path.basename(p) for p in sandbox.allowed_paths)
        info += f" + {extras}"

    return info
