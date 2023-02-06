from bet_game import Game

regular_quests = [
    '7', 1.0,       # weights of random
    '8', 2.0,
    '9', 3.0,
    '9+', 3.0,
    '10', 2.0,
    '10+', 1.0,
    '11', 0.0,
    '12', 0.0,
    'ban', 'dropdead',
    'ban', 'fallensquare',
    'ban', 'altale',
    'ban', 'ifi',
]

turns = 5
game = Game('arcaea', turns=turns)
game.enable('core')
game.enable('rei')
game.enable('yugamu')
game.enable('prelude')
game.enable('vs')
game.enable('ftr')

'''
game.enable_all(en_package=True, en_difficulties=False)
game.disable('extend')
game.enable('ftr')
'''

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
