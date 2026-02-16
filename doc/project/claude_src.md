# Development Guidelines

This document contains critical information about working with this codebase. Follow these guidelines precisely.

Read intended architecture can be found in ./doc/project/architecture.md
Read the functional analysis in ./doc/project/functional-analysis.md

Do not access ./archive unless explicitely told

## Platform

* Development takes place on a Windows machine. DO NOT USE LINUX COMMANDS.
* Python is installed but runs as 'py' not 'python'.

## Documentation

When starting a work, eg new feature or bug fix capture the intention in one line. When architecture, feature, implementation or best practises related decisions capture them in a document ./doc/project/devlog.md. Entries should be to the point and have the format "* DD/MM/YY [Task/Arch/Feat/Code/Standards]" followed by a short description and an empty line. Entries should be in order of most recent first.

## Agent Execution
For non-trivial tasks, briefly outline the intended approach before starting implementation. For small, well-defined tasks, proceed directly.

## Core Development Rules

1. Package Management
  - Leave package management to the user

2. Code Quality
   - Type hints required for all code
   - Public APIs must have docstrings
   - Functions must be focused and small
   - Follow existing patterns exactly
   - Line length: 120 chars maximum

3. Testing Requirements
   - Framework: `pytest`
   - Coverage: test edge cases and errors
   - New features require tests
   - Bug fixes require regression tests

4. Code Style
    - PEP 8 naming (snake_case for functions/variables)
    - Class names in PascalCase
    - Constants in UPPER_SNAKE_CASE
    - Document with docstrings
    - Use f-strings for formatting

5. git
    - NEVER use git commands. 

## Development Philosophy

- **Simplicity**: Write simple, straightforward code
- **Readability**: Make code easy to understand
- **Performance**: Consider performance without sacrificing readability
- **Maintainability**: Write code that's easy to update
- **Testability**: Ensure code is testable
- **Reusability**: Create reusable components and functions
- **Less Code = Less Debt**: Minimize code footprint, clean up dead code

## Coding Best Practices

- **Clear documentation**:Write minimal documentation if needed. NEVER give usage examples in the doc. 
- **Early Returns**: Use to avoid nested conditions
- **Descriptive Names**: Use clear variable/function names (prefix handlers with "handle")
- **Constants Over Functions**: Use constants where possible
- **DRY Code**: Don't repeat yourself
- **Functional Style**: Prefer functional, immutable approaches when not verbose
- **Minimal Changes**: Only modify code related to the task at hand
- **Function Ordering**: Define composing functions before their components
- **TODO Comments**: Mark issues in existing code with "TODO:" prefix
- **Simplicity**: Prioritize simplicity and readability over clever solutions
- **Build Iteratively** Start with minimal functionality and verify it works before adding complexity
- **Run Tests**: Test your code frequently with realistic inputs and validate outputs
- **Build Test Environments**: Create testing environments for components that are difficult to validate directly
- **Functional Code**: Use functional and stateless approaches where they improve clarity
- **Clean logic**: Keep core logic clean and push implementation details to the edges
- **File Organsiation**: Balance file organization with simplicity - use an appropriate number of files for the project scale
- **Prefer positives**: Prefer 'if condition' as opposed to 'if not condition' unless this complicates the code.

## Python Tools

## Code Formatting

1. Ruff
   - Check: `ruff check ./src`
   - Fix: `ruff check ./src --fix`

2. Type Checking
   - Tool: `mypy ./src`

## Error Resolution

1. CI Failures
   - Fix order:
     1. Formatting
     2. Type errors
     3. Linting
   - Type errors:
     - Get full line context
     - Check Optional types
     - Add type narrowing
     - Verify function signatures

2. Common Issues
   - Line length:
     - Break strings with parentheses
     - Multi-line function calls
     - Split imports
   - Types:
     - Add None checks
     - Narrow string types
     - Match existing patterns

3. Best Practices
   - Run formatters before type checks
   - Keep changes minimal
   - Follow existing patterns
   - Document public APIs
   - Test thoroughly