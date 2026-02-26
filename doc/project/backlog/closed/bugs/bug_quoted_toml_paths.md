BUG: Query-path does handle quoted toml paths
========================================
Created: 26/02/2026  
Closed: 26/02/2026  
Created by: FS  


## Description

Query path on toml which contains quotes yields a `path not found`. It is a valid path and should work.

## Replication

**Input:**

```yaml embedm
type: query-path
source: ./pyproject.toml
# this fails
path: project.entry-points."embedm.plugins"
```

and the relevant section in `./pyproject.toml`

```toml
[project.entry-points."embedm.plugins"]
embedm_file = "embedm_plugins.file_plugin:FilePlugin"
...
```

**Output**

error: path 'project.entry-points."embedm.plugins"' not found in 'pyproject.toml'.

**Expected**

No error and

```toml
embedm_file = "embedm_plugins.file_plugin:FilePlugin"
table_of_contents = "embedm_plugins.toc_plugin:ToCPlugin"
hello_world = "embedm_plugins.hello_world_plugin:HelloWorldPlugin"
table = "embedm_plugins.table_plugin:TablePlugin"
synopsis = "embedm_plugins.synopsis_plugin:SynopsisPlugin"
recall = "embedm_plugins.recall_plugin:RecallPlugin"
query_path = "embedm_plugins.query_path_plugin:QueryPathPlugin"
```
