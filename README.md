Quadton Coding Agent

A lightweight, terminal-based AI coding agent built with Python.

Quadton Coding Agent is designed around a reusable agent engine that is completely separate from the terminal interface. This allows the same core engine to later power a web dashboard, API, or other interfaces without rewriting the agent itself.

Features

Current

* Interactive terminal REPL
* One-shot commands
* OpenRouter provider support
* Configurable AI model
* Centralized configuration
* Environment-variable API key management
* Clean terminal output using Rich
* Modular provider architecture

Planned

* SQLite conversation history
* Session management and resume
* Long-term memory
* File reading, writing, editing, and diff previews
* Code execution and testing
* Shell command execution with confirmations
* Web search and research
* Multi-provider support
* Token-by-token streaming
* Token and cost tracking
* Checkpoints and undo
* FastAPI/WebSocket dashboard

Architecture

The project separates the agent’s core logic from the user interface.

                    ┌─────────────────┐
                    │      CLI        │
                    │  Terminal UI    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Agent Engine   │
                    │                 │
                    │ Conversation    │
                    │ Agentic Loop    │
                    │ Tool Handling    │
                    │ Provider Calls  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       ┌────────────┐ ┌────────────┐ ┌────────────┐
       │ Providers  │ │   Memory   │ │   Tools    │
       └────────────┘ └────────────┘ └────────────┘

The CLI is only an interface. Core functionality should remain independent of terminal-specific code.

Project Structure

quadton-coding-agent/
│
├── agent/
│   ├── __init__.py
│   ├── __main__.py
│   ├── config.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   │
│   │   └── providers/
│   │       ├── __init__.py
│   │       ├── base.py
│   │       └── openrouter_provider.py
│   │
│   └── cli/
│       ├── __init__.py
│       └── main.py
│
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md

Requirements

* Python 3.11+
* An OpenRouter API key
* Internet connection

Installation

Clone the repository:

git clone <your-repository-url>
cd quadton-coding-agent

Create a virtual environment:

Windows

python -m venv .venv
.venv\Scripts\activate

Linux / macOS

python3 -m venv .venv
source .venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Configuration

Create a .env file in the project root.

Use .env.example as the template:

OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=your_model

Never commit your .env file.

It is intentionally excluded through .gitignore.

Running

Run the agent with:

python -m agent

For one-shot mode:

python -m agent "Explain this Python function"

Configuration Philosophy

Configuration is centralized rather than scattered throughout the project.

Provider and model selection should come from configuration, environment variables, or CLI arguments rather than being hardcoded into the engine.

For example:

Provider
   ↓
OpenRouter
   ↓
Configured Model

This makes switching providers and models easier as the project grows.

Development Roadmap

Stage 1 — Provider + CLI

* [x]	Project structure
* [ ]	Provider interface
* [ ]	OpenRouter provider
* [ ]	Basic agent engine
* [ ]	Interactive REPL
* [ ]	One-shot mode
* [ ]	Configuration system

Stage 2 — Memory + Sessions

* [ ]	SQLite database
* [ ]	Conversation history
* [ ]	Session IDs
* [ ]	Session listing
* [ ]	Resume sessions
* [ ]	Long-term memory
* [ ]	/new
* [ ]	/history
* [ ]	/sessions
* [ ]	/resume
* [ ]	/switch-provider
* [ ]	/help
* [ ]	/exit

Stage 3 — Tools

* [ ]	Tool interface
* [ ]	Tool registry
* [ ]	File operations
* [ ]	File diff previews
* [ ]	Code execution
* [ ]	Shell commands
* [ ]	Destructive-command confirmation
* [ ]	Web search
* [ ]	Multi-step tool calling

Stage 4 — Advanced Agent

* [ ]	Streaming
* [ ]	Token usage
* [ ]	Cost tracking
* [ ]	Checkpoints
* [ ]	Undo
* [ ]	Improved error handling

Stage 5 — Additional Providers

* [ ]	Anthropic
* [ ]	OpenAI
* [ ]	Additional providers

Stage 6 — Web Dashboard

* [ ]	FastAPI backend
* [ ]	WebSocket support
* [ ]	Web interface
* [ ]	Reuse the existing agent engine
* [ ]	Live agent/tool execution updates

Security

The agent will eventually be capable of reading files, modifying code, and executing commands.

Security is therefore treated as a core architectural concern.

Planned protections include:

* Working-directory restrictions
* Path traversal protection
* Confirmation before destructive operations
* File diffs before modifications
* Subprocess timeouts
* Controlled command execution
* API keys kept outside source code
* .env excluded from Git
* Sensitive information excluded from tool output where possible

Contributing

Contributions and improvements are welcome.

When adding functionality, maintain the separation between the core engine and interfaces.

Provider implementations should follow the common provider interface, while tools should follow the common tool interface.

License

License information will be added as the project develops.
