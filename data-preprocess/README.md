# Описание

Данные, которые были получены с помощью парсеров, следует предобработать перед
использованием их для fine-tuning'а LLM.

Кроме того, помимо таких данных, были также найдены данные об ультрабуках Apple
на Kaggle (ссылка:
https://www.kaggle.com/datasets/ashwinishet/amazon-laptop-review). Их также
следует привести в удобный формат для обучения LLM.

Данный скрипт занимается предобработкой всех найденных датасетов и объединяет их
в один набор данных, который в дальнейшем будет использоваться для обучения
модели.