# Connect the checker to Claude Desktop, Claude Code, Cursor, and VS Code

The checker is a **local stdio MCP server**, launched by `mcc-mcp`. It reads
the app folders you allow; it does **not** require a hosted MCP endpoint.

## Before configuring an AI client

With Python 3.10+ and [pipx](https://pipx.pypa.io/) installed:

```bash
pipx install "git+https://github.com/HPIS-Holdings/app-store-compliance-checker.git@v0.4.0#subdirectory=mcp/server"
mcc snapshot
```

From a local clone of this repository you can instead run `pipx install ./mcp/server`.

One install provides `mcc` (CLI) and `mcc-mcp` (MCP server), including the
bundled policy rules. The ordinary pip alternative, inside your chosen Python
environment, is `python -m pip install "git+https://github.com/HPIS-Holdings/app-store-compliance-checker.git@v0.4.0#subdirectory=mcp/server"`. To run without a permanent
installation, use `uvx --from "git+https://github.com/HPIS-Holdings/app-store-compliance-checker.git@v0.4.0#subdirectory=mcp/server" mcc-mcp` (requires
[uv](https://docs.astral.sh/uv/)). No GitHub account or token is needed.

**Replace these two example values** in the configurations below:

- `/absolute/path/to/mcc-mcp`: the executable returned by
  `command -v mcc-mcp` (macOS/Linux) or `where.exe mcc-mcp` (Windows).
  If the executable is not found, check your pipx installation and PATH.
  GUI applications often have a different PATH than a terminal, so the
  **full executable path** is safer than just `mcc-mcp`.
- `/absolute/path/to/your/app`: the **existing, absolute folder** containing
  the app you want to check, not the checker repository.

On Windows, use forward slashes in JSON paths (for example,
`C:/Users/you/your-app`) or escape every backslash as `\\`.
Use the **actual** executable path printed by `where.exe mcc-mcp`; don't
guess the installation directory. The executable normally ends in
`mcc-mcp.exe`. Do **not** paste a Unix executable path into a Windows config.

`COMPLIANCE_ALLOWED_ROOTS` restricts which projects the checker may inspect.
Use the smallest app folder needed; setting it to a parent folder grants access
to all of that parent's subfolders. If needed, multiple roots are separated
by the platform's path separator (colon on macOS/Linux, semicolon on Windows).
Some clients
may synchronize settings across your devices or account; check your own sync
and privacy settings. The checker itself reads files locally, but an AI client
may send tool responses (including selected file evidence) to its model
service. Do not commit personal absolute paths or credentials to a shared
project.

## Claude Desktop

**File:** `claude_desktop_config.json`. Open Claude Desktop's
**Settings > Developer > Edit Config**. The usual locations are
`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS,
and `%APPDATA%\Claude\claude_desktop_config.json` on Windows.

Paste this JSON (or add only the `store-compliance` entry under an existing
`mcpServers` object so you do not erase other connections):

```json
{
  "mcpServers": {
    "store-compliance": {
      "command": "/absolute/path/to/mcc-mcp",
      "args": [],
      "env": {
        "COMPLIANCE_ALLOWED_ROOTS": "/absolute/path/to/your/app"
      }
    }
  }
}
```

Save, **fully quit and restart Claude Desktop**, then open its connectors/tools
menu to confirm `store-compliance` is available. If it fails, check the
Claude Desktop MCP logs and the executable's full path.

Official format and restart instructions:
[Model Context Protocol: Connect to local servers](https://modelcontextprotocol.io/docs/2026-07-28/develop/connect-local-servers).

## Claude Code

**Recommended for one app:** open a terminal **inside the app project**, then
run this command after replacing both paths:

```bash
claude mcp add --scope local --env "COMPLIANCE_ALLOWED_ROOTS=/absolute/path/to/your/app" --transport stdio store-compliance -- "/absolute/path/to/mcc-mcp"
```

The `--` is required: it separates Claude Code's options from the executable.
The quotes around both path-bearing arguments matter if your app folder or
pipx executable path contains spaces. On Windows, run the equivalent command
with your **real Windows paths** and the `mcc-mcp.exe` executable.
`--scope local` applies to this app project only and does not commit any
config. To use the server in **every** project, change `--scope local` to
`--scope user` (then explicitly choose the folders it may access).

Check the connection with:

```bash
claude mcp list
claude mcp get store-compliance
```

Inside Claude Code, `/mcp` shows connection details.

**Alternative project config:** create `<app-root>/.mcp.json` with this JSON
instead of running `claude mcp add`:

```json
{
  "mcpServers": {
    "store-compliance": {
      "type": "stdio",
      "command": "/absolute/path/to/mcc-mcp",
      "args": [],
      "env": {
        "COMPLIANCE_ALLOWED_ROOTS": "/absolute/path/to/your/app"
      }
    }
  }
}
```

Claude Code prompts you to approve project MCP servers. This file uses
the same portable format as VS Code's workspace `.mcp.json`. Do **not**
commit machine-specific absolute paths to a shared repository unless your
team has deliberately standardized them; each user must adapt the paths.

Official instructions:
[Claude Code MCP: local stdio, CLI flags, scopes and project configuration](https://code.claude.com/docs/en/mcp).

## Cursor

**Global file:** `~/.cursor/mcp.json` (every project), or
**project file:** `<app-root>/.cursor/mcp.json` (only that project).
Create the folder if necessary. In **either** file, paste:

```json
{
  "mcpServers": {
    "store-compliance": {
      "type": "stdio",
      "command": "/absolute/path/to/mcc-mcp",
      "args": [],
      "env": {
        "COMPLIANCE_ALLOWED_ROOTS": "/absolute/path/to/your/app"
      }
    }
  }
}
```

Do not replace other existing server entries when editing an existing file.
Open Cursor's **Customize > MCP** panel and check that the server and its tools load;
if not, review the full executable path and restart/reload Cursor.

Official format and file locations:
[Cursor MCP documentation](https://cursor.com/docs/mcp).

## VS Code / GitHub Copilot

**Preferred current workspace format:** create `<app-root>/.mcp.json`, using
the portable `mcpServers` format. This can also be used by Claude Code:

```json
{
  "mcpServers": {
    "store-compliance": {
      "type": "stdio",
      "command": "/absolute/path/to/mcc-mcp",
      "args": [],
      "env": {
        "COMPLIANCE_ALLOWED_ROOTS": "/absolute/path/to/your/app"
      }
    }
  }
}
```

**Alternative VS Code-specific format:** if you already use
`<app-root>/.vscode/mcp.json`, keep using it with the distinct top-level
`servers` key. In this **VS Code-specific** file, `${workspaceFolder}`
resolves to your open app workspace folder:

```json
{
  "servers": {
    "store-compliance": {
      "type": "stdio",
      "command": "/absolute/path/to/mcc-mcp",
      "args": [],
      "env": {
        "COMPLIANCE_ALLOWED_ROOTS": "${workspaceFolder}"
      }
    }
  }
}
```

**Choose one VS Code configuration location**, rather than declaring the same
server in both files. VS Code's current documentation recommends the portable
`.mcp.json` for new setups; `.vscode/mcp.json` remains supported. In VS Code,
open the Command Palette and run **MCP: List Servers** to start/check the
server, then enable the available tools in chat. **Workspace Trust** must be
enabled for workspace MCP configuration; VS Code blocks these servers in
Restricted Mode. Inspect any project MCP configuration before trusting it
because these servers run local commands. If working in Remote/WSL/Dev
Containers, the executable must exist in the environment where the MCP
server actually runs.

Official instructions:
[VS Code: Add and manage MCP servers](https://code.visualstudio.com/docs/agent-customization/mcp-servers)
and [MCP configuration reference](https://code.visualstudio.com/docs/agents/reference/mcp-configuration).

## Quick check and troubleshooting

Run `mcc snapshot` in a terminal first; that checks the installation and
bundled rules, but **does not** prove that your AI client has connected.
After you configure a client, confirm that the `snapshot_info` tool works
through that client. It should report the policy snapshot and rule count.
To check an app, call `check_project` with
`project_path` set to the actual absolute app folder.

If the client says the program was not found, replace `command` with the
full executable path. If the app path or executable contains spaces, keep
the surrounding shell quotes for the Claude Code command (JSON values are
already quoted). If it says the project is outside the allowed roots,
correct `COMPLIANCE_ALLOWED_ROOTS` to match the app folder. The checker is
local and reads project files; its findings are not a guarantee of store
approval. It requires a compatible **local** MCP client; a browser-only chat
cannot launch your computer's `mcc-mcp` automatically.

## Any agent (skill folder)

Copy [the portable skill](../skill/store-compliance/) into the agent's skill
folder (for example `~/.claude/skills/` or `.claude/skills/`). The skill
describes how to use the CLI or MCP tools; it does not install a server.

## GitHub Actions (separate packaging piece)

The repository root contains a composite action (`action.yml`). See the
[example workflow](example-workflow.yml). This is **not** needed to connect
Claude, Cursor or VS Code. A `fail-on-review`
flag is **not supported**: the proof-only checker fails a job only for proven
problems.
