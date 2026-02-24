BUG: MD Files were skipped during compilation
=============================================
Draft
Created: 24/02/2026
Closed: `<date>`
Created by: FS  

## Description

Table / Synopsis manual were skipped because they were referenced by another file as embedded snippets. This stems from a misunderstanding that 'not compile twice' = 'skip files if they have been compiled before`.

The bug is "fixed" but we need to analyze the following in `plantree.py` to see if the intention is expressed correctly:

```py
def collect_embedded_sources(root: PlanNode, embed_type: str = "file") -> set[str]:
    """Return the resolved source paths of directives that merge content inline.

    Only sources from directives of `embed_type` are collected. Other directive types
    (recall, synopsis, query-path, table) read their source but do not merge it into
    the compiled output, so they must not be excluded from standalone compilation.
    """
    sources: set[str] = set()
    for node in walk_nodes(root):
        for child in node.children or []:
            if child.directive.source and child.directive.type == embed_type:
                sources.add(str(Path(child.directive.source).resolve()))
    return sources
```

The process should work as follows:

  * This doesn't apply to single compiles
  * Collect all md files in the target directory / directories in case of compiling a directory (target_list)
  * When compiling a node completes, check if the file is in the target_list. If so write it to file and remove it from the target_list. This _should_ cause the file cache to have a reference to the file (it may be unloaded). 
  * When compiling of a node which has a source begins, check if the file_cache has a reference to the source. If so it means it was previously compiled and can be gotten from the file_cache. 
  * This does not handle the double compilation which can happen when referencing files outside the target directory or its subdirectories. I'm not sure if this avoidable.
 
 ## Replication

Because this bug has been "fixed", it's no longer possible to replicate it directly. Suggest we build an integration / white box test to verify if this works as intended

**Start condition**
Create a file a and b in a directory. a references b. Both are `.md` files

**Execution**
Collect target list, both a and b should be on there.
Compile a. Both a and b should have compiled versions.
Compile b. B should be retrieved from the cache.

