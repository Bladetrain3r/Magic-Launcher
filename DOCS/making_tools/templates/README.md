## Quick Start Template

Building a new tool? Start here:

1. Copy the template
2. Replace `run()` with your logic
3. Adjust argument parser if needed
4. Ship it

The template handles:
- File/stdin/stdout automatically
- Optional GUI with --gui flag
- Proper error handling
- UTF-8 everywhere
- CGA color scheme

Don't overthink. Most tools are just:
INPUT → TRANSFORM → OUTPUT

The template does INPUT and OUTPUT. You do TRANSFORM.

### Sample Usage
```bash
# CLI, stdin default
echo "hello" | python app.py
python app.py input.txt > out.txt

# Named output + quiet
python app.py input.txt -o out.txt -q

# Minimal GUI view of the result (Esc to quit)
python app.py input.txt --gui --title "My ML Tool"
```

### HTML Template Guide
```javascript
// Replace the processData() function with your tool:

// Text transformer
function processData() {
    const text = input.value;
    const result = text.split('\n').reverse().join('\n');
    output.textContent = result;
}

// JSON formatter
function processData() {
    try {
        const obj = JSON.parse(input.value);
        output.textContent = JSON.stringify(obj, null, 2);
    } catch(e) {
        setStatus('Invalid JSON', 'error');
    }
}

// Base64 encoder
function processData() {
    const text = input.value;
    output.textContent = btoa(text);
}
```