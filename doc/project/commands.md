List of commands 
================

## Update snapshot

`py .\src\embedm\ .\tests\regression\src\** -d .\tests\regression\snapshot\ -A`
`py .\src\embedm\ .\doc\manual\src\** -d .\doc\manual\compiled\`

## Reinstall Embedm

`py -m pip install -e .`

## Ruff 

`ruff format ./src`
`ruff check --fix ./src`

## Xenon / Radon

`radon cc ./src/ -s -a`