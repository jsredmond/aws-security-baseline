#!/usr/bin/env python3
"""
Generate comprehensive audit report by aggregating findings from all module audits.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, field


@dataclass
class Finding:
    """Represents a security finding from module audit."""
    module: str
    title: str
    resource: str
    severity: str
    category: str
    effort: str
    breaking_change: bool
    description: str
    current_config: str
    recommended_config: str
    aws_doc_reference: str
    terraform_doc_reference: str
    
    def __hash__(self):
        return hash((self.module, self.title, self.resource))


def parse_audit_report(report_path: Path) -> Tuple[str, List[Finding]]:
    """Parse an individual module audit report and extract findings."""
    content = report_path.read_text()
    
    # Extract module name from filename or content
    module_match = re.search(r'(\w+)-audit-report\.md', report_path.name)
    if module_match:
        module_name = module_match.group(1)
    else:
        module_match = re.search(r'Module:\s+(\w+)', content)
        module_name = module_match.group(1) if module_match else "unknown"
    
    findings = []
    
    # Split content by severity sections
    severity_pattern = r'####?\s+(Critical|High|Medium|Low)\s+Severity'
    sections = re.split(severity_pattern, content)
    
    current_severity = None
    for i, section in enumerate(sections):
        if section.strip() in ['Critical', 'High', 'Medium', 'Low']:
            current_severity = section.strip()
            continue
        
        if current_severity is None:
            continue
        
        # Extract individual findings from the section
        finding_pattern = r'#####\s+(.+?)\n\n\*\*Resource:\*\*\s+`(.+?)`\n\n\*\*Category:\*\*\s+(.+?)\n\n\*\*Effort:\*\*\s+(.+?)\n\n\*\*Breaking Change:\*\*\s+(.+?)\n\n\*\*Description:\*\*\n\n(.+?)\n\n\*\*Current Configuration:\*\*\n\n```(?:hcl)?\n(.+?)\n```\n\n\*\*Recommended Configuration:\*\*\n\n```(?:hcl)?\n(.+?)\n```\n\n\*\*References:\*\*\n\n-\s+\[AWS Documentation\]\((.+?)\)\n-\s+\[Terraform Documentation\]\((.+?)\)'
        
        for match in re.finditer(finding_pattern, section, re.DOTALL):
            title = match.group(1).strip()
            resource = match.group(2).strip()
            category = match.group(3).strip()
            effort = match.group(4).strip()
            breaking_change = match.group(5).strip().lower() == 'yes'
            description = match.group(6).strip()
            current_config = match.group(7).strip()
            recommended_config = match.group(8).strip()
            aws_doc = match.group(9).strip()
            terraform_doc = match.group(10).strip()
            
            finding = Finding(
                module=module_name,
                title=title,
                resource=resource,
                severity=current_severity,
                category=category,
                effort=effort,
                breaking_change=breaking_change,
                description=description,
                current_config=current_config,
                recommended_config=recommended_config,
                aws_doc_reference=aws_doc,
                terraform_doc_reference=terraform_doc
            )
            findings.append(finding)
    
    return module_name, findings


def aggregate_findings(spec_dir: Path) -> Dict[str, List[Finding]]:
    """Aggregate findings from all module audit reports."""
    all_findings = {}
    
    # Find all audit report files
    audit_reports = list(spec_dir.glob('*-audit-report.md'))
    
    for report_path in audit_reports:
        module_name, findings = parse_audit_report(report_path)
        if findings:
            all_findings[module_name] = findings
    
    return all_findings


def categorize_findings(findings_by_module: Dict[str, List[Finding]]) -> Dict[str, Dict[str, List[Finding]]]:
    """Categorize findings by severity and type."""
    categorized = {
        'by_severity': {'Critical': [], 'High': [], 'Medium': [], 'Low': []},
        'by_category': {}
    }
    
    for module, findings in findings_by_module.items():
        for finding in findings:
            # By severity
            categorized['by_severity'][finding.severity].append(finding)
            
            # By category
            if finding.category not in categorized['by_category']:
                categorized['by_category'][finding.category] = []
            categorized['by_category'][finding.category].append(finding)
    
    return categorized


def identify_quick_wins(findings_by_module: Dict[str, List[Finding]]) -> List[Finding]:
    """Identify quick wins (low effort, high/medium severity)."""
    quick_wins = []
    
    for module, findings in findings_by_module.items():
        for finding in findings:
            if finding.effort == 'Low' and finding.severity in ['High', 'Medium']:
                quick_wins.append(finding)
    
    # Sort by severity (High first, then Medium)
    quick_wins.sort(key=lambda f: (0 if f.severity == 'High' else 1, f.module, f.title))
    
    return quick_wins


def generate_executive_summary(findings_by_module: Dict[str, List[Finding]], 
                               categorized: Dict[str, Dict[str, List[Finding]]]) -> str:
    """Generate executive summary section."""
    total_findings = sum(len(findings) for findings in findings_by_module.values())
    critical_count = len(categorized['by_severity']['Critical'])
    high_count = len(categorized['by_severity']['High'])
    medium_count = len(categorized['by_severity']['Medium'])
    low_count = len(categorized['by_severity']['Low'])
    
    modules_audited = sorted(findings_by_module.keys())
    quick_wins = identify_quick_wins(findings_by_module)
    
    summary = f"""## Executive Summary

- **Total Findings:** {total_findings}
- **Critical:** {critical_count}
- **High:** {high_count}
- **Medium:** {medium_count}
- **Low:** {low_count}
- **Modules Audited:** {', '.join(modules_audited)}
- **Quick Wins Identified:** {len(quick_wins)}

### Key Insights

This comprehensive audit of the AWS Security Baseline Terraform modules identified {total_findings} findings across {len(modules_audited)} security service modules. The findings span multiple categories including access control, encryption, monitoring, logging, and configuration management.

**Severity Distribution:**
- {high_count} high-severity findings require immediate attention
- {medium_count} medium-severity findings should be addressed in the near term
- {low_count} low-severity findings represent opportunities for improvement

**Quick Wins:** {len(quick_wins)} findings are classified as "quick wins" - low effort changes that provide significant security value. These should be prioritized for immediate implementation.

**Breaking Changes:** {sum(1 for findings in findings_by_module.values() for f in findings if f.breaking_change)} findings involve breaking changes that require careful planning and migration strategies.
"""
    
    return summary


def generate_findings_section(findings_by_module: Dict[str, List[Finding]]) -> str:
    """Generate detailed findings section organized by module."""
    sections = []
    
    for module in sorted(findings_by_module.keys()):
        findings = findings_by_module[module]
        
        # Group by severity
        by_severity = {'Critical': [], 'High': [], 'Medium': [], 'Low': []}
        for finding in findings:
            by_severity[finding.severity].append(finding)
        
        module_section = f"### Module: {module.capitalize()}\n\n"
        
        for severity in ['Critical', 'High', 'Medium', 'Low']:
            if not by_severity[severity]:
                continue
            
            module_section += f"#### {severity} Severity\n\n"
            
            for finding in by_severity[severity]:
                module_section += f"""##### {finding.title}

**Resource:** `{finding.resource}`

**Category:** {finding.category}

**Effort:** {finding.effort}

**Breaking Change:** {'Yes' if finding.breaking_change else 'No'}

**Description:**

{finding.description}

**Current Configuration:**

```hcl
{finding.current_config}
```

**Recommended Configuration:**

```hcl
{finding.recommended_config}
```

**References:**

- [AWS Documentation]({finding.aws_doc_reference})
- [Terraform Documentation]({finding.terraform_doc_reference})

---

"""
        
        sections.append(module_section)
    
    return "\n".join(sections)


def generate_quick_wins_section(quick_wins: List[Finding]) -> str:
    """Generate quick wins section."""
    if not quick_wins:
        return "## Quick Wins\n\nNo quick wins identified.\n\n"
    
    section = """## Quick Wins

These findings are low effort but provide significant security value. Prioritize these for immediate implementation:

"""
    
    for i, finding in enumerate(quick_wins, 1):
        section += f"""{i}. **{finding.title}** ({finding.module})
   - Severity: {finding.severity}
   - Resource: `{finding.resource}`
   - Effort: {finding.effort}
   - Category: {finding.category}

"""
    
    return section


def generate_recommendations_section(categorized: Dict[str, Dict[str, List[Finding]]]) -> str:
    """Generate recommendations section prioritized by severity and effort."""
    section = """## Recommendations

### Implementation Priority

"""
    
    # Priority 1: Critical and High Severity
    high_priority = categorized['by_severity']['Critical'] + categorized['by_severity']['High']
    if high_priority:
        section += "#### Priority 1: Critical and High Severity Findings\n\n"
        section += "These findings represent significant security risks and should be addressed immediately:\n\n"
        
        # Group by effort
        by_effort = {'Low': [], 'Medium': [], 'High': []}
        for finding in high_priority:
            by_effort[finding.effort].append(finding)
        
        for effort in ['Low', 'Medium', 'High']:
            if by_effort[effort]:
                section += f"**{effort} Effort:**\n\n"
                for finding in by_effort[effort]:
                    section += f"- **{finding.title}** ({finding.module})\n"
                    section += f"  - Resource: `{finding.resource}`\n"
                    section += f"  - Breaking: {'Yes' if finding.breaking_change else 'No'}\n\n"
    
    # Priority 2: Medium Severity
    medium_priority = categorized['by_severity']['Medium']
    if medium_priority:
        section += "\n#### Priority 2: Medium Severity Findings\n\n"
        section += "These findings should be addressed in the near term:\n\n"
        
        # Group by effort
        by_effort = {'Low': [], 'Medium': [], 'High': []}
        for finding in medium_priority:
            by_effort[finding.effort].append(finding)
        
        for effort in ['Low', 'Medium', 'High']:
            if by_effort[effort]:
                section += f"**{effort} Effort:**\n\n"
                for finding in by_effort[effort]:
                    section += f"- **{finding.title}** ({finding.module})\n"
                    section += f"  - Resource: `{finding.resource}`\n"
                    section += f"  - Breaking: {'Yes' if finding.breaking_change else 'No'}\n\n"
    
    # Priority 3: Low Severity
    low_priority = categorized['by_severity']['Low']
    if low_priority:
        section += "\n#### Priority 3: Low Severity Findings\n\n"
        section += "These findings represent opportunities for improvement:\n\n"
        
        for finding in low_priority:
            section += f"- **{finding.title}** ({finding.module})\n"
            section += f"  - Resource: `{finding.resource}`\n"
            section += f"  - Effort: {finding.effort}\n"
            section += f"  - Breaking: {'Yes' if finding.breaking_change else 'No'}\n\n"
    
    # Breaking Changes Summary
    breaking_changes = []
    for severity_findings in categorized['by_severity'].values():
        breaking_changes.extend([f for f in severity_findings if f.breaking_change])
    
    if breaking_changes:
        section += "\n### Breaking Changes\n\n"
        section += f"The following {len(breaking_changes)} findings involve breaking changes that require careful planning:\n\n"
        
        for finding in breaking_changes:
            section += f"- **{finding.title}** ({finding.module}) - {finding.severity} severity\n"
    
    return section


def generate_comprehensive_report(spec_dir: Path) -> str:
    """Generate the comprehensive audit report."""
    # Aggregate findings
    findings_by_module = aggregate_findings(spec_dir)
    
    if not findings_by_module:
        return "No audit reports found to aggregate."
    
    # Categorize findings
    categorized = categorize_findings(findings_by_module)
    
    # Identify quick wins
    quick_wins = identify_quick_wins(findings_by_module)
    
    # Generate report sections
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""# AWS Security Baseline Comprehensive Audit Report

**Generated:** {timestamp}

**Report Version:** 1.0

---

"""
    
    # Table of Contents
    report += """## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Findings by Module](#findings-by-module)
3. [Quick Wins](#quick-wins)
4. [Recommendations](#recommendations)
5. [Category Analysis](#category-analysis)
6. [References](#references)

---

"""
    
    # Executive Summary
    report += generate_executive_summary(findings_by_module, categorized)
    report += "\n---\n\n"
    
    # Findings by Module
    report += "## Findings by Module\n\n"
    report += generate_findings_section(findings_by_module)
    report += "---\n\n"
    
    # Quick Wins
    report += generate_quick_wins_section(quick_wins)
    report += "---\n\n"
    
    # Recommendations
    report += generate_recommendations_section(categorized)
    report += "\n---\n\n"
    
    # Category Analysis
    report += "## Category Analysis\n\n"
    report += "Findings grouped by security category:\n\n"
    
    for category in sorted(categorized['by_category'].keys()):
        findings = categorized['by_category'][category]
        report += f"### {category}\n\n"
        report += f"**Total Findings:** {len(findings)}\n\n"
        
        # Count by severity
        severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
        for finding in findings:
            severity_counts[finding.severity] += 1
        
        report += f"- Critical: {severity_counts['Critical']}\n"
        report += f"- High: {severity_counts['High']}\n"
        report += f"- Medium: {severity_counts['Medium']}\n"
        report += f"- Low: {severity_counts['Low']}\n\n"
    
    report += "---\n\n"
    
    # References
    report += """## References

### AWS Documentation

- [AWS Security Best Practices](https://aws.amazon.com/architecture/security-identity-compliance/)
- [CloudTrail Security Best Practices](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/best-practices-security.html)
- [AWS Config Best Practices](https://docs.aws.amazon.com/config/latest/developerguide/best-practices.html)
- [GuardDuty Best Practices](https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_best-practices.html)
- [Detective Best Practices](https://docs.aws.amazon.com/detective/latest/userguide/security-best-practices.html)
- [Security Hub Best Practices](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-best-practices.html)
- [S3 Security Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)
- [KMS Best Practices](https://docs.aws.amazon.com/kms/latest/developerguide/best-practices.html)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

### Terraform Documentation

- [AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [Terraform Module Development](https://developer.hashicorp.com/terraform/language/modules/develop)

### Compliance Frameworks

- [CIS AWS Foundations Benchmark](https://www.cisecurity.org/benchmark/amazon_web_services)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [PCI DSS](https://www.pcisecuritystandards.org/)

---

## Next Steps

1. **Review Findings:** Review all findings with your security and infrastructure teams
2. **Prioritize Implementation:** Use the recommendations section to prioritize fixes
3. **Start with Quick Wins:** Implement low-effort, high-value changes first
4. **Plan Breaking Changes:** Develop migration strategies for breaking changes
5. **Test Changes:** Validate all changes in a non-production environment first
6. **Update Documentation:** Document all configuration changes and rationale
7. **Monitor Impact:** Track security posture improvements after implementation

---

*This report was automatically generated by the AWS Security Baseline Audit Tool.*
"""
    
    return report


def main():
    """Main entry point."""
    spec_dir = Path(__file__).parent.parent / '.kiro' / 'specs' / 'security-audit-mcp'
    
    print("Generating comprehensive audit report...")
    report = generate_comprehensive_report(spec_dir)
    
    # Write report
    output_path = spec_dir / 'audit-report.md'
    output_path.write_text(report)
    
    print(f"✓ Comprehensive audit report generated: {output_path}")


if __name__ == '__main__':
    main()
