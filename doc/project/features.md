EmbedM Features
===============

In this document we capture the individual features that make Ebedm and have been implemented. It is a reflection of what is, and what is NOT Ebedm. This document does NOT capture future features, improvements or otherwise.

## Scope and Intentions

* Embedm takes a markdown input file or set of input files and deterministically _compiles_ them into one or more output files. 

* Embedm ONLY _reads_ from local files. It does NOT get data from other sources like URLs or database connections. 

* Embedm can ONLY _read_ and _write_ from and to paths that the user has explicitely defined. The only exception to reading is the current working directory of Embedm, everthing under said directory can be read by Embedm.

* Embedm adheres to strict limitations to protect the user. Limitations include elements like the maximum file size that can be read or produced.

* At any point the user is in control of what Embedm does and how via a CLI and the Embedm Configuration.

* Embedm provides a framework and a set of standard plugins to execute document compilation. The framework facilitates common functionality, the safe execution of these plugins as well as the means to _easily_ extend Embedm with new plugins without having to touch the Embedm code itself. 

* Errors caused input are gracefully handled and clearly communicated to the user via the CLI. 

* Errors caused by coding errors will cause Ebedm to crash at the point of this coding error without the option to recover.

## Functionalities

... this should just list the items in the backlog/closed folder with a one line description. 