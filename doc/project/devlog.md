# Dev Log

This document contains entries related to the work done or decisions on feature, architecture, implementation or code / design philosophy.

## Entries

* 15/02/26 [Task] Implement planner with directive validation, recursion control, and tests

* 15/02/26 [Arch] Plan-before-execute: validate all directives and sources before building the plan tree

* 15/02/26 [Feat] PlanNode DAG as immutable plan representation with per-node error isolation

* 15/02/26 [Task] Implement file cache with LRU eviction, path access control, and tests

* 15/02/26 [Arch] Lazy validation in file cache — skip filesystem checks for already-cached files

* 15/02/26 [Task] Implement directive parser with YAML block extraction and fragment decomposition

* 15/02/26 [Arch] Three-layer parsing pipeline: block detection, YAML parsing, fragment decomposition

* 15/02/26 [Feat] EmbedmContext as dependency injection container for config, file cache, and plugin registry

* 15/02/26 [Feat] Status-based error reporting with OK, WARNING, ERROR, FATAL levels