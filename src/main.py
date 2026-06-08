"""
Main entry point for the Deep Agent Trading Research System.
"""
import os
import sys
import logging
from dotenv import load_dotenv

from src.agent.harness import DeepAgentHarness

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not set in .env file")
        print("Please add your Google API key to the .env file")
        sys.exit(1)
    
    print("=" * 80)
    print("🤖 Deep Agent Trading Research System")
    print("=" * 80)
    print()
    
    # Get configuration
    model = os.getenv("GEMINI_MODEL", "gemini-pro")
    
    print(f"Model: Google {model}")
    print(f"Real Trading: ✅ Enabled (with mandatory approval gates)")
    print()
    
    # Initialize agent
    print("Initializing agent...")
    try:
        agent = DeepAgentHarness(
            google_api_key=api_key,
            model=model
        )
        print("✅ Agent initialized successfully")
        print()
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        sys.exit(1)
    
    # Interactive mode
    print("=" * 80)
    print("Interactive Mode - Enter your requests (or 'quit' to exit)")
    print("=" * 80)
    print()
    
    print("Example requests:")
    print("  - Analyze AAPL stock and show me the current price and volatility")
    print("  - What's the risk of buying one AAPL call option at $180 strike?")
    print("  - Show me my portfolio and identify concentration risks")
    print("  - Buy 10 shares of MSFT (will require approval)")
    print()
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            print()
            print("🤖 Agent is thinking...")
            print()
            
            # Run agent
            result = agent.run(user_input)
            
            # Display result
            print("=" * 80)
            print("📊 AGENT RESPONSE")
            print("=" * 80)
            print()
            print(result.final_report)
            print()
            
            if result.success:
                print(f"✅ Run completed successfully (Run ID: {result.run_id})")
                print(f"📁 Artifacts saved to: workspace/runs/{result.run_id}/")
            else:
                print(f"❌ Run failed: {result.error}")
            
            print()
            print("=" * 80)
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.exception("Error in main loop")
            print()


if __name__ == "__main__":
    main()

# Made with Bob
