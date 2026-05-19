

class Operator:

    def __init__(self, name: str):
        self.name = name
        self.score = 0.0
        self.weight = 1.0

    def apply(self, solution, problem, config):
        pass
    
    def add_reward(self, reward: float):
        self.score += reward

    def update_weight(self):
        self.weight = max(0.1, self.score)
        self.score = 0.0
