import argparse
import os
import pathlib
import multiprocessing
import subprocess

def run(data, id):
    try:
        return subprocess.check_output([".\\test", str(data)])
        
    except KeyboardInterrupt:
        return None

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("file_name", type=str,  help="You must enter the name of the file you want to use")
    arg_parser.add_argument("process_number", type=int,  help="You must enter the number of thread you want to start")
    args = arg_parser.parse_args()

    print(str(pathlib.Path(__file__).parent.absolute()))
    file_path = str(pathlib.Path(__file__).parent.absolute())+"\\"+args.file_name
    if not os.path.exists(file_path):
        print("This file doesn't exist")
        exit()

    file = open(file_path,"r")
    data = {"distances":[]}
    for line in file.readlines():
        line = line[:-1]
        cur_line_data = [float(x) for x in line.split("  ")]
        data["distances"].append(cur_line_data)

    
    
    with multiprocessing.Pool(processes=args.process_number) as p:
            argsList = []
            for i in range(args.process_number):
                argsList.append((data,i))
            try:
                p.starmap(run, argsList)
            except KeyboardInterrupt:
                print("ctrl+C")
                p.terminate()

    
    # sorting part
    tasks = [(12, "4,5,8"), (2, "8,5,4"), (8, "5,8,4")]

    for task in sorted(tasks, key=lambda x: x[0]):
        print(f"{task[1]} took {task[0]}")
