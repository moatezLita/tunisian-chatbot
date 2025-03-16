# Tunisian Dialect Chat Project

This README provides a comprehensive guide to set up and run the Tunisian Dialect Chat project, which includes fine-tuning language models for Tunisian Arabic dialect processing and a cultural context system.

## Project Overview

The Tunisian Dialect Chat project aims to create a conversational AI system that understands and responds in Tunisian Arabic dialect. It includes:

- Fine-tuning of language models on Tunisian dialect data
- Cultural context processing for Tunisian expressions and references
- Transliteration between Arabic and Latin scripts (Arabizi)
- A chat interface for interacting with the model

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- PyTorch
- CUDA-compatible GPU (recommended for faster training)

### Installation

1. Clone the repository or download the project files to your local machine:
```bash
git clone https://github.com/yourusername/tunisian-chat.git
cd c:\Users\moate\Desktop\Tunisian-chat
```

2. Install the required dependencies:
```bash
pip install torch transformers datasets pandas numpy tqdm tensorboard fastapi uvicorn python-multipart jinja2 requests
```

3. Create the necessary directories:
```bash
mkdir -p data models resources logs
```

## Project Structure

```
tunisian-chat/
├── app.py                    # FastAPI application
├── cultural_context.py       # Cultural context processing
├── fine_tuning.py            # Model fine-tuning
├── transliteration.py        # Arabic-Latin transliteration
├── test_cultural_context.py  # Test script for cultural context
├── create_sample_data.py     # Script to create sample data
├── data/                     # Training and test data
├── models/                   # Fine-tuned models
├── resources/                # Cultural context resources
├── logs/                     # Training and application logs
├── static/                   # Static files for web interface
└── templates/                # HTML templates
```

## Usage Guide

### 1. Create Sample Data

First, create some sample Tunisian dialect data for testing:

```bash
python c:\Users\moate\Desktop\Tunisian-chat\create_sample_data.py
```

### 2. Initialize Cultural Context

Initialize and test the cultural context system:

```bash
python c:\Users\moate\Desktop\Tunisian-chat\test_cultural_context.py
```

### 3. Fine-tune the Model

Edit the fine_tuning.py file to use your data files and run:

```bash
python c:\Users\moate\Desktop\Tunisian-chat\fine_tuning.py
```

For a quick test with minimal resources, modify the main section of fine_tuning.py:

```python
if __name__ == "__main__":
    # Example usage
    fine_tuner = TunisianDialectFineTuner(base_model="distilgpt2")  # Smaller model for testing
    
    # Example data files
    data_files = [
        "c:/Users/moate/Desktop/Tunisian-chat/data/tunisian_sample.csv"
    ]
    
    # Run fine-tuning pipeline with smaller parameters
    results = fine_tuner.run_fine_tuning_pipeline(
        data_files, 
        epochs=1,
        batch_size=2,
        learning_rate=5e-5
    )
    
    print(f"Fine-tuning completed. Model saved at: {results['model_path']}")
```

### 4. Run the Web Application

Start the FastAPI application:

```bash
python -m uvicorn app:app --reload
```

Then open your browser and navigate to http://localhost:8000

## Model Training Details

### Data Requirements

For effective fine-tuning, you'll need:

- Tunisian dialect text data (conversations, social media posts, etc.)
- At least a few hundred samples for minimal testing
- Several thousand samples for better results

### Training Parameters

Adjust these parameters in fine_tuning.py based on your resources:

- **epochs**: Number of training epochs (3-5 recommended)
- **batch_size**: Batch size for training (adjust based on GPU memory)
- **learning_rate**: Learning rate for training (5e-5 is a good starting point)
- **base_model**: Base model to fine-tune (smaller models like "distilgpt2" for testing, larger models like "facebook/opt-350m" for better results)

### Estimated Training Time

Training time depends on:

- Data size
- Model size
- Hardware (GPU vs CPU)

Approximate estimates:

- Small test (distilgpt2, 100 samples, 1 epoch): 5-10 minutes on CPU
- Full training (opt-350m, 5000 samples, 3 epochs): 2-8 hours on GPU

## Customization

### Adding Cultural Context

Edit the cultural_context.py file to add more Tunisian cultural references:

```python
context.add_cultural_entity(
    category="expressions",
    entity="new_expression",
    meaning="Meaning of the expression",
    context="Cultural context of the expression",
    variations=["variation1", "variation2"])
```

### Improving Transliteration

Edit the mapping in transliteration.py to improve Arabic-Latin script conversion.

## Troubleshooting

### Common Issues

**Out of memory errors during training:**
- Reduce batch size
- Use a smaller model
- Reduce sequence length

**Slow training on CPU:**
- Use a GPU if available
- Reduce model size
- Use fewer training samples for testing

**Model not understanding Tunisian dialect:**
- Ensure your training data is high-quality Tunisian dialect
- Increase the amount of training data
- Train for more epochs

## Contributing

Contributions to improve the Tunisian Dialect Chat project are welcome! Please feel free to submit pull requests or open issues to suggest improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.