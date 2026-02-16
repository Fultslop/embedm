# Embedm backlog

## Planned

* Orchestration add InputMode.DIRECTORY, InputMode.STDIN
* Setup regression testing
* ToC plugin
* Table plugin with sql-ish syntax
* File properties
* --silent --yes-to-all --dry-run --verify
* Enabled plugins
* Add progress indicator

## To do

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
