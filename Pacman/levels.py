class LevelController(object):
    def __init__(self):
        self.level = 0
        self.levelmaps = {0: {"name":"maze1.txt", "row":0, "fruit":"cherry"},
                          1: {"name":"maze1.txt", "row":0, "fruit":"banana"},
                          2: {"name":"maze1.txt", "row":0, "fruit":"apple"}}
        
    def nextLevel(self):
        self.level += 1

    def reset(self):
        self.level = 0

    def getLevel(self):
        # print(self.level)
        return self.levelmaps[self.level % len(self.levelmaps)]
