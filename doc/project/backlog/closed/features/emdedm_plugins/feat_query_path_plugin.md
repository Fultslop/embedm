FEATURE: Query Path plugin
========================================
Draft
Release v1.0
Created: 22/02/2026
Closed: 22/02/2026
Created by: Claude

## Description

A plugin that extracts and embeds a value from a JSON, YAML, or XML file using a dot-notation key path. The primary use case is keeping version numbers, metadata, and configuration values in a single source file and embedding them into documentation automatically — eliminating the manual synchronisation problem.

Pipeline: `source → normalize → query → present`

Each format has its own normalizer (`normalize_json.py`, `normalize_yaml.py`, `normalize_xml.py`). A shared query engine walks the normalized tree. A shared presenter renders the result.

Directive definition:

```yaml embedm
type: query-path
source: ./package.json
path: version
```

```yaml embedm
type: query-path
source: ./pyproject.toml
path: project.version
```

```yaml embedm
type: query-path
source: ./config.xml
path: server.attributes.host
```

### Behaviour

- `source` is required; there is no current-document mode.
- Format is auto-detected from the file extension: `.json` → JSON, `.yaml` / `.yml` → YAML, `.xml` → XML. Unrecognised extension → error caution block.
- `path` is a dot-separated key sequence into the normalised tree (e.g. `project.version`, `dependencies.react`).
- If `path` is omitted, the entire document is embedded as a fenced code block using the source format as the language tag.
- Integer path segments resolve list elements (`servers.0.host`).
- If the resolved value is a scalar (string, number, bool), it is output as plain inline text with no trailing newline — so it can be embedded mid-sentence.
- If the resolved value is a dict or list, it is formatted as a fenced `yaml` code block.
- Path not found → error caution block.
- Invalid source file (parse error) → error caution block.

### XML normalisation

XML nodes are projected onto the following structure:

```
{
  "<element_name>": {
    "attributes": { "<attr>": <value>, ... },   # omitted if no attributes
    "value": "<text content>",                   # omitted if no text content
    "<child_element>": { ... },                  # one key per child element name
    ...
  }
}
```

`attributes` and `value` are reserved keys. When an element has both text content and child elements, both `value` and the child keys coexist at the same level.

XML input:

```xml
<node attr_a="foo" attr_b="123">
    hello
    <child x="1"/>
</node>
```

Normalised:

```yaml
node:
  attributes:
    attr_a: foo
    attr_b: "123"
  value: hello
  child:
    attributes:
      x: "1"
```

Querying: `node.attributes.attr_a` → `foo`, `node.value` → `hello`, `node.child.attributes.x` → `1`.

**Reserved key escaping:** if an XML element is literally named `<value>` or `<attributes>`, wrap the path segment in backticks to access it as a literal child key rather than the reserved slot:

```yaml embedm
type: query-path
source: ./config.xml
path: node.`value`.child
```

### Architecture

- Single plugin class `QueryPathPlugin`; `type: query-path` is the only directive type.
- Normalizers: `normalize_json.py` (`json` stdlib), `normalize_yaml.py` (`PyYAML`, already a dependency), `normalize_xml.py` (`xml.etree.ElementTree` stdlib — no new dependency).
- Shared query engine: dot-notation walker with integer index and backtick-literal segment support.
- Shared presenter: scalar → inline text, dict/list → fenced code block.
- Plugin sequence: runs after `file`.

### Out of scope (v2.0)

- Directory as a query source → `feat_query_directory_source.md`
- Glob / wildcard path queries and multi-result output → `feat_query_glob_paths.md`
- XPath `@attr` shorthand for `attributes.<attr>`

## Acceptance criteria

- Scalar value at a given path is embedded as plain text (no trailing newline, embeddable inline)
- Nested path notation (`a.b.c`) resolves correctly for JSON, YAML, and XML
- Integer segment in path resolves list elements (`a.0.b`)
- Full document embed (no `path`) outputs a fenced code block with the correct language tag
- `.json`, `.yaml`, `.yml`, `.xml` extensions all supported
- Unrecognised extension → error caution block
- Invalid path → error caution block
- Invalid source file → error caution block
- XML: `attributes` key resolves element attributes
- XML: `value` key resolves element text content
- XML: element with both text content and child elements resolves both correctly
- XML: backtick-escaped path segment resolves a literal child key, not the reserved slot
- Unit and integration tests included
- Regression example included

## Comments

`22/02/2026 Claude:` Killer use case: embedding `version` from `pyproject.toml` or `package.json` into a README or changelog. Also useful for embedding API config (base URLs, environment names) into documentation. Shares no infrastructure with table plugin — data loading is separate and simpler.

`22/02/2026 FS:` We should consider generalizing it so the "user api" (ie directive) is the same for all variations. Take in account .xml (support of c# / java projects) or a directory structure (to embed file layout).

The process would be
`source` -> `node normalization` -> `query exectution` ->`presentation`

where the node `normalization step` would project the input source to a standard, query-able format. Each format should have its own file (normalize_json.py, normalize_yaml.py, normalize_xml.py and so on)

Let's look at some cases (note these are discussion starters, we need to work out the details)

**Xml**
Xml has attributes, a value and 0 or more children. This is different from json/yaml for instance that have "simple key/value pairs", ignoring arrays for now. So the normalization could project an xml node onto a structure:

xml input:

```xml
<node attr_name_a="value" attr_name_b=123>
    foo and bar
    <child_node foo="foo" bar="bar"/>
</node>
```

normalized xml node:

```yaml
- node
  - attributes
     - attr_name_a: "value"
     - attr_name_b: 123
  - value: "foo and bar"
  - child_node
    - attributes
        ...
```

Note: the structure above is a proposal, needs discussion

Which could be queryable the same way as json / yaml.

**Json/Yaml**
From json/yaml we should take in account the existance of arrays, which should after node normalization expand to an index

json input example
```json
[
    "obj1": { "key": "value", "arr": [1,2,3]}
]
```

normalized json node:

```yaml
- 0
  - obj1
    - key: value
    - arr:
        - 0: 1
        - 1: 2
        - 2: 3
```

**Directories/Files**

A file can be considered a node with properties, same with directories. This too can be normalized:

```
File structure

dir_1/
    dir_2/
        file_2.md
    foo.txt
    bar.xml
```

this can be normalized to

```yaml
- dir_1
    - properties
        - last_modified: DD/MM/YY
        - permissions: RW-
    - files
        - foo.txt
            - last_modified: DD/MM/YY
            - size: 12938
            - permissions:
```

**Query structure:**

To cater to more than single properties we could change the directive to use a glob like structure (discuss)

```yaml embedm
type: json
source: ./directory
path: a/b/**/.*md
recursive_depth (should be the same as used in config?): number
output: (key or path) | value (default)
format: list or tree
```

`22/02/2026 FS/Claude:` Decisions locked. Directive unified to `type: query-path`; format auto-detected from extension. XML normalisation structure agreed: `attributes` and `value` are reserved keys; text + children coexist at the same level. Backtick escaping for reserved key collisions (`node.`value``). Attribute querying via dot-notation (`node.attributes.x`), XPath `@` shorthand deferred. Directory source and glob queries deferred to v2.0 — see `feat_query_directory_source.md` and `feat_query_glob_paths.md`.
