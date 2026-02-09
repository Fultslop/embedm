"""Tests for processing phases."""

import os
import pytest
from embedm.phases import ProcessingPhase, PhaseProcessor
from embedm.resolver import ProcessingContext
from embedm.models import Limits


class TestProcessingPhaseEnum:
    """Test ProcessingPhase enumeration."""

    def test_phase_values(self):
        """Test phase enum values."""
        assert ProcessingPhase.EMBED.value == "embed"
        assert ProcessingPhase.POST_PROCESS.value == "post"

    def test_phase_order(self):
        """Test phases are in correct order."""
        phases = list(ProcessingPhase)
        assert phases[0] == ProcessingPhase.EMBED
        assert phases[1] == ProcessingPhase.POST_PROCESS

    def test_phase_count(self):
        """Test number of phases."""
        phases = list(ProcessingPhase)
        assert len(phases) == 2

    def test_display_names(self):
        """Test phase display names."""
        assert ProcessingPhase.EMBED.display_name == "Embed Resolution"
        assert ProcessingPhase.POST_PROCESS.display_name == "Post-Processing"


class TestPhaseProcessor:
    """Test PhaseProcessor functionality."""

    def test_processor_initialization_default_context(self):
        """Test processor initializes with default context."""
        processor = PhaseProcessor()
        assert processor.context is not None
        assert isinstance(processor.context, ProcessingContext)

    def test_processor_initialization_custom_context(self):
        """Test processor initializes with custom context."""
        custom_limits = Limits(max_recursion=5)
        context = ProcessingContext(limits=custom_limits)
        processor = PhaseProcessor(context=context)

        assert processor.context is context
        assert processor.context.limits.max_recursion == 5

    def test_handler_registration(self):
        """Test all phases have handlers registered."""
        processor = PhaseProcessor()

        # Check all phases have handlers
        for phase in ProcessingPhase:
            assert phase in processor._phase_handlers
            assert callable(processor._phase_handlers[phase])

    def test_handler_count_matches_phases(self):
        """Test number of handlers matches number of phases."""
        processor = PhaseProcessor()
        assert len(processor._phase_handlers) == len(list(ProcessingPhase))


class TestPhaseExecution:
    """Test phase execution and integration."""

    def test_process_simple_markdown(self, tmp_path):
        """Test processing simple markdown without embeds."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test\n\nSimple content.")

        processor = PhaseProcessor()
        result = processor.process_all_phases(str(test_file))

        assert result is not None
        assert "# Test" in result
        assert "Simple content" in result

    def test_process_with_file_embed(self, tmp_path):
        """Test processing with file embed."""
        # Create source file
        source_file = tmp_path / "source.py"
        source_file.write_text("def hello():\n    print('Hello')")

        # Create markdown with embed
        test_file = tmp_path / "test.md"
        test_file.write_text(
            "# Test\n\n"
            "```yaml\n"
            "type: embed.file\n"
            f"source: {source_file.name}\n"
            "```\n"
        )

        processor = PhaseProcessor()
        result = processor.process_all_phases(str(test_file))

        assert "def hello():" in result
        assert "print('Hello')" in result

    def test_process_with_toc(self, tmp_path):
        """Test processing with TOC generation."""
        test_file = tmp_path / "test.md"
        test_file.write_text(
            "# Main Title\n\n"
            "```yaml\n"
            "type: embed.toc\n"
            "```\n\n"
            "## Section 1\n\n"
            "Content 1\n\n"
            "## Section 2\n\n"
            "Content 2\n"
        )

        processor = PhaseProcessor()
        result = processor.process_all_phases(str(test_file))

        # Should have TOC generated - H1 is skipped, starts from H2
        assert "- [Main Title](#main-title)" not in result
        assert "- [Section 1](#section-1)" in result
        assert "- [Section 2](#section-2)" in result

    def test_process_with_comment_removal(self, tmp_path):
        """Test that comments are removed."""
        test_file = tmp_path / "test.md"
        test_file.write_text(
            "# Test\n\n"
            "Before comment.\n\n"
            "```yaml\n"
            "type: embed.comment\n"
            "```\n\n"
            "After comment.\n"
        )

        processor = PhaseProcessor()
        result = processor.process_all_phases(str(test_file))

        # Content before and after should remain
        assert "Before comment" in result
        assert "After comment" in result
        # Comment block should be removed (empty line remains)
        assert "type: embed.comment" not in result

    def test_phases_execute_in_order(self, tmp_path):
        """Test that EMBED phase runs before POST_PROCESS."""
        # Create a file with both embed and TOC
        # The TOC should include headings from embedded content

        source_file = tmp_path / "source.md"
        source_file.write_text("## Embedded Heading\n\nEmbedded content.")

        test_file = tmp_path / "test.md"
        test_file.write_text(
            "# Main\n\n"
            "```yaml\n"
            "type: embed.toc\n"
            "```\n\n"
            "```yaml\n"
            "type: embed.file\n"
            f"source: {source_file.name}\n"
            "```\n"
        )

        processor = PhaseProcessor()
        result = processor.process_all_phases(str(test_file))

        # TOC should include the embedded heading
        # (because EMBED phase runs first, then POST_PROCESS generates TOC)
        # H1 is skipped, starts from H2
        assert "- [Main](#main)" not in result
        assert "- [Embedded Heading](#embedded-heading)" in result


    def test_process_with_limits(self, tmp_path):
        """Test processing respects limits from context."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test\n\nContent.")

        # Create limits with low recursion
        limits = Limits(max_recursion=1)
        context = ProcessingContext(limits=limits)
        processor = PhaseProcessor(context=context)

        # Should process successfully
        result = processor.process_all_phases(str(test_file))
        assert "# Test" in result

    def test_process_nonexistent_file(self):
        """Test processing nonexistent file returns error message."""
        processor = PhaseProcessor()

        result = processor.process_all_phases("nonexistent.md")
        # Should return error message instead of raising exception
        assert "Embed Error" in result
        assert "File not found" in result

    def test_content_threading_between_phases(self, tmp_path):
        """Test that content passes correctly between phases."""
        # Create a simple file
        test_file = tmp_path / "test.md"
        test_file.write_text(
            "# Test\n\n"
            "```yaml\n"
            "type: embed.toc\n"
            "```\n\n"
            "## Section\n"
        )

        processor = PhaseProcessor()

        # Manually execute phases to verify content threading
        # Phase 1: EMBED
        content_after_embed = processor._execute_embed_phase(str(test_file), None)
        assert content_after_embed is not None
        assert "# Test" in content_after_embed

        # Phase 2: POST_PROCESS (receives content from phase 1)
        content_after_post = processor._execute_post_process_phase(
            str(test_file), content_after_embed
        )
        assert content_after_post is not None
        # TOC should be generated - H1 is skipped, starts from H2
        assert "- [Test](#test)" not in content_after_post
        assert "- [Section](#section)" in content_after_post


class TestPhaseProcessorBackwardCompatibility:
    """Test that PhaseProcessor maintains backward compatibility."""

    def test_same_output_as_direct_calls(self, tmp_path):
        """Test PhaseProcessor produces same output as direct function calls."""
        from embedm.resolver import resolve_content, resolve_table_of_contents

        test_file = tmp_path / "test.md"
        test_file.write_text(
            "# Title\n\n"
            "```yaml\n"
            "type: embed.toc\n"
            "```\n\n"
            "## Section\n"
        )

        # Direct calls (old way)
        content_old = resolve_content(str(test_file))
        final_old = resolve_table_of_contents(content_old, source_file_path=str(test_file))

        # PhaseProcessor (new way)
        processor = PhaseProcessor()
        final_new = processor.process_all_phases(str(test_file))

        # Should produce identical output
        assert final_old == final_new
