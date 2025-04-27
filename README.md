# Emilia
A Python-based command-line chatbot interface using OpenRouter AI models with autosave, typing effects, and customizable persona.

# OpenRouter Chatbot

A Python-based command-line chatbot interface using OpenRouter AI models.  
It features a smooth typing effect, autosaving chat history, dynamic persona customization, and basic model management commands.

---

## ✨ Features
- Easy-to-use command-line chat interface
- Typing effect for a realistic chat feel
- Automatic history saving and loading
- Model switching at runtime
- Dynamic system prompt for persona customization
- Helpful built-in commands (/help, /save, /load, /clear, /model)

---

## 🛠 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Aman489-art/Emilia.git
   cd Emilia

2. **Install dependencies**
   ```bash
   pip install httpx 

3. ## 🚀 Usage

  - Edit the main() function in backup.py:

  - Replace "APT-KEY" with your actual OpenRouter API key.
  
  - Set your preferred model name (e.g., "mistralai/mistral-7b-instruct:free").
  
  - Optionally, customize the default persona description.
   
4. ## Run the Script:
      ```bash
      python backup.py
      
5. ## Chat Commands
    - /help — List available commands
    
    - clear — Clear chat history
    
    - /save [filename] — Save conversation to file
    
    - /load [filename] — Load conversation from file
    
    - /model [model_name] — Change model on the fly
    
    - /exit or /quit — Exit the chat safely

## 📄 License

    This project is open-source and free to use!

**Made with ☕, 🎶, and a love for AI conversations.**
