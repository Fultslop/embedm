# Embedm backlog

## Planned

* Integration tests
* Error handling pass
* Discuss IoC
* Orchestration add InputMode.DIRECTORY, InputMode.STDIN
* Setup regression testing
* Add progress indicator

## To do

* Review
  * Fix duplicate source in child lookup (data loss bug)
  * Make transformer failures loud (raise on programming errors)
  * Standardise path handling on pathlib
  * Add plugin load error handling
  * Write 3-4 integration tests for the happy path
  * Stop mutating directives in-place
  * Add error channel to compilation result
