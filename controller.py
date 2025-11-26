# controller.py
import asyncio
from datetime import datetime
import logging
import sys
import threading
from typing import Optional

from app.config import Config
from app.whatsapp_bot import WhatsAppBot
from app.pipeline import LLMPipeline
from app.utils import get_timestamp,setup_logging
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
        logger.info(f"AI Helper {status} (running={self.running})")
        print(f"\n🤖 AI Helper {status}")
        if self.ai_enabled and not self.running:
            logger.warning("AI enabled but app is not running. Make sure to start the app first.")
            print("⚠️  Warning: App is not running. Please start the app first.")
        return self.ai_enabled
    
    def set_agent_type(self, agent_type: str):
        """Set the agent type for the AI pipeline."""
        valid_types = ["default", "friendly", "flirty"]
        if agent_type not in valid_types:
            raise ValueError(f"Invalid agent type. Must be one of: {valid_types}")
        
        self.pipeline.set_agent_type(agent_type)
        logger.info(f"Agent type set to: {agent_type}")
        print(f"🎭 Agent type changed to: {agent_type}")
        return agent_type
    
    def get_agent_type(self):
        """Get the current agent type."""
        return self.pipeline.agent_type
    
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
                print("✅ AI Helper ENABLED--->")

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
        """Continuously monitor for new messages when AI is enabled."""
        logger.info("Message monitoring loop started")
        while self.running:
            try:
                if self.ai_enabled:
                    logger.debug("AI enabled - checking for new messages...")
                    print("🔍 Checking for new messages...")
                    has_new = await self.bot.check_new_messages()
                    if has_new:
                        logger.info("New message detected, processing...")
                        await self.process_new_message()
                else:
                    logger.debug("AI disabled - skipping message check")

                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Error in monitor_messages loop: {e}", exc_info=True)
                print(f"❌ Error checking messages: {e}")
                # Continue running even if there's an error
                await asyncio.sleep(2)
        
        logger.info("Message monitoring loop stopped")


class AppController:
    def __init__(self):
        self.app = WhatsAppAIChatHelper()
        self.loop = None
        self.loop_thread = None
        self.monitor_task = None

    def _run_event_loop(self):
        """Run the event loop in a separate thread."""
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            logger.info("Event loop created in background thread")
            self.loop.run_forever()
        except Exception as e:
            logger.error(f"Error in event loop thread: {e}", exc_info=True)
        finally:
            if self.loop:
                self.loop.close()
                self.loop = None

    def start_background_loop(self):
        """Start the background event loop in a separate thread."""
        if self.loop_thread is None or not self.loop_thread.is_alive():
            self.loop_thread = threading.Thread(target=self._run_event_loop, daemon=True)
            self.loop_thread.start()
            logger.info("Background event loop thread started")
            
            # Wait for the loop to be initialized
            import time
            max_wait = 5  # Wait up to 5 seconds
            waited = 0
            while self.loop is None and waited < max_wait:
                time.sleep(0.1)
                waited += 0.1
            
            if self.loop is None:
                raise RuntimeError("Failed to initialize background event loop")
            
            logger.info("Background event loop initialized and running")

    def start(self):
        """Initialize the app and start monitoring."""
        try:
            # Start background event loop if not already running
            if self.loop is None or not self.loop.is_running():
                self.start_background_loop()
            
            if self.loop is None or not self.loop.is_running():
                raise RuntimeError("Event loop is not running")
            
            # Run initialization in the background loop
            logger.info("Initializing WhatsApp bot and pipeline...")
            future = asyncio.run_coroutine_threadsafe(self.app.initialize(), self.loop)
            future.result(timeout=120)  # Wait up to 120 seconds for initialization
            
            logger.info("App initialized successfully")
            
            # Set running flag
            self.app.running = True
            
            # Start monitoring task in background loop
            if self.monitor_task is None or self.monitor_task.done():
                self.monitor_task = asyncio.run_coroutine_threadsafe(
                    self._monitor_wrapper(), 
                    self.loop
                )
                logger.info("Message monitoring task started")
            else:
                logger.info("Message monitoring task already running")
            
        except Exception as e:
            logger.error(f"Error starting app: {e}", exc_info=True)
            raise

    async def _monitor_wrapper(self):
        """Wrapper to run monitor_messages continuously."""
        try:
            await self.app.monitor_messages()
        except Exception as e:
            logger.error(f"Error in monitor wrapper: {e}", exc_info=True)

    def stop(self):
        """Stop the app and cleanup."""
        try:
            self.app.running = False
            
            # Cancel monitoring task if running
            if self.monitor_task and not self.monitor_task.done():
                self.monitor_task.cancel()
            
            # Run cleanup in background loop
            if self.loop and self.loop.is_running():
                future = asyncio.run_coroutine_threadsafe(self.app.cleanup(), self.loop)
                try:
                    future.result(timeout=10)
                except Exception as e:
                    logger.error(f"Error during cleanup: {e}")
            
            # Stop the event loop
            if self.loop and self.loop.is_running():
                self.loop.call_soon_threadsafe(self.loop.stop)
            
            logger.info("App stopped")
            
        except Exception as e:
            logger.error(f"Error stopping app: {e}", exc_info=True)

    def toggle_ai(self):
        return self.app.toggle_ai()

    def set_agent_type(self, agent_type: str):
        """Set the agent type for the AI pipeline."""
        return self.app.set_agent_type(agent_type)
    
    def get_agent_type(self):
        """Get the current agent type."""
        return self.app.get_agent_type()

    def get_status(self):
        return {
            "ai_enabled": self.app.ai_enabled,
            "running": self.app.running,
            "agent_type": self.app.get_agent_type()
        }
