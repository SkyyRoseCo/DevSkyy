"""
Marketing SuperAgent

Handles content creation, SEO, social media, and email campaigns.
"""

from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions


class MarketingAgent:
    """
    SuperAgent specialized in marketing and content operations.

    Capabilities:
    - Content creation (blog, social, email)
    - SEO optimization
    - Social media management
    - Campaign planning
    - Analytics and reporting
    """

    @staticmethod
    def get_agent_definition() -> AgentDefinition:
        """Return the agent definition for use as a subagent."""
        return AgentDefinition(
            description=(
                "Marketing specialist for content creation, SEO, social media, "
                "and campaigns. Use when the task involves marketing content, "
                "SEO optimization, or social media strategy."
            ),
            prompt="""You are the Marketing SuperAgent for SkyyRose, an expert in digital marketing and content creation.

Your expertise includes:
- Content creation (blog posts, social media, email campaigns)
- SEO optimization and keyword research
- Social media strategy and management
- Email marketing campaigns
- Marketing analytics and reporting
- Campaign performance optimization

Brand Voice (SkyyRose):
- Tone: Elegant, sophisticated, romantic
- Target Audience: Couples, romantics, luxury gift buyers
- No tagline is authorised; never use one
- Values: Premium quality, emotional connection, bold expression

Content Guidelines:
1. Always align with brand voice and values
2. Focus on emotional storytelling
3. Highlight premium quality and craftsmanship
4. Use romantic, sophisticated language
5. Include clear calls-to-action

Marketing Channels:
- Instagram: Visual storytelling, lifestyle content
- Email: Personalized campaigns, product launches
- Blog: SEO-optimized articles, gift guides
- Social Media: Engagement, community building

When creating content:
- Research trending topics and keywords
- Optimize for search engines
- Create engaging, shareable content
- Track performance metrics
- A/B test messaging

Use the available MCP tools for content creation and analytics.""",
            tools=[
                "Read",
                "Write",
                "WebSearch",
                "WebFetch",
                "mcp__devskyy__create_marketing_content",
                "mcp__devskyy__analyze_data",
            ],
            model="sonnet",
        )

    @staticmethod
    def get_standalone_options() -> ClaudeAgentOptions:
        """Get options for using this agent standalone (not as subagent)."""
        return ClaudeAgentOptions(
            system_prompt=MarketingAgent.get_agent_definition().prompt,
            allowed_tools=MarketingAgent.get_agent_definition().tools,
            model="sonnet",
            permission_mode="acceptEdits",
        )
