import json
import os
import re
import logging
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TunisianCulturalContext:
    """
    Handles Tunisian cultural context and expressions
    """
    
    def __init__(self, data_path="resources/cultural_context.json"):
        """
        Initialize the cultural context handler
        
        Args:
            data_path: Path to cultural context data file
        """
        self.data_path = data_path
        self.cultural_data = self.load_cultural_data()
        self.training_start_time = None
        self.estimated_completion_time = None
        
    def load_cultural_data(self):
        """
        Load cultural context data from file
        
        Returns:
            Dictionary with cultural context data
        """
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Cultural context file not found at {self.data_path}")
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            
            # Create a template data file
            template_data = {
                "expressions": {
                    "ahla bik": {
                        "meaning": "Hello/Welcome",
                        "context": "Common greeting in Tunisian dialect",
                        "variations": ["ahla", "ahla w sahla"]
                    },
                    "labess": {
                        "meaning": "How are you?",
                        "context": "Common greeting/question about well-being",
                        "variations": ["labess 3lik", "ça va"]
                    },
                    "barcha": {
                        "meaning": "A lot/very much",
                        "context": "Used to emphasize quantity or intensity",
                        "variations": ["barsha", "bezzef"]
                    }
                },
                "food": {
                    "couscous": {
                        "meaning": "Traditional Tunisian dish",
                        "context": "National dish made of semolina with vegetables and meat",
                        "variations": ["كسكسي"]
                    },
                    "lablebi": {
                        "meaning": "Tunisian chickpea soup",
                        "context": "Popular street food",
                        "variations": ["لبلابي"]
                    }
                },
                "places": {
                    "sidi bou said": {
                        "meaning": "Famous blue and white village",
                        "context": "Tourist destination near Tunis",
                        "variations": ["سيدي بو سعيد"]
                    }
                },
                "customs": {
                    "fitr": {
                        "meaning": "Eid al-Fitr celebration",
                        "context": "Celebration after Ramadan",
                        "variations": ["عيد الفطر", "l3id"]
                    }
                }
            }
            
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=4)
                
            logger.info(f"Created template cultural context file at {self.data_path}")
            return template_data
    
    def extract_cultural_entities(self, text):
        """
        Extract cultural entities from text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with cultural entities by category
        """
        entities = {}
        
        for category, items in self.cultural_data.items():
            found_items = []
            
            for item_name, item_data in items.items():
                # Check for the main item name
                if re.search(r'\b' + re.escape(item_name) + r'\b', text, re.IGNORECASE):
                    found_items.append(item_name)
                    continue
                    
                # Check for variations
                for variation in item_data.get("variations", []):
                    if re.search(r'\b' + re.escape(variation) + r'\b', text, re.IGNORECASE):
                        found_items.append(item_name)
                        break
                        
            if found_items:
                entities[category] = found_items
                
        return entities
    
    def get_cultural_context(self, entity, category):
        """
        Get cultural context for an entity
        
        Args:
            entity: Entity name
            category: Entity category
            
        Returns:
            Dictionary with cultural context
        """
        if category in self.cultural_data and entity in self.cultural_data[category]:
            return self.cultural_data[category][entity]
        return None
        
    def add_cultural_entity(self, category, entity, meaning, context, variations=None):
        """
        Add a new cultural entity to the data
        
        Args:
            category: Category of the entity
            entity: Name of the entity
            meaning: Meaning of the entity
            context: Cultural context of the entity
            variations: List of variations (optional)
            
        Returns:
            True if added successfully, False otherwise
        """
        if variations is None:
            variations = []
            
        # Create category if it doesn't exist
        if category not in self.cultural_data:
            self.cultural_data[category] = {}
            
        # Add entity
        self.cultural_data[category][entity] = {
            "meaning": meaning,
            "context": context,
            "variations": variations
        }
        
        # Save updated data
        try:
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(self.cultural_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error saving cultural data: {str(e)}")
            return False
            
    def get_response_suggestions(self, text):
        """
        Get response suggestions based on cultural context
        
        Args:
            text: Input text
            
        Returns:
            List of suggested responses
        """
        entities = self.extract_cultural_entities(text)
        suggestions = []
        
        for category, items in entities.items():
            for item in items:
                context = self.get_cultural_context(item, category)
                if context:
                    if category == "expressions":
                        if item == "ahla bik" or item == "ahla":
                            suggestions.append("Ahla bik! Chneya n3awnek?")
                        elif item == "labess":
                            suggestions.append("Hamdullah, enti labess?")
                        elif item == "barcha":
                            suggestions.append("Ih, barcha barcha!")
                    elif category == "food":
                        suggestions.append(f"T7eb {item}? Makla tounsia tayba barcha!")
                    elif category == "places":
                        suggestions.append(f"{item} blasa jmila fi tounes!")
                    elif category == "customs":
                        suggestions.append(f"{item} 3ada mohema fi thaqafetna.")
                        
        return suggestions
        
    def enrich_cultural_data(self):
        """
        Enrich the cultural data with more Tunisian content
        
        Returns:
            True if enriched successfully, False otherwise
        """
        # Start training timer
        self.start_training(total_items=100)
        
        # Add more expressions
        expressions = {
            "3aslema": {
                "meaning": "Hello/Hi",
                "context": "Casual greeting in Tunisian dialect",
                "variations": ["3aslama", "3asslema"]
            },
            "chbik": {
                "meaning": "What's wrong with you?",
                "context": "Used to ask what's bothering someone",
                "variations": ["chbik", "شبيك"]
            },
            "yezzi": {
                "meaning": "Enough/Stop it",
                "context": "Used to tell someone to stop doing something",
                "variations": ["yezzi", "يزي"]
            },
            "mela": {
                "meaning": "So/Then/Well",
                "context": "Used as a filler word or to transition in conversation",
                "variations": ["mela", "ملا"]
            },
            "sahit": {
                "meaning": "Thank you/Bless you",
                "context": "Used to thank someone or as a response to a sneeze",
                "variations": ["sahit", "صحيت"]
            }
        }
        
        # Add more food items
        foods = {
            "brik": {
                "meaning": "Tunisian pastry with egg and tuna",
                "context": "Popular during Ramadan",
                "variations": ["brik", "بريك"]
            },
            "makroudh": {
                "meaning": "Semolina cake with dates",
                "context": "Traditional sweet pastry",
                "variations": ["makroudh", "مقروض"]
            },
            "ojja": {
                "meaning": "Tunisian egg dish with tomatoes and peppers",
                "context": "Popular breakfast or lunch dish",
                "variations": ["ojja", "عجة"]
            },
            "kafteji": {
                "meaning": "Fried vegetables with egg",
                "context": "Popular street food",
                "variations": ["kafteji", "كفتاجي"]
            },
            "mlawi": {
                "meaning": "Tunisian layered flatbread",
                "context": "Often eaten with honey or cheese",
                "variations": ["mlawi", "ملاوي"]
            }
        }
        
        # Add more places
        places = {
            "carthage": {
                "meaning": "Ancient city and archaeological site",
                "context": "Historical site near Tunis",
                "variations": ["carthage", "قرطاج"]
            },
            "djerba": {
                "meaning": "Island in southern Tunisia",
                "context": "Popular tourist destination",
                "variations": ["djerba", "جربة"]
            },
            "kairouan": {
                "meaning": "City in central Tunisia",
                "context": "Known for the Great Mosque and Islamic heritage",
                "variations": ["kairouan", "القيروان"]
            },
            "el jem": {
                "meaning": "Town with Roman amphitheater",
                "context": "Home to one of the best-preserved Roman amphitheaters",
                "variations": ["el jem", "الجم"]
            },
            "matmata": {
                "meaning": "Berber town with underground houses",
                "context": "Famous for troglodyte dwellings and Star Wars filming location",
                "variations": ["matmata", "مطماطة"]
            }
        }
        
        # Add more customs
        customs = {
            "henna": {
                "meaning": "Traditional body art",
                "context": "Used in weddings and celebrations",
                "variations": ["henna", "حناء"]
            },
            "ramadan": {
                "meaning": "Holy month of fasting",
                "context": "Important religious observance",
                "variations": ["ramadan", "رمضان"]
            },
            "chachia": {
                "meaning": "Traditional Tunisian hat",
                "context": "Part of traditional male attire",
                "variations": ["chachia", "شاشية"]
            },
            "mezoued": {
                "meaning": "Traditional Tunisian bagpipe music",
                "context": "Popular folk music style",
                "variations": ["mezoued", "مزود"]
            },
            "khomsa": {
                "meaning": "Hand-shaped amulet",
                "context": "Used for protection against evil eye",
                "variations": ["khomsa", "خمسة"]
            }
        }
        
        # Add new category: Tunisian slang
        slang = {
            "mrigel": {
                "meaning": "Cool/Awesome/Manly",
                "context": "Used to describe something impressive or someone brave",
                "variations": ["mrigel", "مريقل"]
            },
            "fissa": {
                "meaning": "Quickly/In a hurry",
                "context": "Used to tell someone to do something quickly",
                "variations": ["fissa", "فيسع"]
            },
            "3ayech": {
                "meaning": "Living the life/Enjoying",
                "context": "Used to describe someone who is enjoying life",
                "variations": ["3ayech", "عايش"]
            },
            "7ala": {
                "meaning": "Situation/State",
                "context": "Often used to describe a bad or chaotic situation",
                "variations": ["7ala", "حالة"]
            },
            "meskina": {
                "meaning": "Poor thing/Unfortunate",
                "context": "Expression of sympathy",
                "variations": ["meskina", "مسكينة"]
            }
        }
        
        # Add all new data
        try:
            # Update progress
            self.update_training_progress(20)
            
            # Add expressions
            for entity, data in expressions.items():
                if "expressions" not in self.cultural_data:
                    self.cultural_data["expressions"] = {}
                if entity not in self.cultural_data["expressions"]:
                    self.cultural_data["expressions"][entity] = data
            
            # Update progress
            self.update_training_progress(40)
                    
            # Add foods
            for entity, data in foods.items():
                if "food" not in self.cultural_data:
                    self.cultural_data["food"] = {}
                if entity not in self.cultural_data["food"]:
                    self.cultural_data["food"][entity] = data
            
            # Update progress
            self.update_training_progress(60)
                    
            # Add places
            for entity, data in places.items():
                if "places" not in self.cultural_data:
                    self.cultural_data["places"] = {}
                if entity not in self.cultural_data["places"]:
                    self.cultural_data["places"][entity] = data
                    
            # Add customs
            for entity, data in customs.items():
                if "customs" not in self.cultural_data:
                    self.cultural_data["customs"] = {}
                if entity not in self.cultural_data["customs"]:
                    self.cultural_data["customs"][entity] = data
                    
            # Add slang
            if "slang" not in self.cultural_data:
                self.cultural_data["slang"] = {}
            for entity, data in slang.items():
                if entity not in self.cultural_data["slang"]:
                    self.cultural_data["slang"][entity] = data
                    
            # Save updated data
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(self.cultural_data, f, ensure_ascii=False, indent=4)
            
            # Complete training
            self.complete_training()
                
            logger.info("Cultural data enriched successfully")
            return True
        except Exception as e:
            logger.error(f"Error enriching cultural data: {str(e)}")
            return False
            
    def get_cultural_explanation(self, text):
        """
        Get a cultural explanation for text
        
        Args:
            text: Input text
            
        Returns:
            Cultural explanation string
        """
        entities = self.extract_cultural_entities(text)
        if not entities:
            return None
            
        explanation = "Cultural context:\n"
        for category, items in entities.items():
            explanation += f"\n{category.capitalize()}:\n"
            for item in items:
                context = self.get_cultural_context(item, category)
                if context:
                    explanation += f"- {item}: {context['meaning']} - {context['context']}\n"
                    
        return explanation