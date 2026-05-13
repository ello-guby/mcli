from src.cli import Cmd

class mCmd(Cmd):
    def cmd_print(self, msg: str) -> None:
        print(msg)

