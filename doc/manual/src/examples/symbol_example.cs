namespace Widgets
{
    public enum Theme
    {
        Light,
        Dark,
        HighContrast
    }

    class Button
    {
        public void Render()
        {
            Console.WriteLine("<button>Click me</button>");
        }

        public void Render(string label)
        {
            Console.WriteLine($"<button>{label}</button>");
        }

        public void Render(string label, string style)
        {
            Console.WriteLine($"<button style=\"{style}\">{label}</button>");
        }
    }

    class Label
    {
        public void Render()
        {
            Console.WriteLine("<span>Label</span>");
        }
    }
}
