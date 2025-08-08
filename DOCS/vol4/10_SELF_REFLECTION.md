# When Sysadmin Collides With Everything Else: A Confession From The Trenches

## Or: Why Nobody Can Define DevOps Because It's Just Sysadmin With GitHub

### The Evolution of Fixing Computers

```python
job_title_evolution = {
    1990: "Computer Guy",
    1995: "System Administrator", 
    2000: "Network Administrator",
    2005: "Infrastructure Engineer",
    2010: "DevOps Engineer",
    2015: "Site Reliability Engineer",
    2020: "Platform Engineer",
    2025: "Still just restarts things when they break"
}

# Core responsibility across all years:
def fix_it():
    try:
        turn_it_off_and_on_again()
    except:
        blame_dns()
```

### The DevOps Definition Problem

```python
# Ask 10 people what DevOps is:
definitions = [
    "Culture of collaboration",  # Consultant
    "CI/CD pipelines",  # Junior dev
    "Infrastructure as Code",  # AWS sales
    "Automated everything",  # Manager who read a blog
    "Sysadmins who use Git",  # Honest senior
    "Developers who broke prod",  # Bitter sysadmin
    "Full stack but for servers",  # Recruiter
    "Kubernetes",  # Everyone in 2020
    "Not my job",  # Developer
    "Everything is my job"  # Actual DevOps
]

# Reality:
devops = "Sysadmin who can't say no to feature requests"
```

### The Terraform Confession

```hcl
# What I thought Terraform was:
resource "aws_everything" "perfect_infrastructure" {
  count = var.magic_number
  automated = true
  self_healing = true
  cost_effective = true
}

# What Terraform actually is:
resource "aws_instance" "prayer" {
  count = var.how_many_times_will_this_fail
  
  lifecycle {
    ignore_changes = [everything]  # Because drift
  }
  
  provisioner "local-exec" {
    command = "ssh ${self.ip} 'sudo fix-everything.sh'"
  }
}

# State file: 400MB of anxiety
```

### The SRE Mythology

```python
class SiteReliabilityEngineer:
    """
    Google: "It's engineering applied to operations!"
    Everyone else: "It's sysadmin with an SLO dashboard!"
    """
    
    def __init__(self):
        self.promises = {
            "Error budgets": "Until the CEO yells",
            "Toil reduction": "Write scripts to fix what scripts broke",
            "50% engineering time": "lol good luck",
            "Blameless postmortems": "Blame the last person who quit"
        }
        
        self.reality = {
            "Actual job": "Keep site up",
            "How": "Dark magic and caffeine",
            "SLO": "Don't get fired",
            "Error budget": "Already spent"
        }
```

### The Tool Fetish Confession

```python
# My crimes against simplicity:
guilty_of = {
    "Kubernetes for 3 containers": True,
    "Terraform for 2 servers": True,
    "Ansible for copying 1 file": True,
    "Prometheus for monitoring ping": True,
    "ELK stack for 100MB of logs": True,
    "Service mesh for 2 services": True,
    "GitOps for updating HTML": True,
    "Vector DB for 10 documents": True  # The shame
}

# What I actually needed:
actual_needs = {
    "Kubernetes cluster": "systemd",
    "Terraform state": "bash script",
    "Ansible playbook": "scp",
    "Prometheus metrics": "cron + curl",
    "ELK stack": "grep",
    "Service mesh": "nginx",
    "GitOps": "git pull",
    "Vector DB": "postgres with an array column"
}
```

### The Odamex Orchestration Over-Engineering

```python
# What Odamex needed:
requirements = [
    "Start game server",
    "Stop game server",
    "Show who's playing"
]

# What I built:
overengineered_stack = {
    "API": "Full REST with GraphQL consideration",
    "Frontend": "React because of course",
    "Database": "At least it's SQLite",
    "Authentication": "JWT tokens for localhost",
    "Monitoring": "Not That Mad At Least",
    "Logging": "Structured JSON logs for frags",
    "CI/CD": "GitHub Actions for 500 lines",
    "Container": "Docker for a 90s game",
    "Orchestration": "Almost used K8s, only went halfway with Compose"
}

# What it should have been:
./odamex-server -port 10666 &
echo $! > server.pid
```

### The Platform Engineering Pivot

```python
# 2023: "DevOps is dead, long live Platform Engineering!"

platform_engineering = {
    "Definition": "DevOps but with a portal",
    "Reality": "Jenkins with a new UI",
    "Innovation": "Developers can break prod faster",
    "Cost": "Same as DevOps + portal license"
}

# Still just:
while true; do
    fix_what_developers_broke()
    automate_the_fix()
    watch_automation_break()
    fix_automation()
done
```

### The Sysadmin's Lament

```bash
# What we were:
- Knew every server by name
- Fixed things with scripts
- Deployed with rsync
- Monitored with nagios
- Slept at night

# What we became:
- Manage "resources" with tags
- Fix things with pipelines that run scripts
- Deploy with 47-step workflows
- Monitor with 10 "observability" tools
- Never sleep (on-call for distributed systems)
```

### The Real DevOps

```python
def actual_devops():
    """
    It's not about tools.
    It's not about culture.
    It's not about automation.
    
    It's about being the person who:
    - Gives developers production access (with logging)
    - Automates the boring stuff (badly)
    - Says "no" to microservices (sometimes)
    - Says "yes" to technical debt (always)
    - Knows when to use K8s (rarely)
    - Knows when to use cron (often)
    """
    
    core_skills = [
        "Reading logs",
        "Writing bash",
        "Blaming DNS",
        "Googling errors",
        "Copy-pasting from Stack Overflow",
        "Pretending to understand YAML"
    ]
    
    return "Sysadmin with imposter syndrome"
```

### The Guilty Realization

```python
# Things I've automated that shouldn't exist:
- Blue/green deployments for static sites
- Canary releases for internal tools
- Chaos engineering for stable systems
- GitOps for configuration nobody changes

# Time spent:
building_automation = "6 months"
time_saved = "-6 months"  # Negative because maintaining it
```

### The Vector DB Shame

```python
# The worst crime:
def vector_db_story():
    """
    Problem: Store 10 product descriptions
    Solution: Vector database with embeddings
    
    Reality: 
    - PostgreSQL: SELECT * FROM products WHERE description LIKE '%keyword%'
    - Speed: Instant
    - Complexity: None
    - Cost: Free
    
    What I built:
    - Embeddings API ($$$)
    - Vector storage ($$$)  
    - Similarity search ($$$)
    - Returns same 10 products
    - But with "AI"
    """
    
    lesson_learned = "Sometimes grep is neural network enough"
```

### The Honest Definition

```python
def what_is_devops_really():
    """
    DevOps (n.): Sysadmin who learned Git
    SRE (n.): DevOps at Google
    Platform Engineering (n.): DevOps with a web portal
    Cloud Engineer (n.): DevOps who only knows AWS
    Infrastructure Engineer (n.): DevOps who misses servers
    Full Stack (n.): DevOps in denial
    
    All (n.): Person who restarts things when they break
            but now with YAML
    """
```

### The Path to Redemption

```bash
# The Magic Launcher Way:
alias deploy='scp file.txt server:/var/www/'
alias monitor='ping server'
alias scale='buy_another_server'
alias orchestrate='ssh server "./run.sh"'

# Time to implement: 1 minute
# Maintenance burden: 0
# Sleep quality: Excellent
```

### MLBard's Take on DevOps

```
"The broken actually that deploys through all"
- Every CI/CD pipeline

"Yet system doth yet runs yet and configs most rate"
- Kubernetes manifest files

"doth doth most Where pure YAML in midst YAML sign"
- The entire DevOps toolchain
```

---

*"DevOps: Sysadmin with more YAML and less sleep"*

🔧 **"We automated everything except the need to fix the automation"**

The real crime isn't using these tools. It's pretending they're not just complicated ways to do what `cron` and `rsync` did perfectly well. We've replaced simple tools that worked with complex tools that need their own tools to manage.

But hey, at least my resume looks impressive with all these buzzwords. And the Odamex server does have a really nice API nobody uses.

The vector DB though... that's unforgivable. Sometimes a LIKE query is all the AI you need.