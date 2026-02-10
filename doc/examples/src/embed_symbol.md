# Include file

Example of symbol using a method name

```yaml embedm
type: file
title: Symbol inclusion
source: SymbolTest.cs
symbol: UniqueMethod
line_numbers: text
```

Example of symbol using a class name

```yaml embedm
type: file
title: Symbol inclusion
source: SymbolTest.cs
symbol: SymbolTest
line_numbers: text
```

Example of symbol using line offsets

```yaml embedm
type: file
title: Symbol inclusion
source: SymbolTest.cs
symbol: SymbolTest
line_numbers: text
lines: 3-7
```

Example of symbol using overloading by default params

```yaml embedm
type: file
title: Symbol inclusion
source: SymbolTest.cs
symbol: OverloadMethod1()
line_numbers: text
```

Example of symbol using overloading by params

```yaml embedm
type: file
title: Symbol inclusion
source: SymbolTest.cs
symbol: OverloadMethod1(string)
line_numbers: text
```

Example of symbol using overloading by explicit scoping

```yaml embedm
type: file
title: Symbol inclusion
source: SymbolTest.cs
symbol: SymbolTest2.OverloadMethod1()
line_numbers: text
```

Example of symbol that doesn't exist

```yaml embedm
type: file
title: Symbol inclusion
source: SymbolTest.cs
symbol: SomeMissingMethod()
line_numbers: text
```

Trying to outsmart the parser by asking a symbol embedded in comments

```yaml embedm
type: file
title: Symbol inclusion
source: SymbolTest.cs
symbol: OverloadMethod1(int number) 
line_numbers: text
```