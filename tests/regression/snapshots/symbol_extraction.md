# Symbol Extraction Tests

## Python: Extract a class

```py
class Calculator:
    """A simple calculator class."""

    def __init__(self, value=0):
        self.value = value

    def add(self, x):
        self.value += x
        return self

    def result(self):
        return self.value
```

## Python: Extract a method via dot notation

```py
def add(self, x):
    self.value += x
    return self
```

## Python: Extract a standalone function

```py
def standalone_helper(items):
    """A standalone function."""
    return [item * 2 for item in items]
```

## JavaScript: Extract a function

```js
function greet(name) {
    return "Hello, " + name + "!";
}
```

## JavaScript: Extract a class

```js
export class Counter {
    constructor(initial = 0) {
        this.count = initial;
    }

    increment() {
        this.count++;
    }

    getCount() {
        return this.count;
    }
}
```

## SQL: Extract a CTE

```sql
order_totals AS (
    SELECT user_id, SUM(amount) AS total
    FROM orders
    GROUP BY user_id
)
```

## Python: Symbol with line numbers

```py
 4 | class Calculator:
 5 |     """A simple calculator class."""
 6 | 
 7 |     def __init__(self, value=0):
 8 |         self.value = value
 9 | 
10 |     def add(self, x):
11 |         self.value += x
12 |         return self
13 | 
14 |     def result(self):
15 |         return self.value
```

## Python: Symbol with lines offset

```py
class Calculator:
    """A simple calculator class."""
```
