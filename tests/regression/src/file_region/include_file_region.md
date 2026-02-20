# Include a file region

Include full `c#` file

```yaml embedm
type: file
source: Hello.cs
```

Include `c#`, first region

```yaml embedm
type: file
source: Hello.cs
region: doSomething
```

Include `c#`, second region

```yaml embedm
type: file
source: Hello.cs
region: doSomethingElse
```

Include full `python` file

```yaml embedm
type: file
source: hello.py
```

Include `python` region

```yaml embedm
type: file
source: hello.py
region: print_hello
```

