Claude code review check list.
==============================

Ask this after doing a unit of work.

Review your code. Ask yourself:

```yaml
review_metadata:
  agent_id: "claude-code-v1"
  schema_version: "1.2"

checklists:
  functional_and_technical_standards:
    - id: "SPEC_01"
      question: "Does the code pass the acceptance criteria in the specs?"
      validation_method: "cross_reference_requirements_doc"
    - id: "TEST_01"
      question: "Does the code pass the test suite, ruff, xenon, and radon?"
      validation_method: "execute_shell_test_and_lint_commands"
    - id: "DEF_01"
      question: "Does the public facing code check its pre-conditions and invariants?"
      validation_method: "ast_parsing_entry_points"
    - id: "DEBT_01"
      question: "If the code exposes any issues, did you raise them or add #TODO tags?"
      validation_method: "grep_todo_and_issue_tracker"

  clean_code_philosophy:
    - id: "CLEAN_01"
      question: "Is the code clean (self-documenting, low coupling, low complexity)?"
      validation_method: "cyclomatic_complexity_check"
    - id: "CLEAN_02"
      question: "Do comments explain the motivation (why) behind the code?"
      validation_method: "nlp_comment_analysis"
    - id: "CLEAN_03"
      question: "Does the code follow the single responsibility pattern?"
      validation_method: "class_method_responsibility_audit"
    - id: "CLEAN_04"
      question: "Does it pass DRY / YAGNI / open-closed sniff tests?"
      validation_method: "heuristic_eval"
    - id: "CLEAN_05"
      question: "Is there any dead code?"
      validation_method: "duplicate_code_detection_vulture"
    - id: "RES_01"
      question: "Does the code avoid magic values/strings? (Check xxx_resources.py)"
      validation_method: "grep_hardcoded_strings_vs_resource_files"

  architectural_integrity:
    - id: "ARCH_01"
      question: "Does the code fit the established architectural pattern(s)?"
      validation_method: "directory_structure_alignment_check"
    - id: "ARCH_02"
      question: "If a new pattern is introduced, is it noted/added to guides?"
      validation_method: "diff_new_patterns_vs_architecture_md"
    - id: "ARCH_03"
      question: "Was the code added in the right place?"
      validation_method: "module_dependency_graph_check"
    - id: "ARCH_04"
      question: "Does similar functionality exist in the code base?"
      validation_method: "semantic_code_search_index"
```