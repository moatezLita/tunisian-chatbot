import logging
import time
from cultural_context import TunisianCulturalContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_cultural_context():
    """Test the TunisianCulturalContext class"""
    print("Testing Tunisian Cultural Context")
    print("-" * 50)
    
    # Initialize cultural context
    context = TunisianCulturalContext()
    
    # Enrich cultural data
    print("Enriching cultural data...")
    context.enrich_cultural_data()
    
    # Test extraction
    test_texts = [
        "Ahla bik, kifech enti?",
        "N7eb nakol couscous w brik",
        "Nroh l Sidi Bou Said w Carthage ghoudwa"
    ]
    
    for text in test_texts:
        print(f"\nText: {text}")
        
        # Extract entities
        entities = context.extract_cultural_entities(text)
        print(f"Extracted entities: {entities}")
        
        # Get response suggestions
        suggestions = context.get_response_suggestions(text)
        if suggestions:
            print(f"Response suggestions:")
            for suggestion in suggestions:
                print(f"- {suggestion}")
                
        # Get cultural explanation
        explanation = context.get_cultural_explanation(text)
        if explanation:
            print(f"Cultural explanation:\n{explanation}")
    
    print("-" * 50)
    print("Test completed")

if __name__ == "__main__":
    test_cultural_context()