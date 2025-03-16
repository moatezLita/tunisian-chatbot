import os
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from tqdm import tqdm
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling
)
from datasets import Dataset

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fine_tuning.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TunisianDialectFineTuner:
    def __init__(self, base_model="facebook/opt-350m", output_dir="models"):
        """
        Initialize the fine-tuner
        
        Args:
            base_model: Base model to fine-tune
            output_dir: Directory to save fine-tuned models
        """
        self.base_model = base_model
        self.output_dir = output_dir
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    def prepare_data(self, data_files, validation_split=0.1):
        """
        Prepare data for fine-tuning
        
        Args:
            data_files: List of data files (CSV or JSON)
            validation_split: Fraction of data to use for validation
            
        Returns:
            Dictionary with train and validation datasets
        """
        logger.info(f"Preparing data from {len(data_files)} files")
        
        all_texts = []
        
        for file_path in data_files:
            try:
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                    
                    # Assume the text column is named 'text'
                    if 'text' in df.columns:
                        texts = df['text'].tolist()
                        all_texts.extend([t for t in texts if isinstance(t, str) and len(t) > 10])
                        
                elif file_path.endswith('.json'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and 'text' in item:
                                all_texts.append(item['text'])
                    elif isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
                        for item in data['data']:
                            if isinstance(item, dict) and 'text' in item:
                                all_texts.append(item['text'])
                                
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {str(e)}")
                
        logger.info(f"Collected {len(all_texts)} text samples")
        
        # Shuffle the data
        np.random.shuffle(all_texts)
        
        # Split into train and validation
        split_idx = int(len(all_texts) * (1 - validation_split))
        train_texts = all_texts[:split_idx]
        val_texts = all_texts[split_idx:]
        
        logger.info(f"Train set: {len(train_texts)} samples")
        logger.info(f"Validation set: {len(val_texts)} samples")
        
        # Create datasets
        train_dataset = Dataset.from_dict({"text": train_texts})
        val_dataset = Dataset.from_dict({"text": val_texts})
        
        return {
            "train": train_dataset,
            "validation": val_dataset
        }
    
    def tokenize_data(self, datasets):
        """
        Tokenize the datasets
        
        Args:
            datasets: Dictionary with train and validation datasets
            
        Returns:
            Dictionary with tokenized datasets
        """
        logger.info("Loading tokenizer")
        tokenizer = AutoTokenizer.from_pretrained(self.base_model)
        
        # Add padding token if it doesn't exist
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        def tokenize_function(examples):
            return tokenizer(
                examples["text"],
                padding="max_length",
                truncation=True,
                max_length=512,
                return_special_tokens_mask=True
            )
            
        logger.info("Tokenizing datasets")
        tokenized_datasets = {}
        
        for split, dataset in datasets.items():
            tokenized_datasets[split] = dataset.map(
                tokenize_function,
                batched=True,
                remove_columns=["text"]
            )
            
        return tokenized_datasets, tokenizer
    
    def fine_tune(self, tokenized_datasets, tokenizer, epochs=3, batch_size=8, learning_rate=5e-5):
        """
        Fine-tune the model
        
        Args:
            tokenized_datasets: Dictionary with tokenized datasets
            tokenizer: Tokenizer for the model
            epochs: Number of training epochs
            batch_size: Batch size for training
            learning_rate: Learning rate for training
            
        Returns:
            Fine-tuned model
        """
        logger.info(f"Loading base model: {self.base_model}")
        model = AutoModelForCausalLM.from_pretrained(self.base_model)
        
        # Set up training arguments
        model_name = self.base_model.split("/")[-1]
        training_args = TrainingArguments(
            output_dir=f"{self.output_dir}/{model_name}-tunisian-{datetime.now().strftime('%Y%m%d-%H%M')}",
            overwrite_output_dir=True,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            eval_steps=500,
            save_steps=1000,
            warmup_steps=500,
            learning_rate=learning_rate,
            weight_decay=0.01,
            logging_dir="./logs",
            logging_steps=100,
            evaluation_strategy="steps",
            save_total_limit=3,
            load_best_model_at_end=True,
            report_to="tensorboard"
        )
        
        # Set up data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False  # We're doing causal language modeling, not masked
        )
        
        # Set up trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            data_collator=data_collator,
            train_dataset=tokenized_datasets["train"],
            eval_dataset=tokenized_datasets["validation"]
        )
        
        # Train the model
        logger.info("Starting fine-tuning")
        trainer.train()
        
        # Save the model
        logger.info("Saving fine-tuned model")
        trainer.save_model()
        tokenizer.save_pretrained(training_args.output_dir)
        
        return model, tokenizer, training_args.output_dir
    
    def run_fine_tuning_pipeline(self, data_files, epochs=3, batch_size=8, learning_rate=5e-5):
        """
        Run the complete fine-tuning pipeline
        
        Args:
            data_files: List of data files
            epochs: Number of training epochs
            batch_size: Batch size for training
            learning_rate: Learning rate for training
            
        Returns:
            Dictionary with fine-tuning results
        """
        # Prepare data
        datasets = self.prepare_data(data_files)
        
        # Tokenize data
        tokenized_datasets, tokenizer = self.tokenize_data(datasets)
        
        # Fine-tune model
        model, tokenizer, model_path = self.fine_tune(
            tokenized_datasets, 
            tokenizer, 
            epochs=epochs, 
            batch_size=batch_size, 
            learning_rate=learning_rate
        )
        
        return {
            "model": model,
            "tokenizer": tokenizer,
            "model_path": model_path
        }
    
    def evaluate_model(self, model_path, test_data_file):
        """
        Evaluate a fine-tuned model on test data
        
        Args:
            model_path: Path to the fine-tuned model
            test_data_file: Path to the test data file
            
        Returns:
            Dictionary with evaluation metrics
        """
        logger.info(f"Evaluating model: {model_path}")
        
        # Load model and tokenizer
        model = AutoModelForCausalLM.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # Load test data
        if test_data_file.endswith('.csv'):
            df = pd.read_csv(test_data_file)
            test_texts = df['text'].tolist() if 'text' in df.columns else []
        elif test_data_file.endswith('.json'):
            with open(test_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if isinstance(data, list):
                test_texts = [item['text'] for item in data if isinstance(item, dict) and 'text' in item]
            elif isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
                test_texts = [item['text'] for item in data['data'] if isinstance(item, dict) and 'text' in item]
            else:
                test_texts = []
                
        # Tokenize test data
        test_dataset = Dataset.from_dict({"text": test_texts})
        
        def tokenize_function(examples):
            return tokenizer(
                examples["text"],
                padding="max_length",
                truncation=True,
                max_length=512,
                return_special_tokens_mask=True
            )
            
        tokenized_test = test_dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=["text"]
        )
        
        # Set up data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False
        )
        
        # Set up trainer
        trainer = Trainer(
            model=model,
            data_collator=data_collator,
            eval_dataset=tokenized_test
        )
        
        # Evaluate
        eval_results = trainer.evaluate()
        
        logger.info(f"Evaluation results: {eval_results}")
        
        return eval_results

if __name__ == "__main__":
    # Example usage
    fine_tuner = TunisianDialectFineTuner()
    
    # Example data files
    data_files = [
        "data/tunisian_corpus.csv",
        "data/tunisian_social_media.csv"
    ]
    
    # Run fine-tuning pipeline
    # results = fine_tuner.run_fine_tuning_pipeline(data_files, epochs=3, batch_size=4)
    
    # Evaluate model
    # eval_results = fine_tuner.evaluate_model(results["model_path"], "data/tunisian_test.csv")
    
    print("Fine-tuning module initialized. Use run_fine_tuning_pipeline() to start training.")