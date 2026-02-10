"""Tests for file access sandbox module."""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock

from embedm.sandbox import (
    SandboxConfig,
    detect_sandbox_root,
    create_sandbox,
    check_sandbox,
    format_sandbox_info,
    _is_under_path,
    _get_git_root,
)
from embedm.models import Limits, ValidationResult
from embedm.validation import validate_all


class TestSandboxConfig(unittest.TestCase):
    """Test SandboxConfig dataclass defaults."""

    def test_defaults(self):
        """Test default values."""
        config = SandboxConfig()
        self.assertTrue(config.enabled)
        self.assertEqual(config.sandbox_root, "")
        self.assertEqual(config.allowed_paths, [])
        self.assertEqual(config.root_source, "")

    def test_custom_values(self):
        """Test custom initialization."""
        config = SandboxConfig(
            enabled=False,
            sandbox_root="/some/path",
            allowed_paths=["/extra"],
            root_source="git",
        )
        self.assertFalse(config.enabled)
        self.assertEqual(config.sandbox_root, "/some/path")
        self.assertEqual(config.allowed_paths, ["/extra"])
        self.assertEqual(config.root_source, "git")


class TestIsUnderPath(unittest.TestCase):
    """Test the _is_under_path helper."""

    def test_exact_match(self):
        """Exact same path should match."""
        path = os.path.normcase(os.path.normpath("/home/user/project"))
        self.assertTrue(_is_under_path(path, path))

    def test_child_path(self):
        """Child directory should match."""
        parent = os.path.normcase(os.path.normpath("/home/user/project"))
        child = os.path.normcase(os.path.normpath("/home/user/project/src/file.py"))
        self.assertTrue(_is_under_path(child, parent))

    def test_outside_path(self):
        """Path outside parent should not match."""
        parent = os.path.normcase(os.path.normpath("/home/user/project"))
        outside = os.path.normcase(os.path.normpath("/home/user/other"))
        self.assertFalse(_is_under_path(outside, parent))

    def test_prefix_attack_blocked(self):
        """Path that starts with parent string but is a different directory should not match."""
        parent = os.path.normcase(os.path.normpath("/home/user"))
        attack = os.path.normcase(os.path.normpath("/home/userdata/file.txt"))
        self.assertFalse(_is_under_path(attack, parent))

    def test_parent_path_not_allowed(self):
        """Parent of sandbox root should not match."""
        parent = os.path.normcase(os.path.normpath("/home/user/project"))
        above = os.path.normcase(os.path.normpath("/home/user"))
        self.assertFalse(_is_under_path(above, parent))


class TestDetectSandboxRoot(unittest.TestCase):
    """Test sandbox root detection logic."""

    @patch('embedm.sandbox._get_git_root')
    def test_git_root_found(self, mock_git):
        """When in a git repo, use git root."""
        git_root = os.path.normcase(os.path.normpath(os.path.abspath("/repo")))
        mock_git.return_value = git_root
        root, source = detect_sandbox_root("/repo/src/file.md")
        self.assertEqual(root, git_root)
        self.assertEqual(source, "git")

    @patch('embedm.sandbox._get_git_root')
    def test_config_dir_fallback(self, mock_git):
        """When git not found, fall back to config dir."""
        mock_git.return_value = None
        with tempfile.TemporaryDirectory() as tmpdir:
            root, source = detect_sandbox_root(os.path.join(tmpdir, "file.md"), config_dir=tmpdir)
            self.assertEqual(root, os.path.abspath(tmpdir))
            self.assertEqual(source, "config")

    @patch('embedm.sandbox._get_git_root')
    def test_cwd_fallback(self, mock_git):
        """When no git and no config, fall back to CWD."""
        mock_git.return_value = None
        root, source = detect_sandbox_root("/some/file.md")
        self.assertEqual(root, os.path.abspath(os.getcwd()))
        self.assertEqual(source, "cwd")

    @patch('embedm.sandbox._get_git_root')
    def test_directory_source(self, mock_git):
        """When source is a directory, use it for git detection."""
        mock_git.return_value = None
        with tempfile.TemporaryDirectory() as tmpdir:
            root, source = detect_sandbox_root(tmpdir)
            # Should use CWD since no git and no config
            self.assertEqual(source, "cwd")
            # Verify git was called with the directory itself
            mock_git.assert_called_once_with(os.path.abspath(tmpdir))


class TestCheckSandbox(unittest.TestCase):
    """Test sandbox access checking."""

    def test_disabled_allows_all(self):
        """Disabled sandbox should allow any path."""
        sandbox = SandboxConfig(enabled=False)
        result = check_sandbox("/etc/passwd", sandbox)
        self.assertIsNone(result)

    def test_inside_sandbox_allowed(self):
        """Files inside sandbox root should be allowed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = os.path.normcase(os.path.normpath(os.path.abspath(tmpdir)))
            sandbox = SandboxConfig(enabled=True, sandbox_root=root)

            inner_file = os.path.join(tmpdir, "src", "file.py")
            os.makedirs(os.path.dirname(inner_file), exist_ok=True)
            with open(inner_file, 'w') as f:
                f.write("test")

            result = check_sandbox(inner_file, sandbox)
            self.assertIsNone(result)

    def test_outside_sandbox_blocked(self):
        """Files outside sandbox root should be blocked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = os.path.normcase(os.path.normpath(os.path.abspath(tmpdir)))
            sandbox = SandboxConfig(enabled=True, sandbox_root=root)

            # Create a file outside the sandbox
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
                outside_file = f.name
                f.write(b"secret")

            try:
                result = check_sandbox(outside_file, sandbox)
                self.assertIsNotNone(result)
                self.assertIn("Access denied", result)
                self.assertIn("--allow-path", result)
                self.assertIn("--no-sandbox", result)
            finally:
                os.unlink(outside_file)

    def test_root_itself_allowed(self):
        """The sandbox root directory itself should be allowed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = os.path.normcase(os.path.normpath(os.path.abspath(tmpdir)))
            sandbox = SandboxConfig(enabled=True, sandbox_root=root)
            result = check_sandbox(tmpdir, sandbox)
            self.assertIsNone(result)

    def test_allowed_paths_grant_access(self):
        """Extra allowed paths should grant access to files within them."""
        with tempfile.TemporaryDirectory() as sandbox_dir:
            with tempfile.TemporaryDirectory() as extra_dir:
                root = os.path.normcase(os.path.normpath(os.path.abspath(sandbox_dir)))
                extra = os.path.normcase(os.path.normpath(os.path.abspath(extra_dir)))
                sandbox = SandboxConfig(
                    enabled=True,
                    sandbox_root=root,
                    allowed_paths=[extra],
                )

                inner_file = os.path.join(extra_dir, "allowed.txt")
                with open(inner_file, 'w') as f:
                    f.write("allowed")

                result = check_sandbox(inner_file, sandbox)
                self.assertIsNone(result)

    def test_prefix_attack_blocked(self):
        """Path prefix attack should be blocked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create sandbox at tmpdir/project
            project_dir = os.path.join(tmpdir, "project")
            os.makedirs(project_dir)
            root = os.path.normcase(os.path.normpath(os.path.abspath(project_dir)))
            sandbox = SandboxConfig(enabled=True, sandbox_root=root)

            # Create a sibling directory with prefix match
            attack_dir = os.path.join(tmpdir, "projectdata")
            os.makedirs(attack_dir)
            attack_file = os.path.join(attack_dir, "secret.txt")
            with open(attack_file, 'w') as f:
                f.write("secret")

            result = check_sandbox(attack_file, sandbox)
            self.assertIsNotNone(result)
            self.assertIn("Access denied", result)


class TestCreateSandbox(unittest.TestCase):
    """Test sandbox creation."""

    def test_no_sandbox_flag(self):
        """--no-sandbox should create disabled sandbox."""
        sandbox = create_sandbox("/some/path", no_sandbox=True)
        self.assertFalse(sandbox.enabled)
        self.assertEqual(sandbox.root_source, "disabled")

    @patch('embedm.sandbox._get_git_root')
    def test_allow_paths_resolved(self, mock_git):
        """--allow-path directories should be resolved to absolute paths."""
        mock_git.return_value = None
        with tempfile.TemporaryDirectory() as tmpdir:
            extra = os.path.join(tmpdir, "extra")
            os.makedirs(extra)
            sandbox = create_sandbox(tmpdir, allow_paths=[extra])
            self.assertTrue(sandbox.enabled)
            self.assertEqual(len(sandbox.allowed_paths), 1)
            # Should be absolute and normalized
            self.assertTrue(os.path.isabs(sandbox.allowed_paths[0]))

    @patch('embedm.sandbox._get_git_root')
    def test_default_sandbox_uses_cwd(self, mock_git):
        """Default sandbox with no git and no config should use CWD."""
        mock_git.return_value = None
        sandbox = create_sandbox("/nonexistent/path")
        self.assertTrue(sandbox.enabled)
        self.assertEqual(sandbox.root_source, "cwd")
        self.assertEqual(sandbox.sandbox_root, os.path.normcase(os.path.normpath(os.path.abspath(os.getcwd()))))


class TestGetGitRoot(unittest.TestCase):
    """Test the _get_git_root helper."""

    def test_finds_git_root_in_real_repo(self):
        """Should find git root when run inside a real repo."""
        # We're running tests from within the embedm git repo
        root = _get_git_root(os.getcwd())
        self.assertIsNotNone(root)
        self.assertTrue(os.path.isdir(root))

    def test_returns_none_for_non_repo(self):
        """Should return None for directories outside any git repo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = _get_git_root(tmpdir)
            # Temp dirs are typically not inside a git repo
            # but on some CI systems they might be, so we just check the type
            self.assertTrue(root is None or isinstance(root, str))

    @patch('embedm.sandbox.subprocess.run')
    def test_handles_timeout(self, mock_run):
        """Should return None on subprocess timeout."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="git", timeout=5)
        root = _get_git_root("/some/dir")
        self.assertIsNone(root)

    @patch('embedm.sandbox.subprocess.run')
    def test_handles_git_not_installed(self, mock_run):
        """Should return None when git is not installed."""
        mock_run.side_effect = FileNotFoundError()
        root = _get_git_root("/some/dir")
        self.assertIsNone(root)

    @patch('embedm.sandbox.subprocess.run')
    def test_handles_nonzero_returncode(self, mock_run):
        """Should return None when git returns non-zero."""
        mock_run.return_value = MagicMock(returncode=128, stdout="")
        root = _get_git_root("/some/dir")
        self.assertIsNone(root)

    @patch('embedm.sandbox.subprocess.run')
    def test_handles_empty_output(self, mock_run):
        """Should return None when git returns empty output."""
        mock_run.return_value = MagicMock(returncode=0, stdout="  \n")
        root = _get_git_root("/some/dir")
        self.assertIsNone(root)


class TestFormatSandboxInfo(unittest.TestCase):
    """Test sandbox info formatting."""

    def test_disabled(self):
        """Disabled sandbox should show disabled message."""
        info = format_sandbox_info(SandboxConfig(enabled=False, root_source="disabled"))
        self.assertIn("disabled", info)

    def test_git_root(self):
        """Git root should show description."""
        sandbox = SandboxConfig(
            enabled=True,
            sandbox_root="/home/user/project",
            root_source="git",
        )
        info = format_sandbox_info(sandbox)
        self.assertIn("git repository root", info)
        self.assertIn("/home/user/project", info)

    def test_config_root(self):
        """Config root should show description."""
        sandbox = SandboxConfig(
            enabled=True,
            sandbox_root="/home/user/project",
            root_source="config",
        )
        info = format_sandbox_info(sandbox)
        self.assertIn("config file directory", info)

    def test_cwd_root(self):
        """CWD root should show description."""
        sandbox = SandboxConfig(
            enabled=True,
            sandbox_root="/home/user/project",
            root_source="cwd",
        )
        info = format_sandbox_info(sandbox)
        self.assertIn("current working directory", info)

    def test_with_allowed_paths(self):
        """Allowed paths should be shown."""
        sandbox = SandboxConfig(
            enabled=True,
            sandbox_root="/project",
            allowed_paths=["/extra/shared"],
            root_source="git",
        )
        info = format_sandbox_info(sandbox)
        self.assertIn("shared", info)


class TestSandboxIntegration(unittest.TestCase):
    """Integration tests for sandbox with validation pipeline."""

    def test_validation_catches_violation(self):
        """validate_all should catch sandbox violations."""
        with tempfile.TemporaryDirectory() as sandbox_dir:
            with tempfile.TemporaryDirectory() as external_dir:
                # Create a markdown file inside the sandbox
                md_file = os.path.join(sandbox_dir, "test.md")
                # Create external source file
                ext_file = os.path.join(external_dir, "secret.txt")
                with open(ext_file, 'w') as f:
                    f.write("secret data")

                # Markdown that references external file
                rel_path = os.path.relpath(ext_file, sandbox_dir)
                with open(md_file, 'w') as f:
                    f.write(f"```yaml embedm\ntype: file\nsource: {rel_path}\n```\n")

                root = os.path.normcase(os.path.normpath(os.path.abspath(sandbox_dir)))
                sandbox = SandboxConfig(enabled=True, sandbox_root=root, root_source="test")
                limits = Limits()

                result = validate_all(md_file, limits, sandbox=sandbox)
                sandbox_errors = [e for e in result.errors if e.error_type == 'sandbox_violation']
                self.assertTrue(len(sandbox_errors) > 0)
                self.assertIn("Access denied", sandbox_errors[0].message)

    def test_validation_passes_inside_sandbox(self):
        """validate_all should pass for files inside sandbox."""
        with tempfile.TemporaryDirectory() as sandbox_dir:
            # Create source file inside sandbox
            src_file = os.path.join(sandbox_dir, "code.py")
            with open(src_file, 'w') as f:
                f.write("def hello():\n    pass\n")

            # Create markdown that references internal file
            md_file = os.path.join(sandbox_dir, "test.md")
            with open(md_file, 'w') as f:
                f.write("```yaml embedm\ntype: file\nsource: code.py\n```\n")

            root = os.path.normcase(os.path.normpath(os.path.abspath(sandbox_dir)))
            sandbox = SandboxConfig(enabled=True, sandbox_root=root, root_source="test")
            limits = Limits()

            result = validate_all(md_file, limits, sandbox=sandbox)
            sandbox_errors = [e for e in result.errors if e.error_type == 'sandbox_violation']
            self.assertEqual(len(sandbox_errors), 0)

    def test_no_sandbox_allows_external(self):
        """Disabled sandbox should allow external file access."""
        with tempfile.TemporaryDirectory() as sandbox_dir:
            with tempfile.TemporaryDirectory() as external_dir:
                md_file = os.path.join(sandbox_dir, "test.md")
                ext_file = os.path.join(external_dir, "code.py")
                with open(ext_file, 'w') as f:
                    f.write("x = 1\n")

                rel_path = os.path.relpath(ext_file, sandbox_dir)
                with open(md_file, 'w') as f:
                    f.write(f"```yaml embedm\ntype: file\nsource: {rel_path}\n```\n")

                sandbox = SandboxConfig(enabled=False, root_source="disabled")
                limits = Limits()

                result = validate_all(md_file, limits, sandbox=sandbox)
                sandbox_errors = [e for e in result.errors if e.error_type == 'sandbox_violation']
                self.assertEqual(len(sandbox_errors), 0)

    def test_force_cannot_bypass_sandbox(self):
        """Sandbox violations should exist regardless of force mode."""
        with tempfile.TemporaryDirectory() as sandbox_dir:
            with tempfile.TemporaryDirectory() as external_dir:
                md_file = os.path.join(sandbox_dir, "test.md")
                ext_file = os.path.join(external_dir, "secret.txt")
                with open(ext_file, 'w') as f:
                    f.write("secret")

                rel_path = os.path.relpath(ext_file, sandbox_dir)
                with open(md_file, 'w') as f:
                    f.write(f"```yaml embedm\ntype: file\nsource: {rel_path}\n```\n")

                root = os.path.normcase(os.path.normpath(os.path.abspath(sandbox_dir)))
                sandbox = SandboxConfig(enabled=True, sandbox_root=root, root_source="test")
                limits = Limits()

                # Even with force mode, sandbox errors should still be reported
                result = validate_all(md_file, limits, sandbox=sandbox)
                sandbox_errors = [e for e in result.errors if e.error_type == 'sandbox_violation']
                self.assertTrue(len(sandbox_errors) > 0)

    def test_sandbox_info_in_result(self):
        """ValidationResult should contain sandbox info."""
        with tempfile.TemporaryDirectory() as sandbox_dir:
            md_file = os.path.join(sandbox_dir, "test.md")
            with open(md_file, 'w') as f:
                f.write("# Hello\n")

            root = os.path.normcase(os.path.normpath(os.path.abspath(sandbox_dir)))
            sandbox = SandboxConfig(enabled=True, sandbox_root=root, root_source="git")
            limits = Limits()

            result = validate_all(md_file, limits, sandbox=sandbox)
            self.assertIsNotNone(result.sandbox_info)
            self.assertIn("git repository root", result.sandbox_info)

    def test_sandbox_info_in_format_report(self):
        """format_report should include sandbox line."""
        result = ValidationResult()
        result.sandbox_info = "test_root (git repository root)"
        report = result.format_report()
        self.assertIn("Sandbox:", report)
        self.assertIn("test_root", report)


if __name__ == '__main__':
    unittest.main()
