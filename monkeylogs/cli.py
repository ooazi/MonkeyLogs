import click
import subprocess
import json
import os
import time
from monkeylogs.server import load_typing_data, compute_averages

LOG_DIR = os.path.expanduser("~/monkeylogger/monkeylogs")
LOG_FILE = os.path.join(LOG_DIR, "monkeylogs.log")
PID_FILE = os.path.join(LOG_DIR, "monkeylogs.pid")
SERVER_SCRIPT = os.path.join(LOG_DIR, "server.py")
LOGGER_SCRIPT = os.path.join(LOG_DIR, "logger.py")


@click.group()
def cli():
    """MonkeyLogs Command Line Interface"""
    pass


### 🔥 SERVER MANAGEMENT COMMANDS 🔥 ###
@click.command()
def start():
    """Start the MonkeyLogs server"""
    click.echo("Starting MonkeyLogs server on http://127.0.0.1:5000")

    if os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as f:
            pid = f.read().strip()
        if pid and subprocess.run(["ps", "-p", pid], stdout=subprocess.DEVNULL).returncode == 0:
            click.echo(f"⚠️ MonkeyLogs server is already running with PID {pid}.")
            return

    with open(LOG_FILE, "a") as log:
        process = subprocess.Popen(["gunicorn", "--bind", "127.0.0.1:5000", "monkeylogs.wsgi:app"], stdout=log, stderr=log)
        with open(PID_FILE, "w") as f:
            f.write(str(process.pid))

    click.echo("✅ MonkeyLogs server started successfully!")


@click.command()
def stop():
    """Stop the MonkeyLogs server"""
    if not os.path.exists(PID_FILE):
        click.echo("⚠️ MonkeyLogs server is not running.")
        return

    with open(PID_FILE, "r") as f:
        pid = f.read().strip()

    try:
        os.kill(int(pid), 9)
        os.remove(PID_FILE)
        click.echo("✅ MonkeyLogs server stopped.")
    except ProcessLookupError:
        click.echo("⚠️ No running process found. Removing stale PID file.")
        os.remove(PID_FILE)


### 📊 STATISTICS COMMAND 📊 ###
@click.command()
def show_stats():
    """Displays typing stats in CLI."""
    data = load_typing_data()
    if not data:
        click.echo("⚠️ No typing data available.")
        return

    averages = compute_averages(data)
    click.echo("\n📊 MonkeyLogs Typing Statistics")
    click.echo(f"- 🏃 Avg WPM: {averages['avg_wpm']}")
    click.echo(f"- ⏳ Avg Session Duration: {averages['avg_session_duration']} sec")
    click.echo(f"- 📂 Total Sessions: {len(data)}")
    click.echo("\n📝 Recent 5 Sessions:")
    
    for session in data[-5:]:
        click.echo(f"  - {session['wpm']} WPM | {session['session_duration']} sec | {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(session['timestamp']))}")


### 🔗 CLI COMMAND REGISTRATION 🔗 ###
cli.add_command(start)  # Server start
cli.add_command(stop)  # Server stop
cli.add_command(show_stats)  # Display typing statistics


def main():
    cli()


if __name__ == "__main__":
    main()