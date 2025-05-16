import os
from getpass import getpass

import keyring
from rich.console import Console
from rich.prompt import Prompt
from pyfiglet import Figlet

console = Console()

ENV_FILE = '.env'

def print_title():
    f = Figlet(font='slant')
    ascii_art = f.renderText('Commvault \nMCP Server')
    console.print(f"[bold][red]{ascii_art}[/red][/bold]")

def load_env():
    env_vars = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env_vars[k.strip()] = v.strip()
    return env_vars

def save_env(env_vars):
    with open(ENV_FILE, 'w') as f:
        for k, v in env_vars.items():
            f.write(f"{k}={v}\n")

def prompt_update_env(env_vars):
    keys = ['CC_SERVER_URL', 'MCP_TRANSPORT_MODE', 'MCP_HOST', 'MCP_PORT', 'MCP_PATH', ]
    console.print("\n[bold underline]Environment Variables[/bold underline]")
    console.print("Press Enter to keep the current value (shown in brackets).\n")
    for key in keys:
        current_val = env_vars.get(key, '')
        if key == 'MCP_TRANSPORT_MODE':
            val = Prompt.ask(key, choices=['streamable-http', 'stdio', 'sse'], default=current_val if current_val else 'streamable-http')
            if val == 'stdio':
                env_vars[key] = val
                break # other variables are not needed for stdio mode
        elif key == 'MCP_PATH':
            val = Prompt.ask(key, default=current_val if current_val else '/mcp')
        else:
            val = Prompt.ask(key, default=current_val)
        env_vars[key] = val

    return env_vars

def prompt_and_save_keyring(service_name, key_names):
    console.print(f"\n[bold underline]Secure Tokens (stored in OS keyring)[/bold underline]")
    console.print("Leave blank to keep the existing secret.\n")
    for key in key_names:
        current = keyring.get_password(service_name, key)
        display_val = "<hidden>" if current else "none"
        prompt_text = f"Enter {key} [{display_val}]"
        val = getpass(prompt_text + ": ")
        if val:
            keyring.set_password(service_name, key, val)
            console.print(f"[green]{key} updated.[/green]")
        else:
            console.print(f"[yellow]{key} unchanged.[/yellow]")

def main():
    console.clear()
    print_title()

    env_vars = load_env()
    env_vars = prompt_update_env(env_vars)
    save_env(env_vars)
    console.print(f"\n[green]Updated {ENV_FILE} file.[/green]")

    service_name = 'commvault-mcp-server'
    secret_keys = ['access_token', 'refresh_token', 'server_secret']
    prompt_and_save_keyring(service_name, secret_keys)

    console.print("\n[bold green]Setup complete! You can now run the MCP server (uv run src/server.py)[/bold green]")

if __name__ == '__main__':
    main()
