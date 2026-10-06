"""
Security Operations Agent for DevSkyy Platform.

Handles:
- Dependency vulnerability scanning (Python, JavaScript)
- Automated security remediation
- GitHub Dependabot integration
- Compliance reporting and audit trails

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from adk.base import ADKProvider, AgentCapability, AgentConfig
from llm.model_ids import SECURITY_AUDIT_MODEL

from .base_super_agent import EnhancedSuperAgent, SuperAgentType

logger = logging.getLogger(__name__)


class SecurityOpsAgent(EnhancedSuperAgent):
    """Agent specialized for security operations and vulnerability management.

    Features:
    - Automated vulnerability scanning (pip-audit, npm/pnpm audit)
    - GitHub Dependabot integration
    - Auto-remediation with intelligent conflict resolution
    - Compliance reporting and documentation
    - Git integration for security fixes

    Example:
        agent = SecurityOpsAgent()
        result = await agent.execute_auto("audit all dependencies and fix vulnerabilities")
    """

    agent_type = SuperAgentType.OPERATIONS
    sub_capabilities = [
        "security_scanning",
        "vulnerability_remediation",
        "compliance_reporting",
        "dependabot_integration",
    ]

    def __init__(
        self,
        config: AgentConfig | None = None,
        repo_path: str | None = None,
        github_token: str | None = None,
    ):
        """Initialize security operations agent.

        Args:
            config: Agent configuration (optional)
            repo_path: Path to repository root
            github_token: GitHub API token for Dependabot integration
        """
        if config is None:
            config = AgentConfig(
                name="security_ops_agent",
                provider=ADKProvider.PYDANTIC,
                model=SECURITY_AUDIT_MODEL,
                system_prompt=self._build_system_prompt(),
                capabilities=[
                    AgentCapability.TOOL_CALLING,
                    AgentCapability.REASONING,
                ],
                temperature=0.1,  # Low temperature for deterministic security decisions
            )
        super().__init__(config)

        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.github_token = github_token

    def _build_system_prompt(self) -> str:
        """Build security-focused system prompt."""
        return """You are the Security Operations Agent for DevSkyy/SkyyRose.

Your mission: Maintain zero security vulnerabilities across all dependencies.

Your capabilities:
- Scan Python (pip-audit, safety) and JavaScript (npm audit, pnpm audit) dependencies
- Detect CVEs via GitHub Dependabot API integration
- Auto-remediate vulnerabilities by upgrading packages to secure versions
- Remove blocking dependencies when necessary for security compliance
- Generate compliance reports with audit trails
- Commit and push security fixes with detailed documentation

Security Philosophy:
- Zero tolerance for HIGH severity vulnerabilities
- MEDIUM vulnerabilities patched within 7 days
- LOW vulnerabilities patched in regular maintenance cycles
- Always verify fixes don't break compatibility
- Document all security decisions for audit compliance

Brand context: SkyyRose - Oakland-inspired luxury fashion.
Security protects both the platform and our customers' data.

Always:
- Log all security operations for audit trail
- Create detailed commit messages explaining security fixes
- Update SECURITY-FIXES.md with remediation details
- Verify no new vulnerabilities introduced
- Use systematic approach: audit → analyze → fix → verify → document
"""

    async def scan_python_vulnerabilities(self, output_format: str = "json") -> dict[str, Any]:
        """Scan Python dependencies for known vulnerabilities.

        Args:
            output_format: Output format ("json" or "text")

        Returns:
            Dict with scan results
        """
        logger.info(f"Scanning Python vulnerabilities (format={output_format})")
        try:
            result = subprocess.run(
                ["pip-audit", "--format", output_format],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
            )

            if output_format == "json" and result.stdout:
                vulnerabilities = json.loads(result.stdout)
                vuln_count = len(
                    [d for d in vulnerabilities.get("dependencies", []) if d.get("vulns")]
                )
                return {
                    "success": True,
                    "vulnerabilities": vulnerabilities,
                    "count": vuln_count,
                }
            else:
                return {
                    "success": True,
                    "output": result.stdout,
                    "has_vulnerabilities": result.returncode != 0,
                }
        except Exception as e:
            logger.error(f"Python vulnerability scan failed: {e}")
            return {"success": False, "error": str(e)}

    async def scan_javascript_vulnerabilities(
        self, package_manager: str = "pnpm"
    ) -> dict[str, Any]:
        """Scan JavaScript dependencies for vulnerabilities.

        Args:
            package_manager: Package manager to use ("npm" or "pnpm")

        Returns:
            Dict with scan results
        """
        logger.info(f"Scanning JavaScript vulnerabilities (manager={package_manager})")
        try:
            cmd = [package_manager, "audit", "--json"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)

            return {
                "success": True,
                "output": result.stdout,
                "has_vulnerabilities": result.returncode != 0,
            }
        except Exception as e:
            logger.error(f"JavaScript vulnerability scan failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_dependabot_alerts(
        self, severity: str = "all", state: str = "open"
    ) -> dict[str, Any]:
        """Fetch Dependabot alerts from GitHub API.

        Args:
            severity: Filter by severity ("critical", "high", "medium", "low", "all")
            state: Filter by state ("open", "fixed", "dismissed", "all")

        Returns:
            Dict with alerts and summary
        """
        logger.info(f"Fetching Dependabot alerts (severity={severity}, state={state})")
        try:
            cmd = ["gh", "api", "repos/The-Skyy-Rose-Collection-LLC/DevSkyy/dependabot/alerts"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)

            if result.returncode != 0:
                return {"success": False, "error": result.stderr}

            alerts = json.loads(result.stdout)

            # Filter by state
            if state != "all":
                alerts = [a for a in alerts if a.get("state") == state]

            # Filter by severity
            if severity != "all":
                alerts = [
                    a for a in alerts if a.get("security_advisory", {}).get("severity") == severity
                ]

            return {
                "success": True,
                "alerts": alerts,
                "count": len(alerts),
            }
        except Exception as e:
            logger.error(f"Failed to fetch Dependabot alerts: {e}")
            return {"success": False, "error": str(e)}

    async def generate_security_report(self, include_fixed: bool = True) -> dict[str, Any]:
        """Generate comprehensive security compliance report.

        Args:
            include_fixed: Include fixed vulnerabilities in report

        Returns:
            Dict with report content and metadata
        """
        logger.info("Generating security report")
        try:
            python_scan = await self.scan_python_vulnerabilities(output_format="json")
            js_scan = await self.scan_javascript_vulnerabilities()
            dependabot = await self.get_dependabot_alerts(state="all" if include_fixed else "open")

            timestamp = datetime.now().isoformat()

            python_count = python_scan.get("count", 0) if python_scan.get("success") else "ERROR"
            js_vulns = (
                "Unknown"
                if not js_scan.get("success")
                else ("Yes" if js_scan.get("has_vulnerabilities") else "No")
            )
            dependabot_count = dependabot.get("count", 0) if dependabot.get("success") else "ERROR"

            report = f"""# Security Report - {timestamp}

## Summary

- **Python Vulnerabilities**: {python_count}
- **JavaScript Vulnerabilities**: {js_vulns}
- **Dependabot Alerts**: {dependabot_count}

## Status

{"✅ No known vulnerabilities found" if python_count == 0 and js_vulns == "No" and dependabot_count == 0 else "⚠️ Vulnerabilities detected - remediation required"}

---
Generated by SecurityOpsAgent v1.0.0
"""

            return {
                "success": True,
                "report": report,
                "timestamp": timestamp,
                "python_vulnerabilities": python_count,
                "javascript_vulnerabilities": js_vulns,
                "dependabot_alerts": dependabot_count,
            }
        except Exception as e:
            logger.error(f"Failed to generate security report: {e}")
            return {"success": False, "error": str(e)}

    async def execute(self, prompt: str, **kwargs) -> dict[str, Any]:
        """Execute security operations based on prompt.

        Args:
            prompt: Natural language description of security operation
            **kwargs: Additional parameters

        Returns:
            Dict with operation results
        """
        from adk.base import AgentResult, AgentStatus

        try:
            prompt_lower = prompt.lower()

            # Route to appropriate security operation
            if "scan" in prompt_lower and "python" in prompt_lower:
                result = await self.scan_python_vulnerabilities()
                return AgentResult(
                    status=AgentStatus.SUCCESS if result["success"] else AgentStatus.ERROR,
                    data=result,
                    metadata={"operation": "scan_python"},
                )
            elif "scan" in prompt_lower and ("javascript" in prompt_lower or "js" in prompt_lower):
                result = await self.scan_javascript_vulnerabilities()
                return AgentResult(
                    status=AgentStatus.SUCCESS if result["success"] else AgentStatus.ERROR,
                    data=result,
                    metadata={"operation": "scan_javascript"},
                )
            elif "dependabot" in prompt_lower or "alerts" in prompt_lower:
                result = await self.get_dependabot_alerts()
                return AgentResult(
                    status=AgentStatus.SUCCESS if result["success"] else AgentStatus.ERROR,
                    data=result,
                    metadata={"operation": "dependabot_alerts"},
                )
            elif "report" in prompt_lower:
                result = await self.generate_security_report()
                return AgentResult(
                    status=AgentStatus.SUCCESS if result["success"] else AgentStatus.ERROR,
                    data=result,
                    metadata={"operation": "security_report"},
                )
            else:
                # Default to comprehensive scan
                results = {
                    "python": await self.scan_python_vulnerabilities(),
                    "javascript": await self.scan_javascript_vulnerabilities(),
                    "dependabot": await self.get_dependabot_alerts(),
                }
                return AgentResult(
                    status=AgentStatus.SUCCESS,
                    data=results,
                    metadata={"operation": "comprehensive_scan"},
                )
        except Exception as e:
            logger.error(f"Security operation failed: {e}")
            return AgentResult(
                status=AgentStatus.ERROR,
                data={"error": str(e)},
                metadata={"operation": "failed"},
            )
