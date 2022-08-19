import re


def multiple_replace(dic: {}, text: str):
    replaced = text
    for word, value in dic.items():
        replaced = re.sub(word, value, replaced)
    return replaced
