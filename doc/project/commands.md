List of commands to run
=======================

## Update snapshot

`py .\src\embedm\ .\tests\regression\** -d .\tests\regression_snapshot\`

## Reinstall Embedm

`py -m pip install -e .`

## Ruff 

`ruff format ./src`
`ruff check --fix ./src`

## Xenon / Radon

`radon cc ./src/ -s -a`