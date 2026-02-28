FEATURE: Resource Caching
========================================
Draft
Release v1.2
Created: 28/02/2026
Closed: `<date>`
Created by: FS

## Description

We want to avoid duplicate work _within an embedm session_. Files that are being compiled may share the same embeddings or 'resources', either within one file (eg re-use of a table) or between files (file a and file b importing file c). The shared resources should not be compiled for each use as this has a noticable performance hit, but only once. We avoid file loading via the `file_cache` but this is too limited, so we need a new mechanism to determine if resources have already been processed and can be retrieved from a cache. 

We plan to implement this via a `resource_cache`. The resource_cache allows _storing_ and _retrieving_ resources by an `id` and `resource_state`. `ID` will map on a full path of the resource, we will need to see if it's possible to resolve relative paths by taking the relative path + CWD, so there's less burden op the caller. `resource_state` is an enum consisting of:

 * `RAW` or `SOURCE` (discuss which name is better): this is the unprocessed input or file data (chars/bytes)
 * `NORMALIZED` the result of a plugins `normalize_data` function.
 * `TRANSFORMED`the result of a plugins `transform` function.

The result of a retrieve call result depends on whether or not the resource state is available and if there were no errors. 

In other words, the caller can ask the resource cache if a result is already cached. The implication being that plugins, being the orchestraters of the transformation process, need to be cache-aware. The implementation is different case by case, we'll discuss this later.

We plan to implement this as a standalone system, then create and add this system to the respective contexts in orchestration and finally we'll move the existing plugins over.

The system consists of the following components:

* A memory bound, recency lookup table. This table works similar  

## Acceptance criteria

`<List of testable outcomes or DISCUSS if more discussion is warranted>`

## Comments

`<Optional comments in the form DD/MM/YY Author: comment>`