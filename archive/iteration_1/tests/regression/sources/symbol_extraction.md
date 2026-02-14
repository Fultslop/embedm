# Symbol Extraction Tests

## Python: Extract a class

```yaml embedm
type: file
source: data/symbol_sample.py
symbol: Calculator
```

## Python: Extract a method via dot notation

```yaml embedm
type: file
source: data/symbol_sample.py
symbol: Calculator.add
```

## Python: Extract a standalone function

```yaml embedm
type: file
source: data/symbol_sample.py
symbol: standalone_helper
```

## JavaScript: Extract a function

```yaml embedm
type: file
source: data/symbol_sample.js
symbol: greet
```

## JavaScript: Extract a class

```yaml embedm
type: file
source: data/symbol_sample.js
symbol: Counter
```

## SQL: Extract a CTE

```yaml embedm
type: file
source: data/symbol_sample.sql
symbol: order_totals
```

## Python: Symbol with line numbers

```yaml embedm
type: file
source: data/symbol_sample.py
symbol: Calculator
line_numbers: text
```

## Python: Symbol with lines offset

```yaml embedm
type: file
source: data/symbol_sample.py
symbol: Calculator
lines: 1-3
```
