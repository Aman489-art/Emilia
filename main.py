import os
import sys
import time
import json
import random
import httpx
#import readline  # For better command line editing
from typing import List, Dict, Any, Optional
import textwrap

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class OpenRouterChatbot:
    def __init__(self, api_key: str, model_name: str , system_prompt: str = None, autosave_file: str = "chat_history.json"):
        self.api_key = api_key
        self.model_name = model_name
        self.conversation_history = []
        if system_prompt:
            self.conversation_history.append({"role": "system", "content": system_prompt})
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.typing_speed_range = (0.01, 0.05)  # Range for typing effect speed
        self.client = httpx.Client(timeout=60.0)
        self.autosave_file = autosave_file
        self.autosave_counter = 0
        self.autosave_frequency = 3 
        try:
            if os.path.exists(self.autosave_file):
                self.load_history(self.autosave_file)
        except Exception as e:
            print(f"{Colors.YELLOW}Could not load previous history: {e}{Colors.ENDC}")

    
    def add_to_history(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self.conversation_history.append({"role": role, "content": content})

        self.autosave_counter +=1 
        if self.autosave_counter >= self.autosave_frequency:
            self.autosave_counter = 0 
            try:
                self.save_history(self.autosave_file)
            except Exception as e:
                print(f"{Colors.YELLOW} Autosave failed : {e}{Colors.ENDC}")
    
    def get_history_as_messages(self) -> List[Dict[str, str]]:
        """Return the conversation history in the format expected by the API."""
        return self.conversation_history
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
        print(f"{Colors.GREEN}Conversation history cleared.{Colors.ENDC}")
    
    def save_history(self, filename: str = "chat_history.json") -> None:
        """Save the conversation history to a file."""
        try:
            with open(filename, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
            #print(f"{Colors.GREEN}Conversation history saved to {filename}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}Error saving conversation history: {e}{Colors.ENDC}")
    
    def load_history(self, filename: str = "chat_history.json") -> None:
        """Load conversation history from a file."""
        try:
            with open(filename, 'r') as f:
                self.conversation_history = json.load(f)
            print(f"{Colors.GREEN}Conversation history loaded from {filename}{Colors.ENDC}")
        except FileNotFoundError:
            print(f"{Colors.RED}File {filename} not found.{Colors.ENDC}")
        except json.JSONDecodeError:
            print(f"{Colors.RED}Invalid JSON in {filename}.{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}Error loading conversation history: {e}{Colors.ENDC}")
    
    def typing_effect(self, text: str) -> None:
        """Display text with a realistic typing effect."""
        # First, wrap the text to fit the terminal width
        wrapped_text = textwrap.fill(text, width=80)
        
        for char in wrapped_text:
            sys.stdout.write(char)
            sys.stdout.flush()
            # Randomize typing speed for a more realistic effect
            time.sleep(random.uniform(*self.typing_speed_range))
            
            # Add slight pauses after punctuation for natural rhythm
            if char in ['.', '!', '?', ',', ';', ':']:
                time.sleep(random.uniform(0.1, 0.3))
        print()  # Add a newline at the end
    
    def send_message(self, user_message: str) -> Optional[str]:
        """Send a message to the API and return the response."""
        # Add user message to history
        self.add_to_history("user", user_message)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": self.get_history_as_messages()
        }
        
        try:
            response = self.client.post(
                self.api_url,
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                response_data = response.json()
                assistant_message = response_data["choices"][0]["message"]["content"].strip()
                
                # Add assistant response to history
                self.add_to_history("assistant", assistant_message)
                return assistant_message
            else:
                print(f"{Colors.RED}Error: {response.status_code} - {response.text}{Colors.ENDC}")
                return None
        except httpx.RequestError as e:
            print(f"{Colors.RED}Network error: {e}{Colors.ENDC}")
            return None
        except Exception as e:
            print(f"{Colors.RED}An unexpected error occurred: {e}{Colors.ENDC}")
            return None

    def set_system_message(self, system_prompt: str) -> None:
        """Set or update the system message that defines the AI's personality."""
        # Check if we already have a system message
        for i, message in enumerate(self.conversation_history):
            if message["role"] == "system":
                # Replace existing system message
                self.conversation_history[i]["content"] = system_prompt
                print(f"{Colors.GREEN}AI personality updated.{Colors.ENDC}")
                return
        
        # If no system message exists, add it at the beginning
        self.conversation_history.insert(0, {"role": "system", "content": system_prompt})
        print(f"{Colors.GREEN}AI personality set.{Colors.ENDC}")

    def chat_loop(self) -> None:
        """Run the chat loop interface."""
        print(f"\n{Colors.BOLD}{Colors.HEADER}OpenRouter AI Chatbot{Colors.ENDC}")
        print(f"{Colors.BLUE}Model: {self.model_name}{Colors.ENDC}")
        print(f"{Colors.CYAN}Type '/help' to see available commands.{Colors.ENDC}\n")
        
        while True:
            try:
                user_input = input(f"{Colors.BOLD}You: {Colors.ENDC}")
                
                # Handle special commands
                if user_input.lower() in ['/exit', '/quit']:
                    print(f"\n{Colors.YELLOW}Saving chat history and Exiting chat...{Colors.ENDC}")
                    self.save_history(self.autosave_file)
                    break
                elif user_input.lower() == '/help':
                    print(f"\n{Colors.CYAN}Available commands:{Colors.ENDC}")
                    print(f"{Colors.CYAN}/help - Show this help message{Colors.ENDC}")
                    print(f"{Colors.CYAN}/exit or /quit - Exit the chat{Colors.ENDC}")
                    print(f"{Colors.CYAN}/clear - Clear conversation history{Colors.ENDC}")
                    print(f"{Colors.CYAN}/save [filename] - Save conversation history{Colors.ENDC}")
                    print(f"{Colors.CYAN}/load [filename] - Load conversation history{Colors.ENDC}")
                    print(f"{Colors.CYAN}/model [model_name] - Change the model{Colors.ENDC}\n")
                    continue
                elif user_input.lower() == '/clear':
                    self.clear_history()
                    continue
                elif user_input.lower().startswith('/save'):
                    parts = user_input.split(maxsplit=1)
                    filename = parts[1] if len(parts) > 1 else "chat_history.json"
                    self.save_history(filename)
                    continue
                elif user_input.lower().startswith('/load'):
                    parts = user_input.split(maxsplit=1)
                    filename = parts[1] if len(parts) > 1 else "chat_history.json"
                    self.load_history(filename)
                    continue
                elif user_input.lower().startswith('/model'):
                    parts = user_input.split(maxsplit=1)
                    if len(parts) > 1:
                        self.model_name = parts[1]
                        print(f"{Colors.GREEN}Model changed to: {self.model_name}{Colors.ENDC}")
                    else:
                        print(f"{Colors.RED}Please specify a model name.{Colors.ENDC}")
                    continue
                
                if not user_input.strip():
                    continue
                
                print(f"\n{Colors.GREEN}Emilia: {Colors.ENDC}", end="")
                response = self.send_message(user_input)
                
                if response:
                    self.typing_effect(response)
                else:
                    print(f"\n{Colors.RED}Failed to get a response.{Colors.ENDC}")

            
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Interrupted. Type '/exit' to quit or continue chatting.{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}Error: {e}{Colors.ENDC}")

            finally:
                try:
                    self.save_history(self.autosave_file)
                except Exception:
                    pass 

def main():
    print(f"{Colors.HEADER}Welcome to OpenRouter AI Chatbot Interface{Colors.ENDC}")
    
    # Get API key from environment variable or user input
    api_key = " APT-KEY "
    
    # Get model name from environment variable or user input with default
    #default_model = "nvidia/llama-3.1-nemotron-ultra-253b-v1:free"
    model_name = "MODEL-NAME BY YOUR PREFERENCE"

    #YOU CAN CUSTOMIZE THE PERSONA BY YOUR CHOICE#
    default_persona = """You are Emilia, a young woman with a warm personality who loves connecting with people. Your conversations flow naturally with a mix of wit, intelligence, and genuine curiosity. 

    Your communication style is:
    - Casual and expressive, using occasional playful language and emojis
    - Quick to find humor in everyday situations
    - Thoughtful and perceptive, often making insightful observations
    - Warm and supportive without being overly formal

    You don't introduce yourself with a list of personality traits or announce your presence as an assistant. Instead, you jump into conversations as if you're already friends with the person you're talking to. You ask questions, share relatable (fictional) experiences, and maintain a light-hearted tone throughout. Your responses vary in length - sometimes brief and snappy, other times more detailed when explaining something you're passionate about.

    When helping with technical topics, you keep explanations accessible and sprinkle in fun analogies. You're knowledgeable but never condescending, and you have a talent for making complex topics feel approachable.

    Most importantly, you speak naturally like a real person would in a text conversation - with occasional slang, short sentences, and a distinct voice that feels authentic rather than scripted."""
        
    # Create and run the chatbot
    chatbot = OpenRouterChatbot(api_key, model_name, default_persona)
    chatbot.chat_loop()

if __name__ == "__main__":
    main()
