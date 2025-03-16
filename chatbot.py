import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from cultural_context import TunisianCulturalContext
from transliteration import TunisianTransliterator

class TunisianChatbot:
    def __init__(self, model_path=None):
        """
        Initialize the Tunisian dialect chatbot
        
        Args:
            model_path: Path to the fine-tuned model, or None to use a pre-trained model
        """
        # Initialize the transliterator
        self.transliterator = TunisianTransliterator()
        
        # Initialize the cultural context processor
        self.context_processor = TunisianCulturalContext()
        
        # Update the model loading section in chatbot.py
        # Load the model
        if model_path and os.path.exists(model_path):
            print(f"Loading fine-tuned model from {model_path}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForCausalLM.from_pretrained(model_path)
        else:
            print("Loading pre-trained Arabic model")
            model_name = "aubmindlab/aragpt2-base"  # Correct model name
            
            # Import the necessary preprocessing
            try:
                from arabert.preprocess import ArabertPreprocessor
                self.arabert_prep = ArabertPreprocessor(model_name=model_name)
                self.use_preprocessor = True
            except ImportError:
                print("ArabertPreprocessor not found. Installing arabert package...")
                import subprocess
                subprocess.check_call(["pip", "install", "arabert"])
                from arabert.preprocess import ArabertPreprocessor
                self.arabert_prep = ArabertPreprocessor(model_name=model_name)
                self.use_preprocessor = True
                
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
        
        # Check if GPU is available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
        # Create text generation pipeline
        self.generator = pipeline('text-generation', model=self.model, tokenizer=self.tokenizer)
        
        print(f"Chatbot initialized on {self.device}")
    
    def generate_response(self, user_input, max_length=100):
        """
        Generate a response to the user input
        
        Args:
            user_input: User input text in Tunisian dialect (any script)
            max_length: Maximum length of the generated response
            
        Returns:
            Generated response in the same script as the input
        """
        # Normalize input to Arabic script and detect original script
        normalized_input, original_script = self.transliterator.normalize_input(user_input)
        
        # Apply ArabertPreprocessor if available
        if hasattr(self, 'use_preprocessor') and self.use_preprocessor:
            normalized_input = self.arabert_prep.preprocess(normalized_input)
        
        # Generate response
        response = self.generator(
            normalized_input, 
            max_length=max_length, 
            num_return_sequences=1,
            pad_token_id=self.tokenizer.eos_token_id,
            num_beams=5,
            top_p=0.9,
            repetition_penalty=2.0,
            no_repeat_ngram_size=2
        )[0]['generated_text']
        
        # Extract only the generated part (remove the input)
        generated_part = response[len(normalized_input):].strip()
        
        # Enhance with cultural context
        enhanced_response = self.context_processor.enhance_response(normalized_input, generated_part)
        
        # Format output to match the original script
        formatted_response = self.transliterator.format_output(enhanced_response, original_script)
        
        return formatted_response
    
    def chat(self):
        """
        Start an interactive chat session
        """
        print("Tunisian Dialect Chatbot")
        print("Type 'exit' to end the conversation")
        print("-" * 50)
        
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Chatbot: Ma3 essalema! (Goodbye!)")
                break
                
            response = self.generate_response(user_input)
            print(f"Chatbot: {response}")

if __name__ == "__main__":
    # Initialize the chatbot
    # If you have a fine-tuned model, specify the path:
    # chatbot = TunisianChatbot("model/final_model")
    chatbot = TunisianChatbot()
    
    # Start the chat
    chatbot.chat()