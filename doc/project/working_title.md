Cocreation with Claude
======================================

> _"Creator of Claude Code: "Coding is solved""_
> 
> _"Creator of the microwave: 'Cooking is solved' "_  
>   -u/CrimsonStorm  

## Overview

## Context

**Goal of the project**

The goal of this project was to get first hand experience with co-creating with an coding assistant, Claude in this case. The project was meant to be limited in scope and moderate in complexity. To narrow down the latter statement, the intention was to have a set of non-trivial, relevant problems that have a well-defined to "define-able" input, output behavior. In other words, something more complex than building a shopping-list-app or calculator, but something well below of theshold of "solve fusion and build me a schematic I can fit in my tiny backyard". 

With this in mind, I started working on something that has been bugging me in my both my professional work and own personal projects: documentation maintenance. While I'm hardly an accomplished writer, I appreciate well written, easy to understand documentation. I generally make an effort to provide something that new users can quickly scan and get going with any of my projects. This sentiment - also generally - dies as soon as the project becomes big enough that examples in the documentation become a liability and maintenance cost as the code being documented changes, is deleted, or superceded by new code. I want the code upkeep to be automated.

I had a general approach in mind, but never got around building it because while trivial on paper, there are a surprising number of implementation details, seemingly unassuming features and other considerations that go into making "automatic document maintenance" work. 

Using various Google and free versions of the chatbot cadre, I _briefly_ verified if no obvious solution existed. The research came up with some similar tools but nothing concrete. Based on the principle that everything already exists and no idea is new, I assume there is a tool that covers Embedm's functionality (maybe some clever grep / regex could even do it), but I am happy to stay ignorant in this respect pretending I've created something original.  

**My background**

In brief, I'm a software engineer with 25+ years of professional experience ranging from start-ups to Fortune 500 companies and at least one of the major software giants. I've worked on the hardware level all the way up to framework(s)-du-jour on the front-end. During this time I wore many hats from code monkey to engineering manager. On a good day, with enough coffee and a good night of sleep, I imagine I am capable of producing average-grade but production ready software. I'm capable, but not a genious. 

What is somewhat ironic is that I am late to the AI party considering I started my career 28 years ago in a company that build ... software agents. Although I'm sure I'm reflecting on this through the pink-colered glasses of nostalgia, the people in that company were some of the smartest people I worked with. The software we produced was well ahead of its time. We had a messaging-bus when Kafka was only known as writer, we created scalable object storage and retrieval almost a decade before the the likes of Redis and Hazelcast appeared, micro-services came as a side-effect of the platform. The company ultimately failed because its solutions were way ahead of its time and in need of a timely problem(s) to solve. 

One of the projects we ran was based on the [Alice](https://en.wikipedia.org/wiki/Artificial_Linguistic_Internet_Computer_Entity) framework. The results were not encouraging and as I result I've been somewhat dismissive the rise of chatbots over the last few years (somewhat of a category error I suppose). My experiences with an early version of co-pilot, which with its auto-complete intrusiveness of nonsense co-snippets, were not encouraging to look deeper into the subject either. 

It wasn't until a random afternoon, where being stuck in a somewhat boring company townhall, I prompted the free Claude-version to build a JS based, bare-bones 2D physics engine and it did so, with graphics and all, in under a couple of seconds. It wasn't perfect but with one or two fixes, it performed admirally well. I was impressed and decided to buy a Claude pro-version to see and explore what it could do.

A couple of weeks later, here we are...

## What went wrong

Let's start with all the things that yielded a "MISS" (*). Something that either caused Claude to produce a wrong solution, or more broadly, yielded a negative user experience.

(*) MISS was identified, by Claude as a useful category in the dev backlog, capturing 'something' that Claude didn't do right. In my experience a lot of these could be attributed to PICNIC or overly broad requests. 

**Token Anxiety**

For those that are not familiar, when working with Claude Code, you have a token budget. Asking Claude Code to do something uses up these tokens. Spend all your tokens and Claude will stop their work. You are left dangling as you have to wait until your next refresh. This next refresh can either come on a 'daily' cadence as you deplete your 'session' allowance or weekly cadence and you deplete your 'weekly' allowance. Antrophic provides a helpful dashboard where you can see your current budget.

The budget is set, in my experience, to a fairly low number (for the Pro plan). I'm estimating working full time with Claude, you are getting 2.5 - 4 days per week depending on what you ask Claude and what work you're doing yourself. After that you're stuck with having to do all the tedious work yourself. 

A lot of burn is caused by Claude going off on some recursive side-quest that sometimes reads like an angsty-anime of doubt and self-discovery. Claude may discover a side-effect of something you asked and instead of getting back to the user, it will wander off looking for a solution. Two sentences after the initial discovery, the stories twist reveals itself with a "But wait.." and a new side quest is or trace-back is initiated. When it eventually resolves ("maybe i should ask the user"), 50% of your session budget could be gone. 

Another of these instances is where Claude's context window gets too full and a so-called `compaction process` is started. After this Claude feels fresh and new but has to read up on what it was doing... which also consumes a budget. At a particular junction in the project, we were closing in on a feature with only a few more tweaks to go. We had 2% of tokens left, but given that the remaining issues were small that should have fitted in the budget... Then compacting started, Claude woke up and consumed the remaining 2% catching up on things.

Both cases (and others) lead to a sub optimal user experience where you as a user feel penalized for Claude's reflections and memory refreshes while being only marginally in control over these.  

I understand Antropic needs to earn a living but right now it 'feels' there is a more than reasonable margin on the product they are selling (tokens) at the expense of the user's interest. Hopefully things like the context window size, more effective reasoning, improve in the future  

**Maintaining Design/Architecture**

**Ignoring directives** Esp no magic values

**Overthinks without asking for feedback**

**Fixing tests to match the output**

**Commenting balance is hard**

**Metric oriented code**

**Context window fills up too fast**
Compacting compacting and then forgetting

**Fighting with Xenon**

**Keeping up with Claude**

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

**Called out tech debt as a to-do**
Recognized opportunity to re-use shared code, wonder if this only works if this inside their context window. 



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

**We may need more deterministic guardrails**

* Is a test relevant
* Does an implementation introduce new abstractions
    - verbose feature implemented an event callback. Wasn't discussed. 

## References

|0| https://www.lennysnewsletter.com/p/head-of-claude-code-what-happens  
|1| https://www.reddit.com/r/programming/comments/1rakdst/creator_of_claude_code_coding_is_solved  
|2| Alice https://en.wikipedia.org/wiki/Artificial_Linguistic_Internet_Computer_Entity

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