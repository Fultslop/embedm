# Title

```embed 
table_of_contents 
```

This should be ignored: ` ```embed file:test.cs ``` `

## Csharp

But this should work:

### CS  Example 1

```embed
file:Hello.cs#doSomething
line_numbers: text
title: hello.cs
```
### CS Example 2

```embed
file:Hello.cs#doSomethingElse
line_numbers: html
```

## MD Recursion

### MD Example 1

recursive step

```embed
file:ref.md
```

### MD Example 2

```embed
file: loop.md
title: loop example
lang: txt
```

## Lorem ipsum

### Line number example

lorem-ipsum
```embed
file:.\lorem-ipsum.md#L4-L7
line_numbers:true
```

## CSV

```embed
file:test.csv
```