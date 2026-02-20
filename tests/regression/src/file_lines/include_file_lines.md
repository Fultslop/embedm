# Include line from a file

Include full `c#` file

```yaml embedm
type: file
source: Hello.cs
```

Include `c#`, single line

```yaml embedm
type: file
source: Hello.cs
lines: "4"
```

Include `c#`, lines starting from 11

```yaml embedm
type: file
source: Hello.cs
lines: "11.."
```

Include `c#`, lines until 7

```yaml embedm
type: file
source: Hello.cs
lines: "..7"
```

Include `c#`, lines 4 until 7

```yaml embedm
type: file
source: Hello.cs
lines: "4..7"
title: "Hello c#"
line_numbers_range: true
link: true
```

```yaml embedm
type: file
source: ../file_region/hello.py
lines: "5.."
title: "Hello python"
line_numbers_range: true
link: true
```
