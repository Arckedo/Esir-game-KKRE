from core.engine import Command

class MoveTopCommand(Command):
    def execute(self, receiver):
        receiver.movetop()

class MoveDownCommand(Command):
    def execute(self, receiver):
        receiver.movedown()

class MoveLeftCommand(Command):
    def execute(self, receiver):
        receiver.moveleft()

class MoveRightCommand(Command):
    def execute(self, receiver):
        receiver.moveright()

class ShootCommand:
    def execute(self, receiver):
        receiver.shoot()