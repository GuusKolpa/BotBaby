import melee


class ESAgent():
    """
    Expert system agent for SmashBot.
    This is the "manually programmed" TAS-looking agent.
    """
    def __init__(self, dolphin, smashbot_port, opponent_port, controller, difficulty=4):
        self.smashbot_port = smashbot_port
        self.opponent_port = opponent_port
        self.controller = controller
        self.framedata = melee.framedata.FrameData()
        self.logger = dolphin.logger
        self.difficulty = difficulty
        self.ledge_grab_count = 0
        self.tech_lockout = 0
        self.meteor_jump_lockout = 0
        self.meteor_ff_lockout = 0
        self.powershielded_last = False

    def act(self, gamestate):
        if self.smashbot_port not in gamestate.players:
            self.controller.release_all()
            return

