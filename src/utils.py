import re


def multiple_replace(dic: {}, text: str):
    replaced = text
    for word, value in dic.items():
        replaced = re.sub(word, value, replaced)
    return replaced


def merge_answers(dict1: {}, dict2):
    for key in dict2:
        if key in dict1:
            p = max(dict1[key], dict2[key])
            if p < 0.5:
                p *= 1.2
            else:
                p *= 1.1
            if p > 0.9:
                p = 0.9
            dict1[key] = p
        else:
            dict1[key] = dict2[key]
    return dict1
