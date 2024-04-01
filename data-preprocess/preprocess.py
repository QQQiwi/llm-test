import pandas as pd

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

stats_df_path = "archive/laptop_data.csv"
dataset1_path = "datasets/stats_df.csv"
dataset2_path = "datasets/i-lite.csv"
dataset3_path = "datasets/istudio-shop.csv"
prompt_dataset_path = "prompts.csv"


# Препроцессинг датасета с Kaggle, который содержит только статистику о
# некоторых ультрабуках
def stats_df_preprocessing():
    stats_df = pd.read_csv(stats_df_path)
    stats_df = stats_df[stats_df["Company"] == "Apple"]

    def stats_to_string(df):
        return f"""{df["Company"]} {df["TypeName"]} {df["Inches"]}""", f"""Ноутбук {df["Company"]} {df["TypeName"]} обладает экраном {df["ScreenResolution"]}, процессором {df["Cpu"]}. Объём его оперативной памяти {df["Ram"]}, его жесткий диск - {df["Memory"]}. Также у него есть графический процессор {df["Gpu"]}. Он весит {df["Weight"]}.""", df["Price"]

    model_list, info_list, price_list = [], [], []
    for idx, row in stats_df.iterrows():
        model, info, price = stats_to_string(row)
        model_list.append(model)
        info_list.append(info)
        price_list.append(price)

    stats_df["Model"] = model_list
    stats_df["Info"] = info_list
    stats_df["Price"] = price_list

    stats_df.to_csv(dataset1_path, index=False)


def generate_prompt(question, data_point):
    return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.
### Instruction:
Answer question of client about advantages and disadvantages of macbook. Tell him about his goods and recommend him to buy it.
### Input:
{question} {data_point["Model"]}
### Response:
{data_point["Info"]}
Он стоит {data_point["Price"]} рублей."""


def create_prompt_dataset():
    df1 = pd.read_csv(dataset1_path)
    df2 = pd.read_csv(dataset2_path)
    df3 = pd.read_csv(dataset3_path)
    dfs = [df1, df2, df3]

    prompts = []
    for cur_df in dfs:
        for _, row in cur_df.iterrows():
            for q in INPUT_QUESTION:
                prompts.append(generate_prompt(q, row))
    
    df = {"prompt": prompts}
    df = pd.DataFrame(df)
    df.to_csv(prompt_dataset_path)


def main():
    stats_df_preprocessing()
    create_prompt_dataset()

if __name__ == "__main__":
    main()

