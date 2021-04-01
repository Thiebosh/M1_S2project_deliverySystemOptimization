from subprocess import check_call
from sys import executable
import pathlib

if __name__ == "__main__":
    filepath = f"{pathlib.Path(__file__).parent.absolute()}\\requirements.txt"
    check_call([executable, "-m", "pip", "install", "-q", "-r", filepath])
