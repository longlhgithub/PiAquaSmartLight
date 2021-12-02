class Command:
    COMMANDS = {'power': 1, 'dimmer': 1, 'color': 3,
                'timer': 0, 'ping': 0, 'brightness': 1}

    def __init__(self, command_str: str) -> None:
        self.command = command_str
        self.command_fragment = self.command.split(' ')

    def is_valid(self) -> bool:
        cmd = Command.COMMANDS.get(self.command_fragment[0], False)
        # print(cmd)
        if type(cmd) == bool and not cmd:
            return False
        return True

    def get_command(self):
        return self.command_fragment[0]

    def get_arguments(self):
        return self.command_fragment[1:]


# test

if __name__ == '__main__':
    cmd = Command('power')
    print(cmd.is_valid())
