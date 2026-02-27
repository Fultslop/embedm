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

The process should work as follows (This doesn't apply to single, stdin compiles):

  * Collect all md files in the target directory / directories in case of compiling a directory (target_list)
  * When compiling a node completes, check if the file is in the target_list. If so write it to file and remove it from the target_list. This _should_ cause the file cache to have a reference to the file (altough it may get unloaded). 
  * When compiling of a node which has a source begins, check if the file_cache has a reference to the source. If so it means it was previously compiled and can be gotten from the file_cache. 
  * This does not handle the double compilation which can happen when referencing files outside the target directory or its subdirectories. Eg:

  root/  
    some_other   
        file_c
  
    target_dir/
        file_a
            -> references file_c
        file_b
            -> references file_c
  
  file_c is not in the target_list.

  I'm not sure if this avoidable at this point. This _could_ be avoided by carefully planning and ordering nodes, seeing there is a shared need for file_c and keeping it in memory or saving it to a scratch directory. This could be done in the future should this become a source of concern.

* Note multithreading is out of scope this item 

## Replication

Because this bug has been "fixed", it's no longer possible to replicate it directly. Suggest we build an integration / white box test to verify if this works as intended

**Start condition**
Create a file a and b in a directory. a references b. Both are `.md` files

**Execution**
Collect target list, both a and b should be on there.
Compile a. Both a and b should have compiled versions.
Compile b. B should be retrieved from the cache.

## Comments

`27/02/26 FS/Agent: During orchestration refactoring discussion, three open questions surfaced that must be resolved before implementing the write-through design above:`

`(1) Cache key — when A is compiled and written via the cache, what path is used as the key? The source path (A's original location) so that downstream embeds hit the cache, or the output path? Using the source path is necessary for B's embed of A to get the compiled version; but this would mean the cache entry for A's source path is replaced with compiled content, which could cause issues if A is also directly referenced elsewhere with its raw content. Using the output path means a separate lookup is needed.`

`(2) Write-through timing — within a single compile pass, A's content is resolved during planning (from its raw source). The compiled version only exists after A's transform completes. This means the write-through approach works for the cross-file case (A compiled first, B reads A's compiled output), but not for inlining within the same transform call. The pipeline order must guarantee A is compiled before B attempts to read it.`

`(3) Relationship to 'embedded' set — the current embedded set in _process_directory prevents A from being re-processed as a standalone root after being compiled as B's dependency. If writes go through the cache, does the embedded set become redundant, or do both mechanisms serve different purposes (one for root-skip logic, one for cache coherence)?`
