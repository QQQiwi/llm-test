import pandas as pd

# Questions needed to formulate a prompt for LLM
INPUT_QUESTION = [
    "Расскажи мне про",
    "Напиши мне характеристики макбука",
    "Какие параметры у ноутбука",
    "Какие преимущества есть у",
    "Чем может похвастаться ноутбук",
    "Чем хорош макбук",
    "Чем от других ноутбуков отличается",
    "Расскажи мне про хороший ноутбук",
    "Какой ноутбук сейчас может быть очень хорошим?",
    "Что умеет",
    "Почему стоит купить",
    "Какой ноутбук мне порекомендуешь?",
    "Посоветуй мне мощный макбук."
]


# TODO:
# Hard-coded paths to datasets (i guess it should be fixed isn't it?)
STATS_DF_PATH = "datasets/laptop_data.csv"
DATASET1_PATH = "datasets/stats_df.csv"
DATASET2_PATH = "datasets/i-lite.csv"
DATASET3_PATH = "datasets/istudio-shop.csv"
PROMPT_DATASET_PATH = "prompts.csv"


def stats_to_string(df_row):
    """
        A function that converts a dataframe sample into a string with
        information about the MacBook and into a string with the cost of the
        MacBook

        Args:
            df_row (pd.Series): sample of dataframe containing information about
                                one MacBook
        
        Returns:
            (str): string with stats about current MacBook (str): string with
            price of current MacBook    

    """
    return f"""{df_row["Company"]} {df_row["TypeName"]} {df_row["Inches"]}""", f"""Ноутбук {df_row["Company"]} {df_row["TypeName"]} обладает экраном {df_row["ScreenResolution"]}, процессором {df_row["Cpu"]}. Объём его оперативной памяти {df_row["Ram"]}, его жесткий диск - {df_row["Memory"]}. Также у него есть графический процессор {df_row["Gpu"]}. Он весит {df_row["Weight"]}.""", df_row["Price"]


def stats_df_preprocessing():
    """
        A function that preprocesses a dataset found on Kaggle, which contains
        some information about apple ultrabooks. This dataset then saving to csv
        format for next preprocessing step.
    """

    stats_df = pd.read_csv(STATS_DF_PATH)
    stats_df = stats_df[stats_df["Company"] == "Apple"]

    model_list, info_list, price_list = [], [], []
    for _, row in stats_df.iterrows():
        model, info, price = stats_to_string(row)
        model_list.append(model)
        info_list.append(info)
        price_list.append(price)

    stats_df["Model"] = model_list
    stats_df["Info"] = info_list
    stats_df["Price"] = price_list

    stats_df.to_csv(DATASET1_PATH, index=False)


def generate_prompt(question, data_point):
    """
        Args:
            question (str): an input question needed to formulate a prompt for
                            LLM
            data_point (pd.Series): sample of dataframe containing information
                                    about one MacBook
    
        Returns:
            (str) a prompt in a convenient format for training a large language
            model.
    """
    return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.
### Instruction:
Answer question of client about advantages and disadvantages of macbook. Tell him about his goods and recommend him to buy it.
### Input:
{question} {data_point["Model"]}
### Response:
{data_point["Info"]}
Он стоит {data_point["Price"]} рублей."""


def create_prompt_dataset():
    """
        A function that creates a dataset for fine-tuning an LLM model. This
        dataset then saving to csv format for LLM fine-tuning.
    """
    df1 = pd.read_csv(DATASET1_PATH)
    df2 = pd.read_csv(DATASET2_PATH)
    df3 = pd.read_csv(DATASET3_PATH)
    dfs = [df1, df2, df3]

    prompts = []
    # TODO:
    # this cycles can be changed to pandas functions (apply etc.)
    for cur_df in dfs:
        for _, row in cur_df.iterrows():
            for q in INPUT_QUESTION:
                prompts.append(generate_prompt(q, row))
    
    df = {"prompt": prompts}
    df = pd.DataFrame(df)
    df.to_csv(PROMPT_DATASET_PATH)


def main():
    """
        This script firstly preprocesses Kaggle dataset which contains info
        about some ultrabooks, then preprocess this data and parsed data to
        create a dataset for LLM finetuning.
    """
    stats_df_preprocessing()
    create_prompt_dataset()

if __name__ == "__main__":
    main()

