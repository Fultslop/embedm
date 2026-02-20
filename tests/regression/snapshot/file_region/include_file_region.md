# Include a file region

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
Include `c#`, first region

```cs
    public void doSomething() 
    {
        // ...
    }
```
Include `c#`, second region

```cs
    public void doSomethingElse() 
    {
        // ...
    }
```
Include full `python` file

```py

def print_hello_world():
    print('hello world')

# md.start: print_hello
def print_hello():
    print('hello')
# md.end: print_hello

print_hello()
```
Include `python` region

```py
def print_hello():
    print('hello')
```
