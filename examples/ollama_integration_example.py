#!/usr/bin/env python3
"""
RoboEyes Desktop - Ollama Integration Example

This example demonstrates how to integrate RoboEyes with Ollama for an AI assistant
with visual feedback. The eyes react to different states of the AI conversation.

Requirements:
- Ollama installed and running locally
- requests library: pip install requests
"""

import sys
import os
import requests
import json
import threading
import time

# Add the src directory to the path so we can import the desktop modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from roboeyes.desktop_roboeyes import (
    DesktopRoboEyes, DEFAULT, TIRED, ANGRY, HAPPY, FROZEN, SCARY, CURIOUS,
    ON, OFF
)
from desktop.config import RoboEyesConfig

class OllamaRoboEyes:
    """
    Integration class that connects RoboEyes with Ollama LLM.
    
    This class manages the visual feedback based on AI conversation states:
    - Idle: Default mood with auto-blinker
    - Thinking: Curious mood with specific animation
    - Responding: Happy mood during response generation
    - Error: Angry mood for errors
    """
    
    def __init__(self, ollama_url="http://localhost:11434", model="llama2"):
        """
        Initialize the Ollama RoboEyes integration.
        
        Args:
            ollama_url: URL of the Ollama API
            model: Model name to use (e.g., "llama2", "mistral", "codellama")
        """
        self.ollama_url = ollama_url
        self.model = model
        self.conversation_history = []
        
        # Create RoboEyes configuration optimized for AI assistant
        config = RoboEyesConfig(
            window_width=600,
            window_height=400,
            display_width=128,
            display_height=64,
            frame_rate=60,
            auto_blinker=True,
            blink_interval=2.0,
            idle_mode=True,
            idle_interval=3.0
        )
        
        # Initialize RoboEyes
        self.robo = DesktopRoboEyes(config=config)
        
        # Set initial state
        self.set_idle_state()
        
        # Start the RoboEyes in a separate thread
        self.robo_thread = threading.Thread(target=self.robo.run, daemon=True)
        self.robo_thread.start()
        
        print("RoboEyes Ollama Assistant initialized!")
        print(f"Using model: {model}")
        print("Commands:")
        print("  - Type your message and press Enter")
        print("  - Type 'quit' to exit")
        print("  - Type 'clear' to clear conversation history")
        print()
    
    def set_idle_state(self):
        """Set eyes to idle state - waiting for input."""
        self.robo.mood = DEFAULT
        self.robo.set_auto_blinker(ON, 2, 1)
        self.robo.set_idle_mode(ON, 3, 2)
    
    def set_thinking_state(self):
        """Set eyes to thinking state - processing input."""
        self.robo.mood = CURIOUS
        self.robo.set_auto_blinker(OFF)
        self.robo.set_idle_mode(OFF)
        # Create a thinking animation sequence
        seq = self.robo.sequences.add("thinking")
        seq.step(0, lambda r: r.set_position(7))    # Look left
        seq.step(500, lambda r: r.set_position(6))  # Look right
        seq.step(1000, lambda r: r.set_position(0)) # Look center
        seq.start()
    
    def set_responding_state(self):
        """Set eyes to responding state - generating response."""
        self.robo.mood = HAPPY
        self.robo.set_auto_blinker(ON, 1, 0.5)  # Faster blinking
        self.robo.set_idle_mode(OFF)
    
    def set_error_state(self):
        """Set eyes to error state - something went wrong."""
        self.robo.mood = ANGRY
        self.robo.set_auto_blinker(OFF)
        self.robo.set_idle_mode(OFF)
        self.robo.confuse()  # Show confusion animation
    
    def check_ollama_connection(self):
        """Check if Ollama is running and accessible."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def send_message(self, message):
        """
        Send a message to Ollama and get the response.
        
        Args:
            message: User message to send to the AI
            
        Returns:
            AI response string or None if error
        """
        # Set thinking state
        self.set_thinking_state()
        
        try:
            # Prepare the request
            data = {
                "model": self.model,
                "prompt": message,
                "stream": False
            }
            
            # Send request to Ollama
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                # Set responding state
                self.set_responding_state()
                
                result = response.json()
                ai_response = result.get("response", "").strip()
                
                # Add to conversation history
                self.conversation_history.append({"user": message, "ai": ai_response})
                
                # Return to idle state after a moment
                threading.Timer(2.0, self.set_idle_state).start()
                
                return ai_response
            else:
                self.set_error_state()
                return f"Error: HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            self.set_error_state()
            return "Error: Request timed out. Ollama might be busy."
        except requests.exceptions.RequestException as e:
            self.set_error_state()
            return f"Error: {str(e)}"
        except json.JSONDecodeError:
            self.set_error_state()
            return "Error: Invalid response from Ollama"
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
        print("Conversation history cleared.")
    
    def run_chat(self):
        """Run the interactive chat loop."""
        # Check Ollama connection
        if not self.check_ollama_connection():
            print(f"Error: Cannot connect to Ollama at {self.ollama_url}")
            print("Make sure Ollama is running: ollama serve")
            return
        
        print("RoboEyes AI Assistant ready! Watch the eyes for visual feedback.")
        print()
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'clear':
                    self.clear_history()
                    continue
                elif not user_input:
                    continue
                
                # Send message and get response
                print("AI: ", end="", flush=True)
                response = self.send_message(user_input)
                
                if response:
                    print(response)
                else:
                    print("No response received.")
                
                print()
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                self.set_error_state()
        
        print("Goodbye!")

def main():
    """Main function to run the Ollama RoboEyes integration."""
    # You can customize these parameters
    ollama_url = "http://localhost:11434"
    model = "llama2"  # Change to your preferred model
    
    try:
        # Create and run the integration
        assistant = OllamaRoboEyes(ollama_url=ollama_url, model=model)
        assistant.run_chat()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()