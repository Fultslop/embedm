namespace test
{
    class SymbolTest
    {
        public void UniqueMethod() 
        {
            // code goes here
        }
        
        public void OverloadMethod1() 
        {
            // code goes here    
        }

        // let's confuse the parser by adding a symbol
        // to the comments like this
        // OverloadMethod1(int number) 

        public void OverloadMethod1(string text) 
        {
            // code goes here    
        }
    }

    class SymbolTest2
    {
        public void OverloadMethod1() 
        {
            // this is from SymbolTest2
        }
    }
}