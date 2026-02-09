# Layout test

<div style="display: flex; flex-direction: row; gap: 20px;">
<div style="flex: 0 0 50%;">

# CSV Table Test

This tests CSV to markdown table conversion.

## Team Members

**Team Roster**

| name | role | department |
| --- | --- | --- |
| Alice | Engineer | Development |
| Bob | Designer | Creative |
| Charlie | Manager | Operations |

## Analysis

The table above shows our team structure.


</div>
<div style="flex: 0 0 50%;">

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

<div style="background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px; padding: 16px; overflow-x: auto; font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; font-size: 12px; line-height: 1.5;">
<pre style="margin: 0; overflow: visible;"><code class="language-py"><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;"> 1</span>&quot;&quot;&quot;Sample Python file for regression testing.&quot;&quot;&quot;
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;"> 2</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;"> 3</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;"> 4</span>def greet(name: str) -&gt; str:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;"> 5</span>    &quot;&quot;&quot;Greet someone by name.
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;"> 6</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;"> 7</span>    Args:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;"> 8</span>        name: Person&#039;s name
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;"> 9</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">10</span>    Returns:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">11</span>        Greeting message
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">12</span>    &quot;&quot;&quot;
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">13</span>    return f&quot;Hello, {name}!&quot;
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">14</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">15</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">16</span>def calculate_sum(a: int, b: int) -&gt; int:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">17</span>    &quot;&quot;&quot;Calculate sum of two numbers.
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">18</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">19</span>    Args:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">20</span>        a: First number
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">21</span>        b: Second number
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">22</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">23</span>    Returns:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">24</span>        Sum of a and b
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">25</span>    &quot;&quot;&quot;
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">26</span>    return a + b
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">27</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">28</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">29</span>if __name__ == &quot;__main__&quot;:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">30</span>    print(greet(&quot;World&quot;))
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">31</span>    print(f&quot;Sum: {calculate_sum(10, 20)}&quot;)
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">32</span>
</span></code></pre>
</div>

The `line_numbers_style` property is optional. If omitted, the `default` theme is used automatically.

### Dark Style

The dark style features a dark background suitable for dark-themed documentation:

<div style="background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 16px; overflow-x: auto; font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; font-size: 12px; line-height: 1.5; color: #c9d1d9;">
<pre style="margin: 0; overflow: visible;"><code class="language-py"><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;"> 1</span>&quot;&quot;&quot;Sample Python file for regression testing.&quot;&quot;&quot;
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;"> 2</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;"> 3</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;"> 4</span>def greet(name: str) -&gt; str:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;"> 5</span>    &quot;&quot;&quot;Greet someone by name.
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;"> 6</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;"> 7</span>    Args:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;"> 8</span>        name: Person&#039;s name
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;"> 9</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">10</span>    Returns:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">11</span>        Greeting message
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">12</span>    &quot;&quot;&quot;
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">13</span>    return f&quot;Hello, {name}!&quot;
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">14</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">15</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">16</span>def calculate_sum(a: int, b: int) -&gt; int:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">17</span>    &quot;&quot;&quot;Calculate sum of two numbers.
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">18</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">19</span>    Args:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">20</span>        a: First number
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">21</span>        b: Second number
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">22</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">23</span>    Returns:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">24</span>        Sum of a and b
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">25</span>    &quot;&quot;&quot;
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">26</span>    return a + b
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">27</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">28</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">29</span>if __name__ == &quot;__main__&quot;:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">30</span>    print(greet(&quot;World&quot;))
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">31</span>    print(f&quot;Sum: {calculate_sum(10, 20)}&quot;)
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">32</span>
</span></code></pre>
</div>

This theme uses high-contrast colors optimized for readability on dark backgrounds.

### Minimal Style

The minimal style provides simple, lightweight styling:

<div style="border-left: 2px solid #0969da; padding-left: 16px; overflow-x: auto; font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; font-size: 12px; line-height: 1.5;">
<pre style="margin: 0; overflow: visible;"><code class="language-py"><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;"> 1</span>&quot;&quot;&quot;Sample Python file for regression testing.&quot;&quot;&quot;
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;"> 2</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;"> 3</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;"> 4</span>def greet(name: str) -&gt; str:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;"> 5</span>    &quot;&quot;&quot;Greet someone by name.
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;"> 6</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;"> 7</span>    Args:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;"> 8</span>        name: Person&#039;s name
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;"> 9</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">10</span>    Returns:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">11</span>        Greeting message
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">12</span>    &quot;&quot;&quot;
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">13</span>    return f&quot;Hello, {name}!&quot;
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">14</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">15</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">16</span>def calculate_sum(a: int, b: int) -&gt; int:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">17</span>    &quot;&quot;&quot;Calculate sum of two numbers.
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">18</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">19</span>    Args:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">20</span>        a: First number
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">21</span>        b: Second number
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">22</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">23</span>    Returns:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">24</span>        Sum of a and b
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">25</span>    &quot;&quot;&quot;
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">26</span>    return a + b
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">27</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">28</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">29</span>if __name__ == &quot;__main__&quot;:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">30</span>    print(greet(&quot;World&quot;))
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">31</span>    print(f&quot;Sum: {calculate_sum(10, 20)}&quot;)
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #656d76; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em;">32</span>
</span></code></pre>
</div>

This theme is ideal when you want code blocks to blend naturally with your document's existing styling.

### Custom CSS Theme

You can create your own custom CSS file for unique styling. This example uses a custom blue theme:

<div style="background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px; padding: 16px; overflow-x: auto; font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; font-size: 12px; line-height: 1.5;">
<pre style="margin: 0; overflow: visible;"><code class="language-py"><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;"> 1</span>&quot;&quot;&quot;Sample Python file for regression testing.&quot;&quot;&quot;
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;"> 2</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;"> 3</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;"> 4</span>def greet(name: str) -&gt; str:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;"> 5</span>    &quot;&quot;&quot;Greet someone by name.
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;"> 6</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;"> 7</span>    Args:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;"> 8</span>        name: Person&#039;s name
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;"> 9</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">10</span>    Returns:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">11</span>        Greeting message
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">12</span>    &quot;&quot;&quot;
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">13</span>    return f&quot;Hello, {name}!&quot;
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">14</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">15</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">16</span>def calculate_sum(a: int, b: int) -&gt; int:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">17</span>    &quot;&quot;&quot;Calculate sum of two numbers.
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">18</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">19</span>    Args:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">20</span>        a: First number
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">21</span>        b: Second number
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">22</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">23</span>    Returns:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">24</span>        Sum of a and b
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">25</span>    &quot;&quot;&quot;
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">26</span>    return a + b
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">27</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">28</span>
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">29</span>if __name__ == &quot;__main__&quot;:
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">30</span>    print(greet(&quot;World&quot;))
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">31</span>    print(f&quot;Sum: {calculate_sum(10, 20)}&quot;)
</span><span style="display: block;"><span style="display: inline-block; width: 3ch; color: #57606a; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #d0d7de;">32</span>
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

<div style="background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 16px; overflow-x: auto; font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; font-size: 12px; line-height: 1.5; color: #c9d1d9;">
<pre style="margin: 0; overflow: visible;"><code class="language-py"><span style="display: block;"><span style="display: inline-block; width: 2ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">1</span>&quot;&quot;&quot;Sample Python file for regression testing.&quot;&quot;&quot;
</span><span style="display: block;"><span style="display: inline-block; width: 2ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">2</span>
</span><span style="display: block;"><span style="display: inline-block; width: 2ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">3</span>
</span><span style="display: block;"><span style="display: inline-block; width: 2ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">4</span>def greet(name: str) -&gt; str:
</span><span style="display: block;"><span style="display: inline-block; width: 2ch; color: #8b949e; user-select: none; text-align: right; padding-right: 1em; margin-right: 1em; border-right: 1px solid #30363d;">5</span>    &quot;&quot;&quot;Greet someone by name.
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


</div>
</div>