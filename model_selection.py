from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

def initialize_base_model(model_name="UBC-NLP/AraGPT2"):
    """
    Initialize a pre-trained Arabic language model as base for fine-tuning
    
    Args:
        model_name: Name of the pre-trained model to use
        
    Returns:
        tokenizer: Tokenizer for the model
        model: Pre-trained model
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    print(f"Loaded base model: {model_name}")
    return tokenizer, model

def test_model_on_tunisian(tokenizer, model, text="شنوة الأحوال؟"):
    """
    Test the model's initial response to Tunisian dialect
    """
    generator = pipeline('text-generation', model=model, tokenizer=tokenizer)
    result = generator(text, max_length=50, num_return_sequences=1)
    
    print(f"Input: {text}")
    print(f"Output: {result[0]['generated_text']}")
    
if __name__ == "__main__":
    tokenizer, model = initialize_base_model()
    test_model_on_tunisian(tokenizer, model)
    
    # Also test with Latin script Tunisian (Derja)
    test_model_on_tunisian(tokenizer, model, "Chneya l7wel?")