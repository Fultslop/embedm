FEATURE: Add deprecation to directive options
========================================
Draft
Release v1.1
Created: 27/02/2026
Closed: `<date>`
Created by: FS

## Description

We should go through the existing names of directives to make sure they follow the same pattern, ie accept snake case '_', but no kebab case '-'. Make sure booleans start with a verb. 

This is also a good opportunity to build the decprecation concept. For v2.0 we want to accept any properties with old names, but give a warning if the user used the older variations. 

It's up to plugins to issue warnings during the validate_directive and map deprecated properties to the actual properties. We might want to add a utility method to the base class, eg def `resolve_property(name:str, deprecated_names: list[str] ) -> tuple[str, Status]:` where the status signifies a deprecated property (warning) or missing properties (error).

## Acceptance criteria

`<List of testable outcomes or DISCUSS if more discussion is warranted>`

## Comments

`<Optional comments in the form DD/MM/YY Author: comment>`