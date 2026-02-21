FEATURE: Synopsis plugin
========================================
DRAFT  
Release v1.0  
Created: 20/02/2026  
Closed: `<date>`  
Created by: FS

## Description

Create a plugin that generates a deterministic synopsis of the current document or the document referred to in the `source` option of corresponding `Directive`. 

Directive definition:

```yaml embedm
type: synopsis
source: optional, if not defined take current document otherwise create a synopsis of source. Text files like .md, .txt are supported (others ?)
max_lines: maximum number of lines of the synopsis. Need to try to see what makes sense.
algorithm: Luhn, TextRank, Custom Frequency, MaxEnt / Statistical. Start with the simplest first for this version. Need at least two options. Discuss.
```

Notes: needs to execute before ToC

## Acceptance criteria

* The plugin creates a human readable synopsis that captures the source / current document correctly.

* The plugin is part of the standard plugins (like hello_world, file, table...)

* We have associated unit and integration tests.

* We have associated regression tests.

* Documentation is out of scope for now.

## Comments

**20/02/2026 ML:**
Possible options
Tool/Library,Language,Algorithm,Complexity  
Sumy,Python,"Multiple (Luhn, TextRank)","Low - ""Plug and play"""  
NLTK / SpaCy,Python,Custom Frequency,Low - Great for DIY  
Gensim,Python,TextRank (Optimized),Medium - Very fast  
Apache OpenNLP,Java,MaxEnt / Statistical,Medium - Enterprise grade  
