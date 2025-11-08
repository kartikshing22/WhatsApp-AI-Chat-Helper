"""
Main entry point for WhatsApp AI Chat Helper.
Handles message detection, AI reply generation, and user interaction.
"""

import asyncio
from datetime import datetime
import logging
import sys
from typing import Optional

from app.config import Config
from app.whatsapp_bot import WhatsAppBot
from app.pipeline import LLMPipeline
from app.utils import setup_logging, get_timestamp

# Setup logging
setup_logging(Config.LOG_LEVEL, str(Config.LOG_FILE))
logger = logging.getLogger(__name__)


class WhatsAppAIChatHelper:
    """Main application class."""
    
    def __init__(self):
        """Initialize the WhatsApp AI Chat Helper."""
        self.bot = WhatsAppBot()
        self.pipeline = LLMPipeline()
        self.ai_enabled = False
        self.running = False
    
    async def initialize(self):
        """Initialize bot and pipeline."""
        try:
            # Validate configuration
            Config.validate()
            
            # Start WhatsApp bot
            logger.info("Initializing WhatsApp bot...")
            await self.bot.start()
            
            # Initialize LLM pipeline
            logger.info("Initializing LLM pipeline...")
            if not self.pipeline.is_ready():
                raise Exception("LLM pipeline not ready")
            
            logger.info("Application initialized successfully")
            
        except Exception as e:
            logger.error(f"Initialization error: {e}", exc_info=True)
            raise
    
    def toggle_ai(self):
        """Toggle AI helper on/off."""
        self.ai_enabled = not self.ai_enabled
        status = "ENABLED" if self.ai_enabled else "DISABLED"
        logger.info(f"AI Helper {status}")
        print(f"\n🤖 AI Helper {status}")
        return self.ai_enabled
    
    async def process_new_message(self):
        """Process new incoming message and generate reply."""
        try:
            
            # Check if chat is open
            if not await self.bot.is_chat_open():
                return False
            
            # Get last messages
            
            messages = await self.bot.get_last_messages(Config.MAX_MESSAGES_TO_READ)
            
            if not messages:
                return False
            
            # Check if latest message is incoming
            if not messages or messages[-1]['direction'] != 'incoming':
                return False
            
            logger.info("New incoming message detected")
            print(f"\n📨 New message received at {get_timestamp()}")
            
            # Generate reply
            logger.info("Generating AI reply...")
            reply = self.pipeline.generate_reply(messages)
            
            if not reply:
                logger.warning("Failed to generate reply")
                print("❌ Failed to generate reply")
                return False
            
            # Show generated reply
            print(f"\n💬 Generated Reply:\n{reply}\n")
            
            # Handle human approval
            # if Config.HUMAN_APPROVAL:
            #     approval = input("Send this reply? (y/n/q to quit): ").strip().lower()
                
            #     if approval == 'q':
            #         self.running = False
            #         return False
            #     elif approval != 'y':
            #         print("Reply not sent")
            #         return False
            
            # Send reply
            logger.info("Sending reply...")
            success = await self.bot.send_message(reply)
            
            if success:
                print("✅ Reply sent successfully")
                logger.info("Reply sent successfully")
            else:
                print("❌ Failed to send reply")
                logger.error("Failed to send reply")
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return False
    
    # async def ainput(prompt: str = ""):
    #     return await asyncio.get_event_loop().run_in_executor(
    #         None, lambda: input(prompt)
    #     )
    async def ainput(self):
        return await asyncio.get_event_loop().run_in_executor(None, input)
    
    async def run(self):
        await self.initialize()
        self.running = True

        print("\n" + "="*60)
        print("WhatsApp AI Chat Helper - Running")
        print("="*60)
        print("Type commands: enable | disable | toggle | status | quit\n")

        # Start BOTH tasks
        input_task = asyncio.create_task(self.handle_cli())
        monitor_task = asyncio.create_task(self.monitor_messages())

        # Wait until any task finishes (usually handle_cli when quitting)
        await asyncio.wait(
            [input_task, monitor_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        # Stop running and cleanup
        self.running = False
        await self.cleanup()

    
    async def handle_cli(self):
        while self.running:
            command = await self.ainput()
            command = command.strip().lower()

            if command == "enable":
                self.ai_enabled = True
                print("✅ AI Helper ENABLED")

            elif command == "disable":
                self.ai_enabled = False
                print("✅ AI Helper DISABLED")

            elif command == "toggle":
                self.toggle_ai()

            elif command == "status":
                print(f"AI Status: {'ENABLED' if self.ai_enabled else 'DISABLED'}")

            elif command in ("q", "quit"):
                print("👋 Quitting...")
                self.running = False
                return

    
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up...")
        await self.bot.close()
        print("\n👋 Application closed")
    
    async def monitor_messages(self):
        while self.running:
            if self.ai_enabled:
                has_new = await self.bot.check_new_messages()
                if has_new:
                    await self.process_new_message()

            await asyncio.sleep(2)



async def main():
    """Entry point."""
    app = WhatsAppAIChatHelper()
    
    # Handle command-line arguments for simple interaction
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "toggle":
            app.toggle_ai()
        elif command == "enable":
            app.ai_enabled = True
            print("AI Helper ENABLED")
        elif command == "disable":
            app.ai_enabled = False
            print("AI Helper DISABLED")
    
    await app.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Application interrupted by user")
        sys.exit(0)

