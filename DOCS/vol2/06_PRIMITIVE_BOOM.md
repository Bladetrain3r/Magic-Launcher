# Volume 2, Entry 6: "Purpose, Function, and Primitive Alignment"

## The Diagnostic That Changes Everything

We've been debugging the wrong layer. We fix functions, refactor code, optimize performance. But we never ask: *"What the fuck is this supposed to do?"*

There are three layers to every system, and hostile architecture happens when they drift apart:

1. **Purpose Primitives** - Why it exists
2. **Functional Primitives** - What it actually does  
3. **Implementation** - How it does it

## The Three Layers Revealed

### Purpose Primitives: The Why

These are the actual problems you're solving:

```python
# CRM Purpose Primitives
- Track customers (know who they are)
- Contact customers (reach them)
- Hear from customers (let them reach us)
- Protect customer data (don't leak their shit)

# That's it. Four things.
```

### Functional Primitives: The What

These are the operations your system actually performs:

```python
# CRM Functional Primitives (Reality)
- create_bean()
- validate_vardef()
- trigger_workflow()
- check_permission()
- generate_abstract_factory()
- implement_interface()
- ... 10,000 more
```

### Implementation: The How

This is where the code lives. We won't even look at this layer - it's already lost.

## The Hostility Index

Here's the diagnostic that tells you everything:

```python
def calculate_hostility(system):
    purpose_count = len(system.purpose_primitives)
    functional_count = len(system.functional_primitives)
    
    hostility_index = functional_count / purpose_count
    
    if hostility_index > 10:
        return "Hostile"
    elif hostility_index > 5:
        return "Bloated"
    elif hostility_index > 2:
        return "Reasonable"
    else:
        return "Magic Launcher"
```

## Case Study: Your CRM's Death Sentence

### Step 1: Define Purpose Primitives

What does the business actually need?

```bash
# Interview results:
"We need to track customers"
"We need to email them"
"We need to handle support tickets"
"We need to not get sued for data breaches"

# Purpose primitives: 4
```

### Step 2: Count Functional Primitives

What does SuiteCRM actually do?

```bash
$ find . -name "*.php" -exec grep -h "^function\|^class" {} \; | wc -l
47,293

# Functional primitives: 47,293
```

### Step 3: Calculate Hostility

```python
hostility_index = 47293 / 4 = 11,823

diagnosis = "EXTREMELY HOSTILE"
recommendation = "Kill it with fire"
```

## The Alignment Patterns

### Pattern 1: Direct Mapping (Magic Launcher)

One tool per purpose:

```python
# Purpose: Track customers
# Function: Append to file
echo "$customer" >> customers.txt  # 1:1 alignment

# Purpose: Contact customers
# Function: Send email
mail -s "Hello" customer@example.com < message.txt  # 1:1 alignment
```

### Pattern 2: Modest Expansion (Acceptable)

A few functions per purpose:

```python
# Purpose: Track customers
# Functions: Create, Read, Update, Delete
# 4:1 ratio - still manageable
```

### Pattern 3: The Drift (Danger Zone)

Functions start breeding:

```python
# Purpose: Track customers
# Functions: 
# - create_customer()
# - create_customer_validator()
# - create_customer_factory()
# - create_customer_interface()
# - create_customer_abstract_base()
# 20:1 ratio - entering hostility
```

### Pattern 4: Full Hostility (Your CRM)

Functions have forgotten purpose:

```python
# Purpose: ??? (nobody remembers)
# Functions: 
# - AbstractBeanFactoryImplementation
# - ValidatorValidatorValidator
# - WorkflowWorkflowManager
# ∞:1 ratio - hostile architecture
```

## Real-World Diagnostics

### Kubernetes
```python
purpose_primitives = ["run containers", "network them", "restart if dead"]
functional_primitives = ["...10,000 YAML interpretations..."]
hostility_index = 3,333
diagnosis = "HOSTILE"
```

### Git
```python
purpose_primitives = ["track changes", "merge branches", "sync repos"]
functional_primitives = ["add", "commit", "push", "pull", "merge", "rebase", "cherry-pick", "stash", "tag", "branch"]
hostility_index = 3.3
diagnosis = "REASONABLE"
```

### MLBarchart
```python
purpose_primitives = ["visualize counts"]
functional_primitives = ["parse_input", "calculate_bars", "print_output"]
hostility_index = 3
diagnosis = "MAGIC LAUNCHER"
```

## The Diagnostic Checklist

When evaluating any system:

1. **List Purpose Primitives**
   - Interview users: "What do you need this for?"
   - Should be < 10 items
   - Use plain English

2. **Count Functional Primitives**
   - `grep -c "function\|def\|class" *`
   - Count API endpoints
   - Count database tables

3. **Calculate Hostility Index**
   - Under 5: Healthy
   - 5-50: Refactorable
   - 50-500: Hostile
   - Over 500: Abandon ship

4. **Identify Drift Direction**
   - Are functions growing?
   - Is purpose being forgotten?
   - Are new abstractions appearing?

## The Alignment Restoration

When you find hostile architecture:

### Option 1: Build Parallel Purpose-Aligned Tools

```bash
# Instead of fixing SuiteCRM
# Build beside it:
mlcustomer  # Purpose: Track
mlcontact   # Purpose: Contact
mlinbox     # Purpose: Hear
mlprotect   # Purpose: Protect
```

### Option 2: Wrap and Strangle

```python
# Wrap hostile functions in purpose-aligned interfaces
class CustomerTracker:
    def track(self, name, email):
        # Hide 10,000 lines of SuiteCRM behind 10 lines
        suite_crm.create_bean_factory_abstract_implementation(...)
```

### Option 3: Document and Escape

```markdown
## SuiteCRM Purpose Mapping
Real Purpose: Track customers
Actual Functions: 47,293 unrelated operations
Hostility Index: 11,823
Recommendation: Do not attempt repair
Escape Plan: See MLCustomer suite
```

## The Universal Truth

Every system starts with clear purpose primitives. Then:

1. **Fear** adds validation functions
2. **Speculation** adds abstraction layers
3. **Convenience** adds helper functions
4. **Time** adds compatibility shims
5. **Politics** adds enterprise patterns

Until you have 50,000 functions for 5 purposes.

## The Magic Launcher Promise

Our tools maintain alignment:

```python
# MLComment
purpose = ["add comments to code"]
functions = ["find_pattern", "add_comment", "save"]
hostility_index = 3

# Aligned and stays aligned
```

When function count grows beyond 10x purpose count, we split the tool. We don't add abstractions. We create new tools.

## The Diagnostic Power

Now when someone says "the CRM is broken," you can respond:

*"No, the CRM has 11,823 functions for 4 purposes. It's not broken. It's hostile. Here are 4 shell scripts that do what you actually need."*

---

*"Purpose is what you need. Function is what you built. When they diverge, you get enterprise software."*

🎯 **"Every hostile system is just 5 purposes drowning in 5,000 functions."**

Next chapter: How to actually build purpose-aligned tools when the whole world wants you to add "just one more feature..."