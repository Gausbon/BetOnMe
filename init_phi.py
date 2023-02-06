from bet_game import Game

regular_quests = [
    '7', 0.0,
    '14', 1.5,
    '15', 1.5,
    '16', 1.0,
    'ban', 'もぺもぺ',
    'ban', 'Break Over',
    'ban', 'Sigma (Haocore Mix) ~ Regrets of The Yellow Tulip ~',
    'ban', 'Sigma (Haocore Mix) ~ 105秒の伝説 ~',
    'ban', 'Spasmodic(Haocore Mix)',
    'ban', 'Introduction',
]

turns = 5
game = Game('phigros', turns=turns)
game.enable_all()
game.disable('hd')
game.disable('ez')

game.add_quest(regular_quests)

def reset(turn:int):
    game.reset_round(turn)

def add(id:str):
    game.enroll(id)

def remove(id:str):
    game.remove(id)

def start():
    game.start()

def event():
    game.draw_event()

def quest():
    game.draw_quest()

def verify():
    game.verify()

def bet(id1, id2, stake=1):
    game.bet(id1, id2, stake)

def play(id, score):
    game.play(id, score)

def result():
    game.evaluate_preprocess()
    game.evaluate_score()
    game.evaluate_bet()
    game.end_turn()

