List of commands 
================

## Update snapshot

**Update regression snapshot**

`py .\src\embedm\ .\tests\regression\src\** -d .\tests\regression\snapshot\ -A`

**Update manual**

`py .\src\embedm\ .\doc\manual\src\** -d .\doc\manual\compiled\`

**Update agent_context**

`py .\src\embedm\ .\doc\project\agent_context.src.md -o .\doc\project\agent_context.md`

## Reinstall Embedm

`py -m pip install -e .`

## Ruff 

`ruff format ./src`
`ruff check --fix ./src`

## Xenon / Radon

`radon cc ./src/ -s -a`