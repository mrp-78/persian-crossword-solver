import re


def multiple_replace(dic: {}, text: str):
    replaced = text
    for word, value in dic.items():
        replaced = re.sub(word, value, replaced)
    return replaced


def merge_answers(dict1: {}, dict2):
    for key in dict2:
        if key in dict1:
            dict1[key] = max(dict1[key], dict2[key])
        else:
            dict1[key] = dict2[key]
    return dict1
