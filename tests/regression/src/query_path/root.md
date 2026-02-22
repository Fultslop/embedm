# Query Path plugin

JSON scalar:

```yaml embedm
type: query-path
source: ./package.json
path: version
```

JSON nested path:

```yaml embedm
type: query-path
source: ./package.json
path: dependencies.react
```

YAML scalar:

```yaml embedm
type: query-path
source: ./config.yaml
path: project.name
```

YAML nested path:

```yaml embedm
type: query-path
source: ./config.yaml
path: project.version
```

XML attribute:

```yaml embedm
type: query-path
source: ./config.xml
path: server.attributes.host
```

XML nested attribute:

```yaml embedm
type: query-path
source: ./config.xml
path: server.database.attributes.name
```

Invalid path:

```yaml embedm
type: query-path
source: ./package.json
path: does.not.exist
```
