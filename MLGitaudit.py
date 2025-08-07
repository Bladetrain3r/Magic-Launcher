#!/usr/bin/env python3
"""
MLGitAudit - The Codebase Accountant
Counts commit intent to reveal where time actually goes
Proves hostile architecture with data
"""

import json
import sys
import re
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class MLGitAudit:
    def __init__(self):
        self.config_dir = Path.home() / '.config' / 'mlgitaudit'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.keywords_file = self.config_dir / 'keywords.json'
        
        # Load or create default keywords
        self.keywords = self.load_keywords()
        
        # Stats tracking
        self.counts = defaultdict(int)
        self.total_commits = 0
        self.uncategorized = []
        
    def load_keywords(self):
        """Load keyword configuration or create defaults"""
        if self.keywords_file.exists():
            with open(self.keywords_file, 'r') as f:
                return json.load(f)
        else:
            # Default keywords that reveal hostile architecture
            default_keywords = {
                "fix": ["fix", "bug", "defect", "resolve", "patch", "hotfix", 
                        "issue", "broken", "error", "crash", "fault"],
                "feature": ["feat", "add", "new", "implement", "feature", 
                           "enhance", "create", "introduce", "modules"],
                "refactor": ["refactor", "clean", "improve", "optimize", 
                            "restructure", "reorganize", "simplify", "bump"],
                "chore": ["chore", "docs", "build", "ci", "test", "config",
                         "deps", "update", "bump", "merge", "formatting"],
                "revert": ["revert", "rollback", "undo"],
                "workaround": ["workaround", "hack", "temp", "temporary", 
                              "quick fix", "bandaid", "kludge"],
                "swearwords": ["fuck", "shit", "damn", "bitch", "asshole", 
                               "kak", "crap", "bollocks", "bollok",]
            }



            # Save defaults
            with open(self.keywords_file, 'w') as f:
                json.dump(default_keywords, f, indent=2)
            
            return default_keywords
    
    def categorize_commit(self, message):
        """Categorize a commit message based on keywords"""
        message_lower = message.lower()
        
        # Check each category
        for category, keywords in self.keywords.items():
            for keyword in keywords:
                # Match keyword at word boundaries to avoid false positives
                if re.search(r'\b' + re.escape(keyword) + r'\b', message_lower):
                    self.counts[category] += 1
                    return category
        
        # Track uncategorized for analysis
        self.uncategorized.append(message)
        self.counts["uncategorized"] += 1
        return "uncategorized"
    
    def process_log(self, log_input):
        """Process git log input line by line"""
        for line in log_input:
            line = line.strip()
            if not line:
                continue
                
            self.total_commits += 1
            
            # Handle different git log formats
            # Default: hash message
            # --oneline: hash message
            # Just take everything after first space
            parts = line.split(' ', 1)
            if len(parts) > 1:
                message = parts[1]
            else:
                message = line
                
            self.categorize_commit(message)
    
    def calculate_percentages(self):
        """Calculate percentage breakdown"""
        if self.total_commits == 0:
            return {}
            
        percentages = {}
        for category, count in self.counts.items():
            percentages[category] = (count / self.total_commits) * 100
            
        return percentages
    
    def get_hostile_score(self):
        """Calculate a 'hostile architecture score' based on fix/feature ratio"""
        fixes = self.counts.get("fix", 0) + self.counts.get("workaround", 0)
        features = self.counts.get("feature", 0)
        
        if features == 0:
            return float('inf') if fixes > 0 else 0
            
        return fixes / features
    
    def format_default(self):
        """Format output as human-readable summary"""
        if self.total_commits == 0:
            return "No commits found in the provided input."
            
        percentages = self.calculate_percentages()
        hostile_score = self.get_hostile_score()
        
        output = []
        output.append(f"=== Git Commit Analysis ===")
        output.append(f"Total commits analyzed: {self.total_commits}")
        output.append("")
        
        # Sort by count descending
        sorted_counts = sorted(self.counts.items(), key=lambda x: x[1], reverse=True)
        
        for category, count in sorted_counts:
            pct = percentages[category]
            output.append(f"{category.capitalize()}: {count} ({pct:.1f}%)")
        
        output.append("")
        output.append(f"Hostile Architecture Score: {hostile_score:.2f}")
        output.append("(Ratio of fixes+workarounds to features - higher is worse)")

        unknown_percentage = percentages.get("uncategorized", 0)
        
        # Interpretation
        output.append("")
        if unknown_percentage > 40:
            output.append(f"🤔 LOW VISIBILITY: {unknown_percentage:.1f}% of commits are uncategorized")
            output.append("   (True architecture quality unknown - categorize more commits!)")
        elif hostile_score > 3:
            output.append("🔥 SEVERE: You're fighting fires, not building features!")
        elif hostile_score > 1.5:
            output.append("⚠️  WARNING: More time fixing than building!")
        elif hostile_score > 0.5:
            output.append("😐 CONCERN: Significant time on fixes")
        elif unknown_percentage > 25:
            output.append(f"🤷 UNCLEAR: {unknown_percentage:.1f}% uncategorized commits")
            output.append("   (Architecture seems healthy but visibility could be better)")
        else:
            output.append("✅ HEALTHY: Good feature/fix balance")
            
        # Show sample uncategorized if any
        if self.uncategorized and len(self.uncategorized) <= 5:
            output.append("")
            output.append("Uncategorized commits:")
            for msg in self.uncategorized[:5]:
                output.append(f"  - {msg[:60]}...")
                
        return "\n".join(output)
    
    def format_barchart(self):
        """Format output for mlbarchart"""
        output = []
        # Sort by count for better visualization
        sorted_counts = sorted(self.counts.items(), key=lambda x: x[1], reverse=True)
        
        for category, count in sorted_counts:
            # Capitalize for prettier charts
            label = category.replace("_", " ").title()
            output.append(f"{label}: {count}")
            
        return "\n".join(output)
    
    def format_json(self):
        """Format output as JSON"""
        data = {
            "total_commits": self.total_commits,
            "counts": dict(self.counts),
            "percentages": self.calculate_percentages(),
            "hostile_score": self.get_hostile_score(),
            "uncategorized_sample": self.uncategorized[:10]
        }
        return json.dumps(data, indent=2)
    
    def format_csv(self):
        """Format output as CSV for spreadsheet import"""
        output = []
        output.append("Category,Count,Percentage")
        
        percentages = self.calculate_percentages()
        for category, count in sorted(self.counts.items()):
            pct = percentages[category]
            output.append(f"{category},{count},{pct:.1f}")
            
        return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(
        description="Analyze git commits to reveal where development time actually goes",
        epilog="Example: git log --oneline --since '1 month ago' | mlgitaudit --barchart | mlbarchart"
    )
    
    parser.add_argument('file', nargs='?', type=argparse.FileType('r'), 
                       default=sys.stdin,
                       help='Git log file to analyze (default: stdin)')
    
    # Output format options
    format_group = parser.add_mutually_exclusive_group()
    format_group.add_argument('--barchart', action='store_true',
                            help='Output format for mlbarchart')
    format_group.add_argument('--json', action='store_true',
                            help='Output raw JSON data')
    format_group.add_argument('--csv', action='store_true',
                            help='Output CSV for spreadsheets')
    
    # Additional options
    parser.add_argument('--show-keywords', action='store_true',
                       help='Show current keyword configuration')
    parser.add_argument('--add-keyword', nargs=2, metavar=('CATEGORY', 'KEYWORD'),
                       help='Add a keyword to a category')
    
    args = parser.parse_args()
    
    auditor = MLGitAudit()
    
    # Handle keyword management
    if args.show_keywords:
        print(json.dumps(auditor.keywords, indent=2))
        return
        
    if args.add_keyword:
        category, keyword = args.add_keyword
        if category not in auditor.keywords:
            auditor.keywords[category] = []
        if keyword not in auditor.keywords[category]:
            auditor.keywords[category].append(keyword)
            with open(auditor.keywords_file, 'w') as f:
                json.dump(auditor.keywords, f, indent=2)
            print(f"Added '{keyword}' to category '{category}'")
        return
    
    # Process the log
    try:
        auditor.process_log(args.file)
    except KeyboardInterrupt:
        pass  # Allow partial processing
    
    # Output results in requested format
    if args.barchart:
        print(auditor.format_barchart())
    elif args.json:
        print(auditor.format_json())
    elif args.csv:
        print(auditor.format_csv())
    else:
        print(auditor.format_default())

if __name__ == "__main__":
    main()