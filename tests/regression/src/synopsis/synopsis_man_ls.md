
Example of the synopsis plugin
==============================
 
## Frequency / En / 3 sentences

```yaml embedm
type: synopsis
source: ./ls.1.txt
max_sentences: 5
algorithm: frequency
language: en
sections: 5
```

## Luhn / En / 10 sentences

```yaml embedm
type: synopsis
source: ./ls.1.txt
max_sentences: 5
algorithm: luhn
language: en
sections: 5
```