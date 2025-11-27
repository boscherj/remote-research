# Model Context Protocol (MCP) Architecture

This overview of the Model Context Protocol (MCP) discusses its scope and core concepts, and provides examples demonstrating each core concept.

## Scope

The Model Context Protocol includes the following projects:

* **MCP Specification**: A specification that outlines the implementation requirements for clients and servers.
* **MCP SDKs**: SDKs for different programming languages that implement MCP.
* **MCP Development Tools**: Tools for developing MCP servers and clients, including the MCP Inspector.
* **MCP Reference Server Implementations**: Reference implementations of MCP servers.

## Concepts of MCP

### Participants

MCP follows a client-server architecture where an MCP host — an AI application like Claude Code or Claude Desktop — establishes connections to one or more MCP servers. The key participants are:

* **MCP Host**: The AI application that coordinates and manages one or multiple MCP clients
* **MCP Client**: A component that maintains a connection to an MCP server and obtains context for the MCP host to use
* **MCP Server**: A program that provides context to MCP clients

MCP servers can execute locally or remotely:
- **Local MCP Server**: Runs on the same machine (e.g., filesystem server using STDIO transport)
- **Remote MCP Server**: Runs on an external platform (e.g., Sentry MCP server using Streamable HTTP transport)

### Layers

MCP consists of two layers:

#### Data Layer
Defines the JSON-RPC based protocol for client-server communication, including:
* **Lifecycle management**: Connection initialization, capability negotiation, and termination
* **Server features**: Tools for AI actions, resources for context data, and prompts for interaction templates
* **Client features**: Sampling from host LLM, eliciting user input, and logging messages
* **Utility features**: Notifications for real-time updates and progress tracking

#### Transport Layer
Manages communication channels and authentication between clients and servers:
* **Stdio Transport**: Uses standard input/output streams for direct process communication
* **Streamable HTTP Transport**: Uses HTTP POST for client-to-server messages with optional Server-Sent Events for streaming

### Data Layer Protocol

The data layer defines the schema and semantics between MCP clients and MCP servers, using JSON-RPC 2.0 as its underlying protocol.

#### Primitives

MCP primitives define what clients and servers can offer each other:

**Server Primitives**:
* **Tools**: Executable functions that AI applications can invoke (e.g., file operations, API calls)
* **Resources**: Data sources that provide contextual information (e.g., file contents, database records)
* **Prompts**: Reusable templates for interactions with language models (e.g., system prompts, few-shot examples)

**Client Primitives**:
* **Sampling**: Allows servers to request language model completions from the client's AI application
* **Elicitation**: Allows servers to request additional information from users
* **Logging**: Enables servers to send log messages to clients

Each primitive type has associated methods for discovery (`*/list`), retrieval (`*/get`), and execution (e.g., `tools/call`).

#### Notifications

The protocol supports real-time notifications to enable dynamic updates between servers and clients, sent as JSON-RPC 2.0 notification messages without expecting a response.
