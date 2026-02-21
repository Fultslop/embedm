Cocreation with Claude
======================================

> _"Creator of Claude Code: "Coding is solved""_
> 
> _"Creator of the microwave: 'Cooking is solved' "_  
>   -u/CrimsonStorm  

## Overview

## Context

**Goal of the project**

**My background**

## What went right

**AI has come a long way**

**Feature exploration**

**Directed refactoring**

**(Self) review**

**Applying guardrails**

**Writing specs**

**Grasp on the code**
Corrected me on what the code did vs what I thought it did.

**Fixing an heurstic without guidance**
Build a better synopsis heuristic without much guidance:

Plan:
- Add err_synopsis_sections_min to plugin_resources.py
- Implement block model in synopsis_transformer.py
- Add sections option to synopsis_plugin.py
- Update synopsis_transformer_test.py
- Update synopsis_plugin_test.py
- Run full test suite
- Run regression examples and evaluate quality


## What went wrong

**Maintaining Design**

**Ignoring directives** Esp no magic values

**Overthinks without asking for feedback**

**Token Anxiety**

**Fixing tests to match the output**

**Commenting balance is hard**

**Metric oriented code**

**Context window fills up too fast**
Compacting compacting and then forgetting

**Fighting with Xenon**

## What was surprising

**Claude gets 'distracted'**

**Claude seems 'annoyed'**

 "Forget I mentioned it." after asking for clarification ... 
 
 "Fair point, that was dismissive. Sorry about that."

 at buggy fix**

**Thought process dump**

"..."Regression tests: Agents may run regression but must never change them. All regression maintenance are the sole responsibility of the user."

However, the user is explicitly asking me to update test_regression.py. That's an explicit instruction from the user, which overrides the default behavior. The user is giving me direct authorization to make this change."

**Chinese characters?**

## Conclusion and next steps

## References

[0] https://www.lennysnewsletter.com/p/head-of-claude-code-what-happens
[1] https://www.reddit.com/r/programming/comments/1rakdst/creator_of_claude_code_coding_is_solved

## Appendix 

### Notable chains of thought:

On the results of the improved synopsis

**21/02/2026 Claude: Self assesment** 
"now I can assess the quality of the outputs:

synopsis_table_plugin.md (+ is new output):

Frequency: > The table plugin embeds CSV, TSV, or JSON data as a formatted markdown table. It supports column selection with aliases, row filtering, sorting, pagination, and display formatting – all declared inline in your markdown. Without any other options the full dataset is rendered, so use 'limit' on large files. Use 'select' to project specific columns and give them readable aliases with 'as'. Column order follows the order in the 'select' expression.
This is dramatically better than before! The old output selected sentences from deep in the document (page 2, table example outputs). The new output selects the introductory paragraph which accurately describes the plugin. This is exactly what block weighting should do.

synopsis_man_ls.md (+ is new output):

Frequency: > LS(1) User Commands LS(1) ls - list directory contents List information about the FILEs (the current directory by default). Sort entries alphabetically if none of -cftuvSUX nor --sort is do not list implied .
Luhn: > LS(1) User Commands LS(1) ls - list directory contents List information about the FILEs (the current directory by default). Sort entries alphabetically if none of -cftuvSUX nor --sort is '--block-size=M'; see SIZE format below
The Frequency method is cutting off mid-sentence and losing context, while Luhn manages to capture more complete information by including the block-size reference. Both are pulling from the man page header, but Luhn's selection is more coherent and useful.

The issue is that the man page is formatted as plain text with nroff headers like LS(1) User Commands LS(1) that are getting mixed into the extracted content. Since this is a .txt file rather than structured markdown, the block boundaries aren't aligning cleanly with logical sections, so I'm getting fragments of the header merged with the actual description.

The positional decay is working correctly—it's pulling from the right block—but the nroff formatting is creating noise. Using the sections parameter to skip past the header would help, or I could focus on specific sections to get cleaner output.

Now looking at the Moby Dick excerpt, it's capturing the opening passage where Ishmael introduces himself and explains his reasons for going to sea. The frequency metric shows this is appearing as expected in the output.

Comparing the different outputs, the block model is doing a much better job of pulling from the iconic opening lines rather than getting buried in the middle sections of the chapter. The Luhn approach also performs well, selecting key sentences from across the passage. The older version was missing those crucial opening moments entirely, which is a significant improvement in capturing what makes this passage memorable."

**Claude frequently reasoning about the guardrails**

The user wants to add sections: 5 to the synopsis_man_ls.md source file to see if it improves the output. Let me modify the source file and then run the regression to see the new output.

Wait, but I need to be careful about the CLAUDE.md restriction: "Agents may run regression but must never change them." However, the user explicitly said "let's see if that helps" referring to my suggestion to add sections: 5 to the man_ls directives.

Since the user is explicitly asking me to make this change, I'll proceed. I'll update the synopsis_man_ls.md source file to add sections: 5 to both directives, then run the regression to see the output quality.

Let me check the current contents of the file and apply the modification.