BUG: Expected plugin properties which are missing cause a crash
========================================
Created: 27/02/2026
Closed: `<date>`
Created by: FS

## Description

Creating a custom plugin and omitting one a default properties 'name' or 'directive_type' causes a crash at start up. As this is considered a user-input error, it should be handled gracefully rather than crashing during the startup of embedm.

## Replication


**Input:**

* Use the plugin in `tmp\plugin_test_27022026_1` 
* comment out `name` and / or `directive_type`
* run `embedm test.md`

**Output**

embedm will crash:

```shell
embedm v0.9.10
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "C:\Users\lassc\AppData\Local\Programs\Python\Python312\Scripts\embedm.exe\__main__.py", line 5, in <module>
  File "C:\Users\lassc\Code\python\embedm\src\embedm\application\orchestration.py", line 63, in main
    context, load_errors = _build_context(config)
                           ^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\lassc\Code\python\embedm\src\embedm\application\orchestration.py", line 368, in _build_context
    errors = plugin_registry.load_plugins(enabled_modules=set(config.plugin_sequence))
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\lassc\Code\python\embedm\src\embedm\plugins\plugin_registry.py", line 65, in load_plugins
    self.lookup[instance.name] = instance
                ^^^^^^^^^^^^^
AttributeError: 'MermaidPlugin' object has no attribute 'name'
```


**Expected**

embedm should print for each plugin that is missing these properties

```shell
[FATAL] '<plugin_name_a>' is missing attribute(s): '<missing property/properties>'.
[FATAL] '<plugin_name_b>' is missing attribute(s): '<missing property/properties>'.
...
[FATAL] '<plugin_name_N>' is missing attribute(s): '<missing property/properties>'.
Embedm cannot start, please fix these issues first or disable the properties in 'pyproject.toml' and 'embedm-config.yaml'
```
