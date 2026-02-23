**Claude**
On dog-fooding recall in the project:

Yes, and there's a natural fit. The project's own docs are the kind of knowledge base recall is designed for — structured markdown, topically dense, rarely read linearly. A few concrete places it could help me directly:

A compiled context document. A file like doc/project/context.md with recall directives pulling from devlog.md, CLAUDE.md, and active specs. E.g.:


type: recall
source: ./devlog.md
query: "plugin sequence execution configuration"
max_sentences: 4
When I read that at the start of a session, I get pre-filtered decision history rather than scanning 200 lines of devlog.

Feature specs referencing prior decisions. A spec could include a recall over the devlog to surface related architectural decisions made during earlier features, reducing the chance I miss relevant history.

The manual itself. Already done — cross-references between plugin manuals via recall (as the examples in recall_plugin.md already demonstrate).

The limitation is that recall queries are fixed at compile time, so it works best for standing questions — "what are the coding standards around validation?", "what decisions were made about plugin sequencing?" — rather than session-specific questions. But those standing questions are exactly the ones worth pre-computing.

Would you want to create a compiled context document as a next step, or is that out of scope for now?

**FS**

 _"can we measure your "performance" with and  without this document ?"_

 **Claude**

 On measuring performance — let me be honest about what's feasible:

A true A/B test isn't possible here. The sessions aren't reproducible: tasks vary in complexity, your instructions vary in specificity, and I have inherent variability. There's no ground truth for "how many turns should this take."

What we can measure with low overhead:

Proxy	How	Limitation
Correction rate	Count user corrections per task (like today's version miss)	**Requires you to note corrections you'd otherwise just make silently**
Tool-call count to first correct output	Count reads/searches before completing a task correctly	Tedious to track manually
First-pass CI rate	Does ruff/mypy/xenon pass on first attempt?	Already partially visible in the session transcript
[MISS] devlog tags	Tag errors where I missed established patterns	Lightweight; already have a devlog convention
The most useful and lowest-overhead option: add a [MISS] tag to the devlog for cases where I get something wrong that context should have prevented. We already use [SUGGESTION] — this is the same pattern. After a few sessions with the context document, we compare [MISS] frequency before and after.

The limitation: "after" sessions will also have different tasks, so we're comparing samples, not the same task twice. But if the specific categories of misses we've observed (pattern blindness, hardcoded values, missing established conventions) stop appearing, that's signal.