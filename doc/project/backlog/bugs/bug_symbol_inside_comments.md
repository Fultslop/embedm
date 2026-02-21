BUG: Symbols inside comments are parsed
=======================================
Draft  
Created: 20/02/2026  
Closed:  

## Description

A `symbol` in a comment block should be ignored by the FilePlugin. The file plugin currently does not ignore this symbol. 

## Replication

Use Embedm to compile the input file below. This does not match the expected outcome.

**Input:**

Markdown file (test.md):
```yaml embedm
type: file
source: Hello.cs
symbol: doSomething()
```

Source file (Hello.cs):
```csharp
namespace foo {
    class Bar {
        /*
          // first doSomething symbol
          // this one should be ignored
          public void doSomething() 
          { 
             // first
          }
        */

        // second doSomething symbol
        // this one should be used
          public void doSomething() 
          { 
             // second
          }
    }
}
```

**Output**:

````markdown
```cs
    public void doSomething() 
    { 
        // first
    }
```
````

**Expected**:

````markdown
```cs
    public void doSomething() 
    { 
        // second
    }
```
````
