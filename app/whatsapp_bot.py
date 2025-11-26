"""
WhatsApp Web automation using Playwright.
Handles browser automation, message reading, and sending.
"""

import asyncio
import logging
from typing import List, Dict, Optional
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError

from app.config import Config

logger = logging.getLogger(__name__)


class WhatsAppBot:
    """WhatsApp Web automation bot using Playwright."""
    
    def __init__(self):
        """Initialize WhatsApp bot."""
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.is_logged_in = False
        self.last_message_count = 0
        self.last_message = ""
    
    async def start(self):
        """Start browser and navigate to WhatsApp Web."""
        try:
            logger.info("Starting Playwright browser...")
            self.playwright = await async_playwright().start()
            
            # Launch browser with persistent context for session persistence
            browser_type = self.playwright.chromium
            context_path = Config.SESSION_DIR / "whatsapp_session"
            
            self.context = await browser_type.launch_persistent_context(
                user_data_dir=str(context_path),
                headless=Config.BROWSER_HEADLESS,
                args=['--disable-blink-features=AutomationControlled'],
                viewport={'width': 1280, 'height': 800},
                timeout=Config.BROWSER_TIMEOUT
            )
            
            # Create new page
            self.page = await self.context.new_page()
            
            # Navigate to WhatsApp Web
            logger.info(f"Navigating to {Config.WHATSAPP_WEB_URL}")
            await self.page.goto(Config.WHATSAPP_WEB_URL, wait_until="networkidle")
            
            # Wait for login or main interface
            await self._wait_for_login()
            
            logger.info("WhatsApp Web loaded successfully")
            
        except Exception as e:
            logger.error(f"Error starting browser: {e}", exc_info=True)
            raise
    
    async def _wait_for_login(self, timeout: int = 60000):
        """
        Wait for user to login (scan QR code if needed).
        
        Args:
            timeout: Maximum time to wait in milliseconds
        """
        try:
            # Check if already logged in (look for chat list)
            chat_list_selector = '#pane-side'
            qr_selector = 'canvas[aria-label*="QR"]'
            
            # Wait for either QR code or chat list
            try:
                await self.page.wait_for_selector(
                    f"{chat_list_selector}, {qr_selector}",
                    timeout=timeout
                )
                
                # Check if QR code is visible
                qr_element = await self.page.query_selector(qr_selector)
                if qr_element:
                    logger.info("QR code detected. Please scan with your phone...")
                    # Wait for QR to disappear (user logged in)
                    await self.page.wait_for_selector(
                        qr_selector,
                        state="hidden",
                        timeout=timeout
                    )
                    logger.info("QR code scanned, waiting for login to complete...")
                
                # Wait for chat list to appear
                await self.page.wait_for_selector(chat_list_selector, timeout=timeout)
                self.is_logged_in = True
                logger.info("Successfully logged in to WhatsApp Web")
                
            except PlaywrightTimeoutError:
                logger.warning("Login timeout - may already be logged in")
                # Try to check if we're on the main page
                if await self.page.query_selector(chat_list_selector):
                    self.is_logged_in = True
                    logger.info("Already logged in")
                else:
                    raise Exception("Failed to login to WhatsApp Web")
                    
        except Exception as e:
            logger.error(f"Error during login wait: {e}")
            raise
    
    async def get_last_messages(self, count: int = 10) -> List[Dict[str, str]]:
        """
        Get last N messages from the currently open chat.
        
        Args:
            count: Number of messages to retrieve
            
        Returns:
            List of message dicts with 'text', 'sender', 'timestamp', 'direction'
        """
        if not self.page:
            raise Exception("Page not initialized")
        
        try:
            # Wait for message container - try multiple selectors
            message_container_selectors = [
                '[data-testid="conversation-panel-messages"]',
                'div[role="log"]',
                'div[aria-label*="message"]',
                '#main > div > div > div'
            ]
            
            container = None
            for selector in message_container_selectors:
                try:
                    container = await self.page.wait_for_selector(selector, timeout=3000)
                    if container:
                        break
                except PlaywrightTimeoutError:
                    continue
            
            if not container:
                logger.warning("Message container not found")
                return []
            
            # Get all message elements - try multiple selectors
            message_selectors = [
                '[data-testid="msg-container"]',
                'div[data-id]',
                'div.message',
                'div[class*="message"]'
            ]
            
            message_elements = []
            for selector in message_selectors:
                message_elements = await self.page.query_selector_all(selector)
                if message_elements:
                    break
            
            if not message_elements:
                logger.warning("No messages found in current chat")
                return []
            
            # Get last N messages
            messages = []
            start_idx = max(0, len(message_elements) - count)
            
            for elem in message_elements[start_idx:]:
                try:
                    # Extract message text - try multiple selectors
                    text_selectors = [
                        'span.selectable-text',
                        'span[class*="selectable"]',
                        'span[dir="ltr"]',
                        'div[class*="text"]'
                    ]
                    
                    text = None
                    for selector in text_selectors:
                        text_elem = await elem.query_selector(selector)
                        if text_elem:
                            text = await text_elem.inner_text()
                            text = text.strip()
                            if text:
                                break
                    
                    if not text:
                        continue
                    
                    # Determine if message is outgoing or incoming
                    # Check for outgoing message indicators
                    message_classes = await elem.get_attribute("class") or ""
                    message_id = await elem.get_attribute("data-id") or ""
                    
                    # Outgoing messages typically have specific classes or attributes
                    is_outgoing = (
                        "message-out" in message_classes.lower() or
                        "message-sent" in message_classes.lower() or
                        (message_id and "true" in str(message_id))
                    )
                    
                    # Alternative: check if message is on the right side (outgoing)
                    try:
                        box_model = await elem.bounding_box()
                        if box_model:
                            page_width = self.page.viewport_size['width'] if self.page.viewport_size else 1280
                            # If message is on the right side, it's likely outgoing
                            if box_model['x'] > page_width * 0.5:
                                is_outgoing = True
                    except:
                        pass
                    
                    sender = "You" if is_outgoing else "Contact"
                    
                    # Try to get timestamp
                    time_selectors = [
                        'span[data-testid="msg-meta"]',
                        'span[class*="time"]',
                        'span[class*="timestamp"]'
                    ]
                    
                    timestamp = ""
                    for selector in time_selectors:
                        time_elem = await elem.query_selector(selector)
                        if time_elem:
                            timestamp = await time_elem.inner_text()
                            timestamp = timestamp.strip()
                            if timestamp:
                                break
                    
                    messages.append({
                        'text': text,
                        'sender': sender,
                        'timestamp': timestamp,
                        'direction': 'outgoing' if is_outgoing else 'incoming'
                    })
                    
                except Exception as e:
                    logger.debug(f"Error parsing message element: {e}")
                    continue
            
            logger.info(f"Retrieved {len(messages)} messages from chat")
            return messages
            
        except Exception as e:
            logger.error(f"Error getting messages: {e}", exc_info=True)
            return []
    
    async def send_message(self, text: str) -> bool:
        """
        Type and send a message in the current chat.
        
        Args:
            text: Message text to send
            
        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.page:
            raise Exception("Page not initialized")
        
        try:
            # Find the message input box
            # WhatsApp Web uses different selectors - try multiple
            input_selectors = [
                'div[contenteditable="true"][data-testid="conversation-compose-box-input"]',
                'div[contenteditable="true"][data-tab="10"]',
                'div[contenteditable="true"][role="textbox"]',
                'div[contenteditable="true"][aria-label*="Type"]',
                'div[contenteditable="true"]'
            ]
            
            input_box = None
            for selector in input_selectors:
                try:
                    input_box = await self.page.wait_for_selector(selector, timeout=3000)
                    if input_box:
                        # Verify it's actually the input box
                        is_visible = await input_box.is_visible()
                        if is_visible:
                            break
                except PlaywrightTimeoutError:
                    continue
            
            if not input_box:
                logger.error("Could not find message input box")
                return False
            
            # Focus and clear any existing text
            await input_box.click()
            await asyncio.sleep(0.2)
            
            # Clear existing content
            await input_box.evaluate("el => el.innerText = ''")
            await asyncio.sleep(0.2)
            
            # Type the message character by character for natural typing
            await input_box.type(text, delay=30)
            
            # Wait a bit before sending
            await asyncio.sleep(0.3)
            
            # Press Enter to send
            # await input_box.press("Enter")
            
            logger.info(f"Message Typied in input box: {text[:50]}...")
            await asyncio.sleep(1)  # Wait for message to be sent
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending message: {e}", exc_info=True)
            return False
    
    async def check_new_messages(self) -> bool:
        """
        Check if there are new incoming messages in the current chat.
        
        Returns:
            True if new messages detected, False otherwise
        """
        try:
            messages = await self.get_last_messages(count=5)
            if not messages:
                return False
            print(messages)
            
            incomings = [i for i in messages if i['direction']=='incoming']
            if incomings:
                latest_incoming_message = incomings[-1]['text']
                print("latest_incoming_message != self.last_message",latest_incoming_message != self.last_message)
            
                if latest_incoming_message != self.last_message:
                    # Check if the latest message is incoming
                    print("messages and messages[-1]['direction'] == 'incoming'",messages and messages[-1]['direction'] == 'incoming')
                    if messages and messages[-1]['direction'] == 'incoming':
                        self.last_message = latest_incoming_message
                        return True
            

            # Check if there are new incoming messages
            # current_count = len(messages)
            # if current_count > self.last_message_count:
            #     # Check if the latest message is incoming
            #     if messages and messages[-1]['direction'] == 'incoming':
            #         self.last_message_count = current_count
            #         return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error checking new messages: {e}")
            return False
    
    async def is_chat_open(self) -> bool:
        """Check if a chat is currently open."""
        try:
            if not self.page:
                return False
            
            # Check for conversation panel
            panel = await self.page.query_selector('[data-scrolltracepolicy="wa.web.conversation.messages"]')
            return panel is not None
            
        except Exception:
            return False
    
    async def close(self):
        """Close browser and cleanup."""
        try:
            if self.context:
                await self.context.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")

