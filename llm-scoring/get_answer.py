from main import ChatBot
import pandas as pd
import os

bot = ChatBot()

def generate_response(input):
    """
        Custom function to generate response by llm using Ollama API
    """
    result = bot.rag_chain.invoke(input)
    return result


def main():
    """
        This function send questions to llm through 'generate_response' function
        and save answers with correlated questions to csv
    """
    questions_file = os.getenv("QUESTION_FILE") 
    answers_file = os.getenv("ANSWERS_FILE") 
    df = pd.read_csv(questions_file)
    df["Predictions"] = df["Questions"].apply(generate_response)
    df[["Questions", "Predictions"]].to_csv(answers_file, index=False)


if __name__ == "__main__":
    main()

