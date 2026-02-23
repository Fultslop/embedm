DOCUMENTATION: Document Architecture
========================================

Release v1.0  
Created: 23/02/2026  
Closed: 
Created by: FS  

## Description

We need to document the overall architecture. This should cover

* Plugin architecture (discovery via entry-points, PluginBase ABC, registry, lifecycle)
* Main domain entities (Directive, PlanNode, Fragment/Document, Status/StatusLevel)
* Main orchestration flow
* Main services (infrastructure - filecache, parsing)
* Plan / compile two-phase model (validate_directive → validate_input → artifact → transform)
* Error model (Status / StatusLevel semantics, ERROR vs FATAL, propagation through the tree)
* Document model (Fragment sequence, parent_document, why plugin_sequence order matters)

Outside the scope of this document (will be documented elsewhere)
  - CLI
  - Configuration

## Target Audience

Users and plugin developers

## Related Features

`<optional link to original / related feature(s)>`

## Comments

`<Optional comments in the form DD/MM/YY Author: comment>`
