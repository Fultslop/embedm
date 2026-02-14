
# Functional Analysis: EmbedM

This document is a high-level overview of the relevant components in Embedm. It relects the intention of the behavior not the implementation. The implementation may differ in minor ways.

Each section outlines the behavior of a layer and its most important components. 

Sections 1 to 6

## 1. Domain Model

Contains the domain entities of Embedm.

**Directive**

Contains the Ebedm type and its properties.

**Span**

General span consisting of an offset + length. In the context of Embedm used to refer to lines in a document.

**Document**

Decomposition of a file into fragments. A fragment is either a text, line span, or a Directive.

**Plan node**

A node structure which can be used to capture a step in the compilation plan derived from a directive.

## 2. Io

Captures all aspects of file IO. Embedm only allows file I/O. Net connections, database connections should not be supported

**File cache**

Manages actual file interaction, caching and may flag violations of the constraints.

## 3. Parsing 

Contains all parsing functionality. Used to extract Embedm yaml blocks or language specific regions.

**Directive parsing**

Parses Embedm Yaml into Directives.

**Symbol parsing**

Parses coding specific language regions

## 4. Plugin Framework

Defines the abstract classes to implement transformers and plugins.

**Transformer base**

Base class capturing the transformer functionality. A transformer takes a directive and generates the resulting text which can be embedded in the resulting document

**Plugin base**

Captures functionality used to validate directives to see if the required properties are included. Provides a transform method invoking one or more transformers.

## 5. Application

Contains all services making up the embedm application.

**CLI**

Parses the command line

**Configuration**

Contains the project's configuration

**Planner**

Creates the embedding plan for a file

**Compiler**

Compiles the output

**Orchestration**

Executes the services in the correct order

## 6. Embedm plugins

Standard plugins included with Embedm