import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Tunisian Dialect Chatbot")
    parser.add_argument("--mode", choices=["chat", "train", "evaluate", "collect-data"], 
                        default="chat", help="Operation mode")
    parser.add_argument("--model-path", type=str, default=None, 
                        help="Path to the fine-tuned model")
    parser.add_argument("--data-dir", type=str, default="data", 
                        help="Directory for data files")
    parser.add_argument("--epochs", type=int, default=3, 
                        help="Number of training epochs")
    
    args = parser.parse_args()
    
    if args.mode == "chat":
        from chatbot import TunisianChatbot
        chatbot = TunisianChatbot(model_path=args.model_path)
        chatbot.chat()
    
    elif args.mode == "train":
        from fine_tuning import TunisianModelTrainer
        
        # Create data directory if it doesn't exist
        if not os.path.exists(args.data_dir):
            os.makedirs(args.data_dir)
            print(f"Created data directory: {args.data_dir}")
            print("Please add training data to this directory before training.")
            return
        
        trainer = TunisianModelTrainer(output_dir="model")
        train_file, val_file = trainer.prepare_dataset(data_dir=args.data_dir)
        trainer.fine_tune(train_file, val_file, epochs=args.epochs)
    
    elif args.mode == "evaluate":
        from evaluation import TunisianChatbotEvaluator
        from chatbot import TunisianChatbot
        
        chatbot = TunisianChatbot(model_path=args.model_path)
        evaluator = TunisianChatbotEvaluator(chatbot)
        evaluator.run_evaluation()
    
    elif args.mode == "collect-data":
        from data_collection import TunisianDataCollector
        
        collector = TunisianDataCollector(output_dir=args.data_dir)
        print("Data Collection Mode")
        print("-" * 50)
        print("Please configure your API keys in the script or provide them as environment variables.")
        print("Available collection methods:")
        print("1. Twitter data collection")
        print("2. Import existing corpus")
        
        choice = input("Select a method (1-2): ")
        
        if choice == "1":
            api_key = input("Enter Twitter API Key: ")
            api_secret = input("Enter Twitter API Secret: ")
            access_token = input("Enter Twitter Access Token: ")
            access_token_secret = input("Enter Twitter Access Token Secret: ")
            
            collector.collect_twitter_data(
                api_key=api_key,
                api_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret
            )
        elif choice == "2":
            corpus_path = input("Enter path to corpus file: ")
            corpus_type = input("Enter corpus type (TSAC, MADAR, etc.): ")
            
            collector.import_existing_corpus(corpus_path, corpus_type)
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()