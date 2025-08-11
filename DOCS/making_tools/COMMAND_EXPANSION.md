# Command Expansion: The Forgotten Unix Power
## A Magic Launcher Addendum

### What Is Command Expansion?

Command expansion (`$()` or backticks) lets you use the output of one command as the input to another. It's not just piping - it's command composition.

```bash
# Pipe: Sequential processing
cat file | grep ERROR | wc -l

# Expansion: Nested composition  
echo "Found $(grep -c ERROR file) errors on $(date)"
```

### The Power Patterns

#### 1. Dynamic Parameters
```bash
# Use one tool's output as another's config
python3 server.py --port "$(python3 getport.py)"
python3 backup.py --name "backup-$(date +%s).tar"
python3 mlbuild.py --version "$(git describe --tags)"
```

#### 2. Multi-line Content Injection
```bash
# Send system status to MLSwarm
python3 mlswarm.py send "$(
    echo "=== System Report $(date) ==="
    echo "CPU: $(uptime)"
    echo "Memory: $(free -h | grep Mem)"
    echo "Disk: $(df -h /)"
    echo "Processes: $(ps aux | wc -l)"
)"

# Create a note with context
python3 mlsticky.py add "$(
    echo "Meeting Notes - $(date +%Y-%m-%d)"
    echo "------------------------"
    echo "Attendees: $(python3 mlteam.py list)"
    echo "Action items:"
    cat action_items.txt
)"
```

#### 3. Tool Orchestration
```bash
# ML tools calling ML tools
python3 mlreport.py create "$(
    python3 mlstats.py weekly "$(
        python3 mlgather.py --since "$(date -d 'last week' +%s)"
    )"
)"

# Conditional execution based on tool output
if [ "$(python3 mlcheck.py status)" = "ready" ]; then
    python3 mlprocess.py --data "$(python3 mlprepare.py)"
fi
```

#### 4. Template Expansion
```bash
# Generate config files
cat > config.ini << EOF
[server]
port = $(python3 mlconfig.py get port)
host = $(python3 mlconfig.py get host)
workers = $(nproc)
started = $(date --iso-8601)
EOF

# Create dynamic scripts
echo "#!/bin/bash
# Generated $(date)
export TOKEN='$(python3 mlauth.py token)'
export ENDPOINT='$(python3 mlconfig.py endpoint)'
$(python3 mlscript.py generate)
" > run.sh
```

### Designing for Expansion

#### Good Expansion Citizens

Tools that output single values or structured text:

```python
#!/usr/bin/env python3
"""MLToken - Designed for command expansion"""
import secrets
import sys

type = sys.argv[1] if len(sys.argv) > 1 else 'hex'

if type == 'hex':
    print(secrets.token_hex(16))
elif type == 'url':
    print(secrets.token_urlsafe(22))
elif type == 'pin':
    print(f"{secrets.randbelow(10000):04d}")
# Just the value, no decoration
```

Usage:
```bash
curl -H "Auth: $(python3 mltoken.py)" api.example.com
echo "PIN: $(python3 mltoken.py pin)" | mail user@example.com
```

#### Expansion Anti-patterns

Don't force expansion where it doesn't fit:

```bash
# BAD - Binary data breaks expansion
python3 process.py "$(cat image.jpg)"

# BAD - Huge files exceed shell limits  
python3 analyze.py "$(cat 1GB_log.txt)"

# BAD - Interactive tools don't expand
python3 mlchat.py "$(echo 'hello')"  # Why?
```

### Real World Examples

#### System Monitoring
```bash
# One-liner health check
python3 mlalert.py check "CPU:$(mpstat 1 1 | tail -1 | awk '{print $NF}')% MEM:$(free -m | awk '/^Mem/{print $3}')MB"
```

#### Git Integration
```bash
# Commit with generated message
git commit -m "$(python3 mlcommit.py generate "$(git diff --staged --stat)")"
```

#### Log Analysis
```bash
# Send alert if errors found
ERRORS="$(grep ERROR /var/log/app.log | tail -20)"
[ -n "$ERRORS" ] && python3 mlnotify.py "$(echo -e "Errors detected:\n$ERRORS")"
```

#### Database Operations
```bash
# Backup with timestamp
mysqldump mydb > "backup-$(python3 mltimestamp.py iso).sql"
```

### The Philosophy

**Command expansion turns every tool into a function.**

No imports. No linking. No dependencies. Just `$()`.

But like any powerful tool:
- Use it when it simplifies
- Skip it when it complicates  
- Design for it when appropriate
- Ignore it when not

### Best Practices

1. **Output only the result** - No progress bars, no "Done!" messages
2. **Exit cleanly** - Non-zero exits break expansion
3. **Handle missing args gracefully** - Provide sane defaults
4. **Consider multiline** - Sometimes that's the point
5. **Document expansion uses** - Show examples in your help text

### The Test

A good ML tool should work in three contexts:
```bash
# Direct execution
python3 mltool.py input.txt

# Pipe compatible
cat input.txt | python3 mltool.py

# Expansion ready (when appropriate)
python3 other.py --param "$(python3 mltool.py)"
```

### Examples of Judgment

**Tools perfect for expansion:**
- Config getters
- Token generators
- Timestamp formatters
- Status checkers
- Count/stat tools

**Tools that shouldn't expand:**
- Interactive CLIs
- File processors
- Binary handlers
- GUI tools
- Long-running processes

### The Bottom Line

Command expansion is not about replacing file I/O or pipes. It's about composition.

When you need a value from one tool as input to another, expansion is your friend. When you need to process data, pipes are better. When you need to handle files, just handle files.

**The revolution includes knowing which tool to use when.**

---

*Remember: `$()` is powerful magic. Use it wisely.*