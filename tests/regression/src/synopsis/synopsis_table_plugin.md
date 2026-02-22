
Example of the synopsis plugin
==============================
 
## Frequency / En / 1 sentences

```yaml embedm
type: synopsis
source: ./table_plugin.md
max_sentences: 1
algorithm: frequency
language: en
```

## Luhn / En / 2 sentences

```yaml embedm
type: synopsis
source: ./table_plugin.md
max_sentences: 2
algorithm: luhn
language: en
```