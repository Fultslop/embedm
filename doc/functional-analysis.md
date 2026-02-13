
# Functional Analysis: EmbedM

## 1. System Orchestration & Flow

The system follows a strict linear progression: **Load Context → Plan → User Consent → Execute → Write.**

### **Orchestrator**

* **Responsibility:** Manages the lifecycle of the application and coordinates data movement between the Planner and the Compiler.
* **Input:** CLI Arguments and Configuration.
* **Behavior:** Initialize the `Context`.
* Trigger the `Planner` to build the DAG.
* If violations exist, interrupt for user consent (unless `--force` is used).
* Trigger the `Compiler` to generate the final `Document`.

**Constraint:** Must not contain domain logic; it is purely a "traffic controller."

## 2. Planning Phase (Static Analysis)

### **Planner**

* **Responsibility:** Recursively analyzes Markdown files to create a complete map of all embeddings.
* **Input:** Entry point file path and `Limits`.
* **Output:** An immutable `Plan` (DAG of `Plan Nodes`).
* **Behavior:** * Discovers `Directives` via the `Directive Parser`.
* Consults the `Plugin Registry` to validate directive types.
* Builds a dependency graph to detect recursion or circularity.



### **Plan Node**

* **Responsibility:** Represents a single unit of work (either a text block or a directive).
* **Properties:** Links a `Directive` to its metadata (file status, size, and child dependencies).

**Constraint:** Does not perform the actual transformation; it only marks the *intent* and *validity*.

### **Directive Parser**

* **Responsibility:** Scans raw Markdown text to identify `embedm` blocks.
* **Input:** Raw string.
* **Output:** List of `Directive` data objects.
* **Behavior:** Extracts the `Type`, `Source`, and `Options` dictionary. It must ignore standard Markdown code blocks unless they are specifically tagged as `embedm`.


## 3. Transformation & Execution

### **Plugin**

* **Responsibility:** Acts as the interface between the core engine and specific embedding logic (e.g., file embedding, symbol extraction).
* **Input:** `Directive` and `Configuration`.
* **Output:** A configured `Transformer`.
* **Behavior:** Validates that the directive's options satisfy the plugin's specific requirements.

### **Transformer (Base Class/Protocol)**

* **Responsibility:** The engine of content generation.
* **Input:** `Directive` and the relevant `File Entry` content.
* **Output:** A `Document Fragment`.

**Constraint:** **Must be deterministic.** Given the same input and file content, it must always produce the same string. It cannot perform its own IO.


## 4. Data & State Management

### **Context**

* **Responsibility:** The central hub for system-wide, read-only resources.
* **Contents:** `Plugin Registry`, `File Cache`, `Configuration`, and eventually the `Plan` and `Document`.

**Constraint:** Properties are set once during initialization and are thereafter immutable.

### **File Cache & File Entry**

* **Responsibility:** Centralized management of filesystem interaction to respect `Limits`.
* **Behavior:** * Loads file content into `File Entries`.
* Tracks "Sanitised Paths" (ensuring no access outside the Sandbox root).
* Provides status (e.g., `NOT_FOUND`, `CANT_READ`).

**Constraint:** If a file exceeds `Max File Size` or `Max Total Memory`, the cache must refuse to load it and flag a violation. The planner should take outcomes into account.

### **Document Structure & Fragment**

* **Responsibility:** Represents the final Markdown output as a series of pointers or strings.
* **Components:** * **Text Fragment:** A static string (usually original markdown).
* **Transformed Fragment:** The output of a `Transformer`.

* **Behavior:** Supports a "functional" assembly—joining fragments to create a new `Document` without mutating the previous state.


## 5. Security & Constraints (Limits)

The system must validate the following before execution:

* **Sandbox Root:** No `Source` or `Embedded` file may exist outside this directory.
* **Recursion Depth:** Prevents a file from embedding itself or creating infinite loops.
* **Resource Caps:** Max file sizes and total directive counts per document.


**Would you like me to generate a set of initial "Unit Test Contracts" based on this analysis to further guide the assistant?**
## **6. Component Catalog (by Layer)**

This section maps the functional components to their respective architectural layers. Cross-layer dependencies must follow the rules in `ARCHITECTURE.md`.

### **Layer: CLI**

* **CLI Parser**
* **Responsibility:** Entry point of the application. Handles argument validation and initial configuration loading.
* **Behavior:** Converts raw terminal input into a validated `Configuration` object.


* **User Interface (Console)**
* **Responsibility:** Handles all output to `stdout/stderr`.
* **Behavior:** Presents the `Plan` to the user and captures consent/confirmation before execution.



### **Layer: Application**

* **Orchestrator**
* **Responsibility:** High-level flow control (Init → Plan → Confirm → Execute).
* **Behavior:** Owns the `Context` and passes data between the `Planner` and the `Compiler`.


* **Plugin Registry**
* **Responsibility:** Catalog of available `Plugins`.
* **Behavior:** Matches a `Directive.type` to a specific `Plugin` implementation. Allows for querying for plugins against directive type with or without phase, eg give me all plugins with a 'source' property.



### **Layer: Plugins**

* **Plugin Framework**
* **Responsibility:** Configures and provides specific `Transformers`.

* **Transformers**
* **Responsibility:** Based class for executing the logic for embedding (e.g., "file-embedder", "symbol-extractor").
* **Input/Output:** Takes a `Directive` + `Source Content` → Returns a `Document Fragment`.

Note this defined the framework. The actual implementation of behavior sits in a separate module.

### **Layer: Parsing**

* **Directive Parser**
* **Responsibility:** Regex or state-machine logic to find `embedm` blocks in Markdown.


* **Symbol Parser**
* **Responsibility:** Language-specific logic (or regex) to find symbols/lines within a source file.



### **Layer: Domain**

* **Planner**
* **Responsibility:** Logic for building the dependency DAG.
* **Behavior:** Recursively creates `Plan Nodes` and validates them against `Limits`.

* **Plan / Plan Node**
* **Responsibility:** Immutable data objects representing the execution strategy.

* **Document / Document Fragment**
* **Responsibility:** Immutable data objects representing the content state.


### **Layer: Infrastructure**

* **File Cache**
* **Responsibility:** The only component permitted to perform Disk IO.
* **Behavior:** Reads files, enforces `Max File Size`, and manages the `Sandbox Root` security boundary.

* **Configuration Loader**
* **Responsibility:** Reads `embedm_config.yaml` and maps it to the domain `Configuration` object.


### **AI Assistant Guidance**

When implementing these components:

1. **Prioritize the File Cache:** All file reading must go through the cache; no `open()` calls should exist in the Planner or Plugins.
2. **Stateless Plugins:** Ensure that a Plugin doesn't "remember" anything from a previous transformation.
3. **Fragment Assembly:** Use a list of fragments to build the document rather than repeated string concatenation for better performance and immutability.
