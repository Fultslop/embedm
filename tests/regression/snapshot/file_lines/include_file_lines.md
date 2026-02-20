# Include line from a file

Include full `c#` file

```cs
namespace test
{
    // md.start: doSomething
    public void doSomething() 
    {
        // ...
    }
    // md.end: doSomething

    // md.start: doSomethingElse
    public void doSomethingElse() 
    {
        // ...
    }
    // md.end: doSomethingElse
}
```
Include `c#`, single line

```cs
    public void doSomething()
```
Include `c#`, lines starting from 11

```cs
    public void doSomethingElse() 
    {
        // ...
    }
    // md.end: doSomethingElse
}
```
Include `c#`, lines until 7

```cs
namespace test
{
    // md.start: doSomething
    public void doSomething() 
    {
        // ...
    }
```
Include `c#`, lines 4 until 7

```cs
    public void doSomething() 
    {
        // ...
    }
```