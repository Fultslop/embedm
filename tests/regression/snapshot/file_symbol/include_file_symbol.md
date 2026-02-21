# Include symbol from a file

Include full `c#` file

```cs
namespace test
{
    public enum MyEnum
    {
        // Outer MyEnum
        Value1 = 0,
        Value2 = 1
    }

    public class Example
    {
        public enum MyEnum
        {
            // Example.MyEnum
            InnerValue1 = 0,
            InnerValue2 = 1
        }

        /* this should be ignored as it's in a comment
            public void doSomething() 
            {
                // you found a comment
            }    
        */

        public class Example
        {
            public void doSomething() 
            {
                // inner Example of do something
            }    
        }

        public void doSomething() 
        {
            // base version
        }

        public void doSomething(string overloaded) 
        {
            // overloaded version
        }

        public void doSomething(string overloaded, int extra)
        {
            // extra overloaded version
        }

        public void doSomethingElse() 
        {
            // ...
        }
    }

    public class AnotherExample
    {
        public void doSomething() 
        {
            // base version in another example
        }
    }
}
```
Include `c#`, MyEnum

```cs
    public enum MyEnum
    {
        // Outer MyEnum
        Value1 = 0,
        Value2 = 1
    }
```
Include `c#`, Example.MyEnum

```cs
        public enum MyEnum
        {
            // Example.MyEnum
            InnerValue1 = 0,
            InnerValue2 = 1
        }
```
Include `c#`, Example class

```cs
    public class Example
    {
        public enum MyEnum
        {
            // Example.MyEnum
            InnerValue1 = 0,
            InnerValue2 = 1
        }

        /* this should be ignored as it's in a comment
            public void doSomething() 
            {
                // you found a comment
            }    
        */

        public class Example
        {
            public void doSomething() 
            {
                // inner Example of do something
            }    
        }

        public void doSomething() 
        {
            // base version
        }

        public void doSomething(string overloaded) 
        {
            // overloaded version
        }

        public void doSomething(string overloaded, int extra)
        {
            // extra overloaded version
        }

        public void doSomethingElse() 
        {
            // ...
        }
    }
```
Include `c#`, doSomething

```cs
        public void doSomething() 
        {
            // base version
        }
```
Include `c#`, doSomethingElse

```cs
        public void doSomethingElse() 
        {
            // ...
        }
```
Include `c#`, doSomething overloaded

```cs
        public void doSomething(string overloaded) 
        {
            // overloaded version
        }
```
Include `c#`, doSomething extra overloaded

```cs
        public void doSomething(string overloaded, int extra)
        {
            // extra overloaded version
        }
```
Include `c#`, doSomething from another class

```cs
        public void doSomething() 
        {
            // base version in another example
        }
```
Include `c#`, doSomething from the inner class

```cs
            public void doSomething() 
            {
                // inner Example of do something
            }
```
Include `c#`, inner class

```cs
        public class Example
        {
            public void doSomething() 
            {
                // inner Example of do something
            }    
        }
```