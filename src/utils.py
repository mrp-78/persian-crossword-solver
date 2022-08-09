def multiple_replace(dic: {}, text: str):
    replaced = text
    for word, initial in dic.items():
        replaced = replaced.replace(word, initial)
    return replaced
