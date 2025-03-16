import re
import logging

logger = logging.getLogger(__name__)

class TunisianTransliterator:
    """
    Handles transliteration between Arabic script and Latin script for Tunisian dialect
    """
    
    def __init__(self):
        """Initialize the transliterator with mapping tables"""
        # Arabic to Latin mapping
        self.ar_to_lat = {
            'ا': 'a', 'أ': 'a', 'إ': 'i', 'آ': 'e',
            'ب': 'b', 'ت': 't', 'ث': 'th',
            'ج': 'j', 'ح': '7', 'خ': 'kh',
            'د': 'd', 'ذ': 'dh', 'ر': 'r',
            'ز': 'z', 'س': 's', 'ش': 'ch',
            'ص': 's', 'ض': 'dh', 'ط': 't',
            'ظ': 'th', 'ع': '3', 'غ': 'gh',
            'ف': 'f', 'ق': '9', 'ك': 'k',
            'ل': 'l', 'م': 'm', 'ن': 'n',
            'ه': 'h', 'ة': 'a', 'و': 'w',
            'ي': 'i', 'ى': 'a', 'ء': '\'',
            'ئ': 'i', 'ؤ': 'w', 'َ': 'a',
            'ُ': 'u', 'ِ': 'i', 'ّ': '',
            'ْ': '', '٠': '0', '١': '1',
            '٢': '2', '٣': '3', '٤': '4',
            '٥': '5', '٦': '6', '٧': '7',
            '٨': '8', '٩': '9'
        }
        
        # Latin to Arabic mapping (simplified for common Tunisian dialect patterns)
        self.lat_to_ar = {
            'a': 'ا', 'e': 'ا', 'i': 'ي',
            'o': 'و', 'u': 'و', 'y': 'ي',
            'b': 'ب', 't': 'ت', 'th': 'ث',
            'j': 'ج', '7': 'ح', 'kh': 'خ',
            'd': 'د', 'dh': 'ذ', 'r': 'ر',
            'z': 'ز', 's': 'س', 'ch': 'ش',
            'sh': 'ش', '9': 'ق', 'k': 'ك',
            'l': 'ل', 'm': 'م', 'n': 'ن',
            'h': 'ه', 'w': 'و', '3': 'ع',
            'gh': 'غ', 'f': 'ف', 'g': 'ق',
            '5': 'خ', '8': 'ق', '2': 'ء'
        }
        
        # Common Tunisian dialect patterns
        self.patterns = {
            # Numbers used as letters
            '3': 'ع', '7': 'ح', '9': 'ق', '5': 'خ', '8': 'ق', '2': 'ء',
            # Common digraphs
            'ch': 'ش', 'th': 'ث', 'gh': 'غ', 'kh': 'خ', 'dh': 'ذ'
        }
        
    def is_arabic_script(self, text):
        """
        Determine if text is primarily in Arabic script
        
        Args:
            text: Input text
            
        Returns:
            Boolean indicating if text is primarily in Arabic script
        """
        # Arabic Unicode block ranges
        arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
        
        # Count Arabic characters
        arabic_chars = len(arabic_pattern.findall(text))
        
        # If more than 30% of characters are Arabic, consider it Arabic script
        return arabic_chars > len(text) * 0.3
    
    def arabic_to_latin(self, text):
        """
        Convert Arabic script to Latin transliteration
        
        Args:
            text: Text in Arabic script
            
        Returns:
            Text in Latin script
        """
        result = ""
        i = 0
        while i < len(text):
            if text[i] in self.ar_to_lat:
                result += self.ar_to_lat[text[i]]
            else:
                result += text[i]
            i += 1
        
        return result
    
    def latin_to_arabic(self, text):
        """
        Convert Latin transliteration to Arabic script
        
        Args:
            text: Text in Latin script
            
        Returns:
            Text in Arabic script
        """
        # First, handle multi-character patterns
        for pattern, replacement in self.patterns.items():
            text = text.replace(pattern, f"_{replacement}_")
            
        # Then convert character by character
        result = ""
        i = 0
        while i < len(text):
            if text[i] == '_':
                # Skip the marker characters
                i += 1
                continue
                
            if i < len(text) - 1 and text[i:i+2] in self.lat_to_ar:
                # Handle digraphs
                result += self.lat_to_ar[text[i:i+2]]
                i += 2
            elif text[i] in self.lat_to_ar:
                # Handle single characters
                result += self.lat_to_ar[text[i]]
                i += 1
            else:
                # Pass through characters not in the mapping
                result += text[i]
                i += 1
                
        return result
    
    def auto_transliterate(self, text):
        """
        Automatically detect script and transliterate accordingly
        
        Args:
            text: Input text in either Arabic or Latin script
            
        Returns:
            Text transliterated to the other script
        """
        if self.is_arabic_script(text):
            return self.arabic_to_latin(text)
        else:
            return self.latin_to_arabic(text)
    
    def normalize_tunisian_text(self, text):
        """
        Normalize Tunisian text by standardizing common variations
        
        Args:
            text: Input text in Tunisian dialect
            
        Returns:
            Normalized text
        """
        # Standardize number-letter substitutions
        substitutions = {
            '2': 'ء', '3': 'ع', '5': 'خ', '7': 'ح', '8': 'ق', '9': 'ق',
            'é': 'e', 'è': 'e', 'ê': 'e', 'à': 'a', 'ç': 's'
        }
        
        for orig, repl in substitutions.items():
            text = text.replace(orig, repl)
            
        return text
    
    def detect_dialect_script_mix(self, text):
        """
        Detect and report on mixed script usage in Tunisian dialect text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with script analysis
        """
        # Arabic Unicode block ranges
        arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
        
        # Latin Unicode block ranges
        latin_pattern = re.compile(r'[a-zA-Z0-9]')
        
        # Count characters
        arabic_chars = len(arabic_pattern.findall(text))
        latin_chars = len(latin_pattern.findall(text))
        total_chars = len(text.strip())
        
        # Calculate percentages
        arabic_percent = arabic_chars / total_chars * 100 if total_chars > 0 else 0
        latin_percent = latin_chars / total_chars * 100 if total_chars > 0 else 0
        
        # Determine primary script
        if arabic_percent > latin_percent:
            primary_script = "Arabic"
        elif latin_percent > arabic_percent:
            primary_script = "Latin"
        else:
            primary_script = "Mixed"
            
        return {
            "primary_script": primary_script,
            "arabic_percent": arabic_percent,
            "latin_percent": latin_percent,
            "is_mixed": arabic_percent > 10 and latin_percent > 10
        }

if __name__ == "__main__":
    # Test the transliterator
    transliterator = TunisianTransliterator()
    
    # Test Arabic to Latin
    arabic_text = "أهلا كيفاش لاباس عليك؟"
    latin_result = transliterator.arabic_to_latin(arabic_text)
    print(f"Arabic to Latin: {arabic_text} -> {latin_result}")
    
    # Test Latin to Arabic
    latin_text = "ahla kifech labess 3lik?"
    arabic_result = transliterator.latin_to_arabic(latin_text)
    print(f"Latin to Arabic: {latin_text} -> {arabic_result}")
    
    # Test auto-detection
    mixed_text = "ahla بيك labess?"
    auto_result = transliterator.auto_transliterate(mixed_text)
    print(f"Auto-transliterate: {mixed_text} -> {auto_result}")
    
    # Test dialect script mix detection
    mix_analysis = transliterator.detect_dialect_script_mix(mixed_text)
    print(f"Script mix analysis: {mix_analysis}")
    
    # Interactive test
    print("\nInteractive test (type 'exit' to quit):")
    while True:
        user_input = input("Enter Tunisian text in any script: ")
        if user_input.lower() == 'exit':
            break
            
        script = transliterator.detect_script(user_input)
        normalized, original_script = transliterator.normalize_input(user_input)
        
        print(f"Detected script: {script}")
        print(f"Normalized (Arabic): {normalized}")
        print(f"Formatted output: {transliterator.format_output(normalized, original_script)}")
        print("-" * 50)
    
    # Create a comprehensive mapping file
    def create_comprehensive_mapping(output_path="resources/comprehensive_transliteration_map.json"):
        """Create a comprehensive transliteration mapping file for Tunisian dialect"""
        comprehensive_mapping = {
            # Basic Arabic alphabet
            "a": "ا", "b": "ب", "t": "ت", "th": "ث",
            "j": "ج", "7": "ح", "kh": "خ", "d": "د",
            "dh": "ذ", "r": "ر", "z": "ز", "s": "س",
            "sh": "ش", "S": "ص", "D": "ض", "T": "ط",
            "Z": "ظ", "3": "ع", "gh": "غ", "f": "ف",
            "q": "ق", "k": "ك", "l": "ل", "m": "م",
            "n": "ن", "h": "ه", "w": "و", "y": "ي",
            
            # Numbers used as letters in Arabizi
            "2": "ء", "5": "خ", "6": "ط", "8": "ق", "9": "ق",
            
            # Vowels and diacritics
            "aa": "ا", "ee": "ي", "ii": "ي", "oo": "و", "uu": "و",
            "ou": "و", "ei": "اي", "ai": "اي", "ey": "اي", "ay": "اي",
            "aw": "او", "ao": "او",
            
            # Common Tunisian dialect digraphs
            "ch": "ش", "dh": "ذ", "gh": "غ", "kh": "خ", "th": "ث",
            "dj": "ج", "tj": "ج",
            
            # Common Tunisian dialect words and patterns
            "el": "ال", "al": "ال", "elli": "اللي", "wl": "ول",
            "fi": "في", "bi": "بي", "ki": "كي", "mi": "مي",
            "ma": "ما", "la": "لا", "ya": "يا", "wa": "وا",
            
            # French-influenced spellings common in Tunisian dialect
            "é": "ي", "è": "ا", "ê": "ا", "à": "ا", "ç": "س",
            "ou": "و", "au": "و", "eau": "و", "ai": "اي",
            
            # Special Tunisian dialect characters
            "g": "ق", "v": "ف", "p": "ب"
        }
        
        # Create directory if it doesn't exist
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the comprehensive mapping
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_mapping, f, ensure_ascii=False, indent=4)
            
        print(f"Comprehensive mapping created at {output_path}")
        return comprehensive_mapping
    
    # Create the comprehensive mapping
    transliterator.create_comprehensive_mapping = create_comprehensive_mapping
    transliterator.create_comprehensive_mapping()