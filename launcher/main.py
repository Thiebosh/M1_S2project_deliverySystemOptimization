
if __name__ == "__main__":
    tasks = [(12, "4,5,8"), (2, "8,5,4"), (8, "5,8,4")]

    for task in sorted(tasks, key=lambda x: x[0]):
        print(f"{task[1]} took {task[0]}")
