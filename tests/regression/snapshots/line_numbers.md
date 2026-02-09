# Line Numbers Test

This tests file embedding with line numbers.

## Specific Function

```py
 1 | """Sample Python file for regression testing."""
 2 | 
 3 | 
 4 | def greet(name: str) -> str:
 5 |     """Greet someone by name.
 6 | 
 7 |     Args:
 8 |         name: Person's name
 9 | 
10 |     Returns:
11 |         Greeting message
12 |     """
13 |     return f"Hello, {name}!"
14 | 
15 | 
16 | def calculate_sum(a: int, b: int) -> int:
17 |     """Calculate sum of two numbers.
18 | 
19 |     Args:
20 |         a: First number
21 |         b: Second number
22 | 
23 |     Returns:
24 |         Sum of a and b
25 |     """
26 |     return a + b
27 | 
28 | 
29 | if __name__ == "__main__":
30 |     print(greet("World"))
31 |     print(f"Sum: {calculate_sum(10, 20)}")
32 |
```

## Full File with Line Numbers

```py
 1 | """Sample Python file for regression testing."""
 2 | 
 3 | 
 4 | def greet(name: str) -> str:
 5 |     """Greet someone by name.
 6 | 
 7 |     Args:
 8 |         name: Person's name
 9 | 
10 |     Returns:
11 |         Greeting message
12 |     """
13 |     return f"Hello, {name}!"
14 | 
15 | 
16 | def calculate_sum(a: int, b: int) -> int:
17 |     """Calculate sum of two numbers.
18 | 
19 |     Args:
20 |         a: First number
21 |         b: Second number
22 | 
23 |     Returns:
24 |         Sum of a and b
25 |     """
26 |     return a + b
27 | 
28 | 
29 | if __name__ == "__main__":
30 |     print(greet("World"))
31 |     print(f"Sum: {calculate_sum(10, 20)}")
32 |
```

## Line Number Styling Examples

This document demonstrates the different line number styles available in embedm.

### Default Style

The default style uses GitHub's color scheme with a light background:

<div class="code-block-default">
<style>
/* Default GitHub-style theme for code blocks with line numbers */
.code-block-default {
  background: #f6f8fa;
  border: 1px solid #d0d7de;
  border-radius: 6px;
  padding: 16px;
  margin: 16px 0;
  overflow-x: auto;
}
.code-block-default pre {
  margin: 0;
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
  font-size: 12px;
  line-height: 1.5;
}
.code-block-default .line {
  display: block;
}
.code-block-default .line-number {
  display: inline-block;
  width: 3ch;
  margin-right: 16px;
  color: #57606a;
  text-align: right;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

</style>
<pre><code class="language-py"><span class="line"><span class="line-number"> 1</span>&quot;&quot;&quot;Sample Python file for regression testing.&quot;&quot;&quot;
</span><span class="line"><span class="line-number"> 2</span>
</span><span class="line"><span class="line-number"> 3</span>
</span><span class="line"><span class="line-number"> 4</span>def greet(name: str) -&gt; str:
</span><span class="line"><span class="line-number"> 5</span>    &quot;&quot;&quot;Greet someone by name.
</span><span class="line"><span class="line-number"> 6</span>
</span><span class="line"><span class="line-number"> 7</span>    Args:
</span><span class="line"><span class="line-number"> 8</span>        name: Person&#039;s name
</span><span class="line"><span class="line-number"> 9</span>
</span><span class="line"><span class="line-number">10</span>    Returns:
</span><span class="line"><span class="line-number">11</span>        Greeting message
</span><span class="line"><span class="line-number">12</span>    &quot;&quot;&quot;
</span><span class="line"><span class="line-number">13</span>    return f&quot;Hello, {name}!&quot;
</span><span class="line"><span class="line-number">14</span>
</span><span class="line"><span class="line-number">15</span>
</span><span class="line"><span class="line-number">16</span>def calculate_sum(a: int, b: int) -&gt; int:
</span><span class="line"><span class="line-number">17</span>    &quot;&quot;&quot;Calculate sum of two numbers.
</span><span class="line"><span class="line-number">18</span>
</span><span class="line"><span class="line-number">19</span>    Args:
</span><span class="line"><span class="line-number">20</span>        a: First number
</span><span class="line"><span class="line-number">21</span>        b: Second number
</span><span class="line"><span class="line-number">22</span>
</span><span class="line"><span class="line-number">23</span>    Returns:
</span><span class="line"><span class="line-number">24</span>        Sum of a and b
</span><span class="line"><span class="line-number">25</span>    &quot;&quot;&quot;
</span><span class="line"><span class="line-number">26</span>    return a + b
</span><span class="line"><span class="line-number">27</span>
</span><span class="line"><span class="line-number">28</span>
</span><span class="line"><span class="line-number">29</span>if __name__ == &quot;__main__&quot;:
</span><span class="line"><span class="line-number">30</span>    print(greet(&quot;World&quot;))
</span><span class="line"><span class="line-number">31</span>    print(f&quot;Sum: {calculate_sum(10, 20)}&quot;)
</span><span class="line"><span class="line-number">32</span>
</span></code></pre>
</div>

The `line_numbers_style` property is optional. If omitted, the `default` theme is used automatically.

### Dark Style

The dark style features a dark background suitable for dark-themed documentation:

<div class="code-block-dark">
<style>
/* Dark theme for code blocks with line numbers */
.code-block-dark {
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 6px;
  padding: 16px;
  margin: 16px 0;
  overflow-x: auto;
  color: #e6edf3;
}
.code-block-dark pre {
  margin: 0;
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
  font-size: 12px;
  line-height: 1.5;
  color: #e6edf3;
}
.code-block-dark .line {
  display: block;
}
.code-block-dark .line-number {
  display: inline-block;
  width: 3ch;
  margin-right: 16px;
  color: #7d8590;
  text-align: right;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

</style>
<pre><code class="language-py"><span class="line"><span class="line-number"> 1</span>&quot;&quot;&quot;Sample Python file for regression testing.&quot;&quot;&quot;
</span><span class="line"><span class="line-number"> 2</span>
</span><span class="line"><span class="line-number"> 3</span>
</span><span class="line"><span class="line-number"> 4</span>def greet(name: str) -&gt; str:
</span><span class="line"><span class="line-number"> 5</span>    &quot;&quot;&quot;Greet someone by name.
</span><span class="line"><span class="line-number"> 6</span>
</span><span class="line"><span class="line-number"> 7</span>    Args:
</span><span class="line"><span class="line-number"> 8</span>        name: Person&#039;s name
</span><span class="line"><span class="line-number"> 9</span>
</span><span class="line"><span class="line-number">10</span>    Returns:
</span><span class="line"><span class="line-number">11</span>        Greeting message
</span><span class="line"><span class="line-number">12</span>    &quot;&quot;&quot;
</span><span class="line"><span class="line-number">13</span>    return f&quot;Hello, {name}!&quot;
</span><span class="line"><span class="line-number">14</span>
</span><span class="line"><span class="line-number">15</span>
</span><span class="line"><span class="line-number">16</span>def calculate_sum(a: int, b: int) -&gt; int:
</span><span class="line"><span class="line-number">17</span>    &quot;&quot;&quot;Calculate sum of two numbers.
</span><span class="line"><span class="line-number">18</span>
</span><span class="line"><span class="line-number">19</span>    Args:
</span><span class="line"><span class="line-number">20</span>        a: First number
</span><span class="line"><span class="line-number">21</span>        b: Second number
</span><span class="line"><span class="line-number">22</span>
</span><span class="line"><span class="line-number">23</span>    Returns:
</span><span class="line"><span class="line-number">24</span>        Sum of a and b
</span><span class="line"><span class="line-number">25</span>    &quot;&quot;&quot;
</span><span class="line"><span class="line-number">26</span>    return a + b
</span><span class="line"><span class="line-number">27</span>
</span><span class="line"><span class="line-number">28</span>
</span><span class="line"><span class="line-number">29</span>if __name__ == &quot;__main__&quot;:
</span><span class="line"><span class="line-number">30</span>    print(greet(&quot;World&quot;))
</span><span class="line"><span class="line-number">31</span>    print(f&quot;Sum: {calculate_sum(10, 20)}&quot;)
</span><span class="line"><span class="line-number">32</span>
</span></code></pre>
</div>

This theme uses high-contrast colors optimized for readability on dark backgrounds.

### Minimal Style

The minimal style provides simple, lightweight styling:

<div class="code-block-minimal">
<style>
/* Minimal theme for code blocks with line numbers */
.code-block-minimal {
  border: 1px solid #ccc;
  padding: 12px;
  margin: 12px 0;
  overflow-x: auto;
}
.code-block-minimal pre {
  margin: 0;
  font-family: monospace;
  font-size: 13px;
  line-height: 1.4;
}
.code-block-minimal .line {
  display: block;
}
.code-block-minimal .line-number {
  display: inline-block;
  width: 3ch;
  margin-right: 12px;
  color: #888;
  text-align: right;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

</style>
<pre><code class="language-py"><span class="line"><span class="line-number"> 1</span>&quot;&quot;&quot;Sample Python file for regression testing.&quot;&quot;&quot;
</span><span class="line"><span class="line-number"> 2</span>
</span><span class="line"><span class="line-number"> 3</span>
</span><span class="line"><span class="line-number"> 4</span>def greet(name: str) -&gt; str:
</span><span class="line"><span class="line-number"> 5</span>    &quot;&quot;&quot;Greet someone by name.
</span><span class="line"><span class="line-number"> 6</span>
</span><span class="line"><span class="line-number"> 7</span>    Args:
</span><span class="line"><span class="line-number"> 8</span>        name: Person&#039;s name
</span><span class="line"><span class="line-number"> 9</span>
</span><span class="line"><span class="line-number">10</span>    Returns:
</span><span class="line"><span class="line-number">11</span>        Greeting message
</span><span class="line"><span class="line-number">12</span>    &quot;&quot;&quot;
</span><span class="line"><span class="line-number">13</span>    return f&quot;Hello, {name}!&quot;
</span><span class="line"><span class="line-number">14</span>
</span><span class="line"><span class="line-number">15</span>
</span><span class="line"><span class="line-number">16</span>def calculate_sum(a: int, b: int) -&gt; int:
</span><span class="line"><span class="line-number">17</span>    &quot;&quot;&quot;Calculate sum of two numbers.
</span><span class="line"><span class="line-number">18</span>
</span><span class="line"><span class="line-number">19</span>    Args:
</span><span class="line"><span class="line-number">20</span>        a: First number
</span><span class="line"><span class="line-number">21</span>        b: Second number
</span><span class="line"><span class="line-number">22</span>
</span><span class="line"><span class="line-number">23</span>    Returns:
</span><span class="line"><span class="line-number">24</span>        Sum of a and b
</span><span class="line"><span class="line-number">25</span>    &quot;&quot;&quot;
</span><span class="line"><span class="line-number">26</span>    return a + b
</span><span class="line"><span class="line-number">27</span>
</span><span class="line"><span class="line-number">28</span>
</span><span class="line"><span class="line-number">29</span>if __name__ == &quot;__main__&quot;:
</span><span class="line"><span class="line-number">30</span>    print(greet(&quot;World&quot;))
</span><span class="line"><span class="line-number">31</span>    print(f&quot;Sum: {calculate_sum(10, 20)}&quot;)
</span><span class="line"><span class="line-number">32</span>
</span></code></pre>
</div>

This theme is ideal when you want code blocks to blend naturally with your document's existing styling.

### Custom CSS Theme

You can create your own custom CSS file for unique styling. This example uses a custom blue theme:

<div class="code-block-custom-blue-theme">
<style>
/* Custom blue theme for code blocks with line numbers */
.code-block-custom-blue-theme {
  background: #e8f4f8;
  border: 2px solid #0066cc;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
  overflow-x: auto;
  box-shadow: 0 2px 8px rgba(0, 102, 204, 0.1);
}
.code-block-custom-blue-theme pre {
  margin: 0;
  font-family: "Courier New", monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #003366;
}
.code-block-custom-blue-theme .line {
  display: block;
}
.code-block-custom-blue-theme .line-number {
  display: inline-block;
  width: 3ch;
  margin-right: 20px;
  padding-right: 12px;
  color: #0066cc;
  font-weight: bold;
  text-align: right;
  border-right: 2px solid #0066cc;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

</style>
<pre><code class="language-py"><span class="line"><span class="line-number"> 1</span>&quot;&quot;&quot;Sample Python file for regression testing.&quot;&quot;&quot;
</span><span class="line"><span class="line-number"> 2</span>
</span><span class="line"><span class="line-number"> 3</span>
</span><span class="line"><span class="line-number"> 4</span>def greet(name: str) -&gt; str:
</span><span class="line"><span class="line-number"> 5</span>    &quot;&quot;&quot;Greet someone by name.
</span><span class="line"><span class="line-number"> 6</span>
</span><span class="line"><span class="line-number"> 7</span>    Args:
</span><span class="line"><span class="line-number"> 8</span>        name: Person&#039;s name
</span><span class="line"><span class="line-number"> 9</span>
</span><span class="line"><span class="line-number">10</span>    Returns:
</span><span class="line"><span class="line-number">11</span>        Greeting message
</span><span class="line"><span class="line-number">12</span>    &quot;&quot;&quot;
</span><span class="line"><span class="line-number">13</span>    return f&quot;Hello, {name}!&quot;
</span><span class="line"><span class="line-number">14</span>
</span><span class="line"><span class="line-number">15</span>
</span><span class="line"><span class="line-number">16</span>def calculate_sum(a: int, b: int) -&gt; int:
</span><span class="line"><span class="line-number">17</span>    &quot;&quot;&quot;Calculate sum of two numbers.
</span><span class="line"><span class="line-number">18</span>
</span><span class="line"><span class="line-number">19</span>    Args:
</span><span class="line"><span class="line-number">20</span>        a: First number
</span><span class="line"><span class="line-number">21</span>        b: Second number
</span><span class="line"><span class="line-number">22</span>
</span><span class="line"><span class="line-number">23</span>    Returns:
</span><span class="line"><span class="line-number">24</span>        Sum of a and b
</span><span class="line"><span class="line-number">25</span>    &quot;&quot;&quot;
</span><span class="line"><span class="line-number">26</span>    return a + b
</span><span class="line"><span class="line-number">27</span>
</span><span class="line"><span class="line-number">28</span>
</span><span class="line"><span class="line-number">29</span>if __name__ == &quot;__main__&quot;:
</span><span class="line"><span class="line-number">30</span>    print(greet(&quot;World&quot;))
</span><span class="line"><span class="line-number">31</span>    print(f&quot;Sum: {calculate_sum(10, 20)}&quot;)
</span><span class="line"><span class="line-number">32</span>
</span></code></pre>
</div>

The custom CSS file ([custom-blue-theme.css](custom-blue-theme.css)) defines styles with:
- Light blue background (#e8f4f8)
- Bold blue line numbers with a vertical border
- Rounded corners and subtle shadow
- Larger padding for a spacious feel

**Note:** Custom CSS files are resolved relative to the markdown file's location. You can also use absolute paths if needed.

### Embedding Specific Lines with Styles

You can combine line number styles with region selection:

<div class="code-block-dark">
<style>
/* Dark theme for code blocks with line numbers */
.code-block-dark {
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 6px;
  padding: 16px;
  margin: 16px 0;
  overflow-x: auto;
  color: #e6edf3;
}
.code-block-dark pre {
  margin: 0;
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
  font-size: 12px;
  line-height: 1.5;
  color: #e6edf3;
}
.code-block-dark .line {
  display: block;
}
.code-block-dark .line-number {
  display: inline-block;
  width: 2ch;
  margin-right: 16px;
  color: #7d8590;
  text-align: right;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

</style>
<pre><code class="language-py"><span class="line"><span class="line-number">1</span>&quot;&quot;&quot;Sample Python file for regression testing.&quot;&quot;&quot;
</span><span class="line"><span class="line-number">2</span>
</span><span class="line"><span class="line-number">3</span>
</span><span class="line"><span class="line-number">4</span>def greet(name: str) -&gt; str:
</span><span class="line"><span class="line-number">5</span>    &quot;&quot;&quot;Greet someone by name.
</span></code></pre>
</div>

### Text-based Line Numbers

For comparison, here's how text-based line numbers look (no styling customization available):

```py
7 | Args:
8 |     name: Person's name
9 |
```

Note that `line_numbers_style` only applies to `line_numbers: html`, not `line_numbers: text`.
