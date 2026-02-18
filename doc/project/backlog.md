# Embedm backlog

## Planned

* ToC plugin
* Setup regression testing
* Table plugin with sql-ish syntax
* File properties
* --silent --yes-to-all --dry-run --verify
* Enabled plugins
* Add progress indicator

## Done

* Discuss IoC
* Integration tests
* Review
  * Fix duplicate source in child lookup (data loss bug)
  * Make transformer failures loud (raise on programming errors)
  * Standardise path handling on pathlib
  * Add plugin load error handling
  * Write 3-4 integration tests for the happy path
  * Stop mutating directives in-place
  * Add error channel to compilation result
* Error handling pass, user interaction
  * add tests for regression testing
* Orchestration add InputMode.DIRECTORY, InputMode.STDIN