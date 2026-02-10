namespace test
{
    class SymbolTest
    {
        public enum EnumSymbol
        {
            Method = 1,
            Class = 2,
            Struct = 3,
            Enum = 4
        }

        public struct InnerStruct
        {
            public int x;
            public int y;
        }
        
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

    private interface ISomeInterface 
    {
        void DoThings();
    }

}