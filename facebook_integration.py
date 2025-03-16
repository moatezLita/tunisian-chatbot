import os
import json
import logging
import requests
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("facebook_bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class FacebookMessengerBot:
    """
    Handles integration with Facebook Messenger for the Tunisian chat bot
    """
    
    def __init__(self, page_access_token, verify_token, app=None):
        """
        Initialize the Facebook Messenger bot
        
        Args:
            page_access_token: Facebook page access token
            verify_token: Verification token for webhook
            app: Flask app (optional)
        """
        self.page_access_token = page_access_token
        self.verify_token = verify_token
        
        # Create Flask app if not provided
        if app is None:
            self.app = Flask(__name__)
        else:
            self.app = app
            
        # Set up routes
        self.setup_routes()
        
    def setup_routes(self):
        """Set up Flask routes for Facebook webhook"""
        
        @self.app.route('/webhook', methods=['GET'])
        def verify_webhook():
            """Verify webhook with Facebook"""
            mode = request.args.get('hub.mode')
            token = request.args.get('hub.verify_token')
            challenge = request.args.get('hub.challenge')
            
            if mode and token:
                if mode == 'subscribe' and token == self.verify_token:
                    logger.info("Webhook verified")
                    return challenge
                else:
                    logger.warning("Webhook verification failed")
                    return 'Verification failed', 403
                    
            return 'Invalid request', 400
            
        @self.app.route('/webhook', methods=['POST'])
        def webhook():
            """Handle incoming messages from Facebook"""
            data = request.json
            
            if data['object'] == 'page':
                for entry in data['entry']:
                    for messaging_event in entry['messaging']:
                        sender_id = messaging_event['sender']['id']
                        
                        # Handle message
                        if 'message' in messaging_event:
                            message_text = messaging_event['message'].get('text')
                            if message_text:
                                self.handle_message(sender_id, message_text)
                                
                return 'EVENT_RECEIVED', 200
            else:
                return 'Not a page subscription', 404
                
    def handle_message(self, sender_id, message_text):
        """
        Handle incoming message from user
        
        Args:
            sender_id: Facebook ID of the sender
            message_text: Text message from the user
        """
        # Process message with Tunisian dialect understanding
        # This is where you'll integrate with your cultural_context and transliteration modules
        
        # For now, just echo the message back
        response = f"Received: {message_text}"
        self.send_message(sender_id, response)
        
    def send_message(self, recipient_id, message_text):
        """
        Send message to user
        
        Args:
            recipient_id: Facebook ID of the recipient
            message_text: Text message to send
        """
        params = {
            "access_token": self.page_access_token
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": message_text
            }
        }
        
        response = requests.post(
            "https://graph.facebook.com/v13.0/me/messages",
            params=params,
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to send message: {response.text}")
            
    def run(self, host='0.0.0.0', port=5000):
        """Run the Flask app"""
        self.app.run(host=host, port=port)

def create_facebook_bot(config_path="config/facebook_config.json"):
    """
    Create a Facebook Messenger bot from config
    
    Args:
        config_path: Path to Facebook configuration file
        
    Returns:
        FacebookMessengerBot instance
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        return FacebookMessengerBot(
            page_access_token=config['page_access_token'],
            verify_token=config['verify_token']
        )
    except FileNotFoundError:
        logger.error(f"Config file not found at {config_path}")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Create a template config file
        template_config = {
            "page_access_token": "YOUR_PAGE_ACCESS_TOKEN",
            "verify_token": "YOUR_VERIFY_TOKEN"
        }
        
        with open(config_path, 'w') as f:
            json.dump(template_config, f, indent=4)
            
        logger.info(f"Template config file created at {config_path}")
        logger.info("Please update with your Facebook credentials")
        
        return None

if __name__ == "__main__":
    # Create and run the Facebook bot
    bot = create_facebook_bot()
    
    if bot:
        logger.info("Starting Facebook Messenger bot")
        bot.run()
    else:
        logger.info("Please update the config file with your Facebook credentials")