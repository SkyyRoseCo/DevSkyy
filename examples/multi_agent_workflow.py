"""
Multi-Agent Workflow Example

Demonstrates complex workflows requiring multiple SuperAgents.
"""

import asyncio
import os

from agent_sdk.main import DevSkyy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def product_launch_workflow():
    """
    Complex workflow: Launch a new product.

    This requires coordination between:
    - Creative: Generate 3D product model
    - Commerce: Create WooCommerce product
    - Marketing: Create launch campaign
    - Analytics: Set up tracking metrics
    """
    print("=" * 60)
    print("Multi-Agent Workflow: Product Launch")
    print("=" * 60)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n❌ ERROR: ANTHROPIC_API_KEY not set!")
        return

    devskyy = DevSkyy()

    task = """
    Launch a new product: "Eternal Love Engagement Ring"

    Requirements:
    1. Generate a 3D visualization of the ring (rose gold with diamond)
    2. Create the product in WooCommerce with premium pricing
    3. Design a Valentine's Day marketing campaign
    4. Set up analytics tracking for the launch

    Ensure all outputs align with SkyyRose brand guidelines:
    - Premium, elegant, romantic
    - Colors: Rose Gold (#B76E79), Black (#1A1A1A)
    - No tagline is authorised
    """

    print("\n🚀 Task: Product Launch Workflow")
    print("-" * 60)
    print(task)

    # Execute with orchestrator
    # The orchestrator will automatically delegate to appropriate SuperAgents
    result = await devskyy.execute(task, permission_mode="acceptEdits")  # Allow file creation, etc.

    print("\n📊 Results:")
    print("-" * 60)
    print(result["result"])

    print(f"\n💰 Cost: ${result.get('total_cost_usd', 0):.4f}")
    print(f"⏱️  Duration: {result.get('duration_ms', 0)}ms")
    print(f"🆔 Session: {result.get('session_id', 'N/A')}")


async def campaign_optimization_workflow():
    """
    Workflow: Optimize existing marketing campaign.

    Requires:
    - Analytics: Analyze current performance
    - Marketing: Suggest improvements
    - Creative: Generate new visuals if needed
    """
    print("\n" + "=" * 60)
    print("Multi-Agent Workflow: Campaign Optimization")
    print("=" * 60)

    devskyy = DevSkyy()

    task = """
    Optimize our Valentine's Day email campaign:

    1. Analyze current metrics (open rate, click rate, conversions)
    2. Identify areas for improvement
    3. Suggest A/B test variations for subject lines and content
    4. Recommend timing and segmentation strategies
    5. Estimate expected improvement in conversion rate
    """

    print("\n📈 Task: Campaign Optimization")
    print("-" * 60)

    result = await devskyy.execute(task, permission_mode="bypassPermissions")  # Analysis only

    print("\n📊 Optimization Recommendations:")
    print("-" * 60)
    print(result["result"])


async def customer_support_workflow():
    """
    Workflow: Handle complex customer inquiry.

    Requires:
    - Support: Handle ticket
    - Commerce: Check order status
    - Operations: Check shipping/delivery
    """
    print("\n" + "=" * 60)
    print("Multi-Agent Workflow: Customer Support")
    print("=" * 60)

    devskyy = DevSkyy()

    task = """
    Customer Support Scenario:

    Customer inquiry: "I ordered an engagement ring 2 weeks ago (Order #12345)
    but haven't received it. It was supposed to arrive before Valentine's Day.
    What's the status? Can you expedite shipping?"

    Actions needed:
    1. Check order status and shipping info
    2. Determine current location of package
    3. Assess if expedited shipping is possible
    4. Draft empathetic response with solutions
    5. Suggest compensation if delivery was delayed
    """

    print("\n💬 Task: Customer Support Inquiry")
    print("-" * 60)

    result = await devskyy.execute(task, permission_mode="default")  # Require approval for actions

    print("\n✉️  Support Response:")
    print("-" * 60)
    print(result["result"])


async def main():
    """Run all multi-agent workflow examples."""
    try:
        # Run product launch workflow
        await product_launch_workflow()

        # Run campaign optimization
        await campaign_optimization_workflow()

        # Run customer support
        await customer_support_workflow()

        print("\n" + "=" * 60)
        print("✅ All workflows completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
