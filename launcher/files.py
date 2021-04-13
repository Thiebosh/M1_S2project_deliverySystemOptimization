def load_file(path):
    with open(path) as file:
        content = file.read()
    return content


def save_csv(path, data):
    with open(path, "w", encoding='utf-8-sig') as file:
        for line in data:
            file.write(";".join(line)+"\n")
