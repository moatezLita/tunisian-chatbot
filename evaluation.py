import json
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from chatbot import TunisianChatbot

class TunisianChatbotEvaluator:
    def __init__(self, chatbot, test_data_path="data/evaluation_data.json"):
        """
        Initialize the evaluator
        
        Args:
            chatbot: Instance of TunisianChatbot
            test_data_path: Path to the test data file
        """
        self.chatbot = chatbot
        self.test_data = self._load_test_data(test_data_path)
        
    def _load_test_data(self, path):
        """Load test data from a JSON file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Test data file not found at {path}. Creating a sample one.")
            # Create a sample test data file
            sample_data = {
                "dialect_identification": [
                    {"text": "ahla bik, chneya l7wel?", "is_tunisian": True},
                    {"text": "كيف حالك؟", "is_tunisian": False},  # MSA
                    {"text": "شنية الأحوال متاعك؟", "is_tunisian": True},
                    {"text": "ماذا تفعل اليوم؟", "is_tunisian": False}  # MSA
                ],
                "cultural_understanding": [
                    {"input": "نحب ناكل كسكسي", "expected_entities": ["food"]},
                    {"input": "باش نمشي لتونس غدوة", "expected_entities": ["places"]},
                    {"input": "صباح الخير، كيفاش صحتك اليوم؟", "expected_entities": ["greetings"]}
                ],
                "conversation_pairs": [
                    {"input": "ahla, chneya esmek?", "expected_response_contains": ["esm", "ism", "اسم"]},
                    {"input": "منين أنت؟", "expected_response_contains": ["من", "تونس", "بلاد"]},
                    {"input": "شنوة تحب تاكل؟", "expected_response_contains": ["أكل", "كسكسي", "طعام"]}
                ]
            }
            
            # Create directory if it doesn't exist
            import os
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Save the sample test data
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(sample_data, f, ensure_ascii=False, indent=4)
                
            return sample_data
    
    def evaluate_dialect_identification(self):
        """
        Evaluate the chatbot's ability to identify Tunisian dialect
        
        Returns:
            Dictionary with evaluation metrics
        """
        from cultural_context import TunisianCulturalContext
        context_processor = TunisianCulturalContext()
        
        y_true = []
        y_pred = []
        
        for item in self.test_data["dialect_identification"]:
            text = item["text"]
            is_tunisian = item["is_tunisian"]
            
            # Extract cultural entities
            entities = context_processor.extract_cultural_entities(text)
            
            # If any entities are found, consider it Tunisian
            predicted_tunisian = len(entities) > 0
            
            y_true.append(is_tunisian)
            y_pred.append(predicted_tunisian)
        
        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary')
        
        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1
        }
    
    def evaluate_cultural_understanding(self):
        """
        Evaluate the chatbot's cultural understanding
        
        Returns:
            Dictionary with evaluation metrics
        """
        from cultural_context import TunisianCulturalContext
        context_processor = TunisianCulturalContext()
        
        correct = 0
        total = 0
        
        for item in self.test_data["cultural_understanding"]:
            input_text = item["input"]
            expected_entities = set(item["expected_entities"])
            
            # Extract cultural entities
            entities = context_processor.extract_cultural_entities(input_text)
            detected_entities = set(entities.keys())
            
            # Check if all expected entities were detected
            if expected_entities.issubset(detected_entities):
                correct += 1
            
            total += 1
        
        accuracy = correct / total if total > 0 else 0
        
        return {
            "accuracy": accuracy,
            "correct": correct,
            "total": total
        }
    
    def evaluate_conversation(self):
        """
        Evaluate the chatbot's conversation abilities
        
        Returns:
            Dictionary with evaluation metrics
        """
        correct = 0
        total = 0
        
        for item in self.test_data["conversation_pairs"]:
            input_text = item["input"]
            expected_phrases = item["expected_response_contains"]
            
            # Generate response
            response = self.chatbot.generate_response(input_text)
            
            # Check if any expected phrase is in the response
            contains_expected = any(phrase.lower() in response.lower() for phrase in expected_phrases)
            
            if contains_expected:
                correct += 1
            
            total += 1
        
        accuracy = correct / total if total > 0 else 0
        
        return {
            "accuracy": accuracy,
            "correct": correct,
            "total": total
        }
    
    def run_evaluation(self):
        """
        Run all evaluations and print results
        
        Returns:
            Dictionary with all evaluation results
        """
        print("Evaluating Tunisian Dialect Chatbot")
        print("-" * 50)
        
        # Evaluate dialect identification
        dialect_results = self.evaluate_dialect_identification()
        print("\nDialect Identification Results:")
        print(f"Accuracy: {dialect_results['accuracy']:.2f}")
        print(f"Precision: {dialect_results['precision']:.2f}")
        print(f"Recall: {dialect_results['recall']:.2f}")
        print(f"F1 Score: {dialect_results['f1']:.2f}")
        
        # Evaluate cultural understanding
        cultural_results = self.evaluate_cultural_understanding()
        print("\nCultural Understanding Results:")
        print(f"Accuracy: {cultural_results['accuracy']:.2f} ({cultural_results['correct']}/{cultural_results['total']})")
        
        # Evaluate conversation
        conversation_results = self.evaluate_conversation()
        print("\nConversation Results:")
        print(f"Accuracy: {conversation_results['accuracy']:.2f} ({conversation_results['correct']}/{conversation_results['total']})")
        
        # Overall results
        overall_accuracy = (dialect_results['accuracy'] + cultural_results['accuracy'] + conversation_results['accuracy']) / 3
        print("\nOverall Results:")
        print(f"Average Accuracy: {overall_accuracy:.2f}")
        
        return {
            "dialect_identification": dialect_results,
            "cultural_understanding": cultural_results,
            "conversation": conversation_results,
            "overall_accuracy": overall_accuracy
        }

if __name__ == "__main__":
    # Initialize the chatbot
    chatbot = TunisianChatbot()
    
    # Initialize the evaluator
    evaluator = TunisianChatbotEvaluator(chatbot)
    
    # Run evaluation
    results = evaluator.run_evaluation()