# Include symbol from a file

Include full `c#` file

```yaml embedm
type: file
source: Hello.cs
```

Include `c#`, MyEnum

```yaml embedm
type: file
source: Hello.cs
symbol: "MyEnum"
```

Include `c#`, Example.MyEnum

```yaml embedm
type: file
source: Hello.cs
symbol: "Example.MyEnum"
```

Include `c#`, Example class

```yaml embedm
type: file
source: Hello.cs
symbol: "Example"
```

Include `c#`, doSomething

```yaml embedm
type: file
source: Hello.cs
symbol: "Example.doSomething()"
```

Include `c#`, doSomethingElse

```yaml embedm
type: file
source: Hello.cs
symbol: "doSomethingElse()"
```

Include `c#`, doSomething overloaded

```yaml embedm
type: file
source: Hello.cs
symbol: "doSomething(string)"
```

Include `c#`, doSomething extra overloaded

```yaml embedm
type: file
source: Hello.cs
symbol: "doSomething(string, int)"
```

Include `c#`, doSomething from another class

```yaml embedm
type: file
source: Hello.cs
symbol: "AnotherExample.doSomething()"
```

Include `c#`, doSomething from the inner class

```yaml embedm
type: file
source: Hello.cs
symbol: "Example.Example.doSomething()"
```

Include `c#`, inner class

```yaml embedm
type: file
source: Hello.cs
symbol: "Example.Example"
```