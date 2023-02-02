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

game = Game('arcaea', turns=2, random_p=0, random_card=True)
game.enable('core')
game.enable('rei')
game.enable('yugamu')
game.enable('prelude')
game.enable('vs')
game.enable('ftr')

game.add_quest(regular_quests)

game.enroll('p1111')
game.enroll('p2222')
game.enroll('p3333')
game.enroll('p4444')

game.start()

# turn 1
game.draw_event()
game.draw_quest()

game.bet('p1', 'p2', 1)
game.bet('p2', 'p3', 1)
game.bet('p3', 'p1', 1)
game.bet('p4', 'p1', 1)
game.bet('p4', None)

game.play('p1', 9950000)
game.play('p2', 9900000)
game.play('p3', 9850000)
game.play('p4', 9500000)
game.play('p4', 9800000)

game.evaluate_score()

game.evaluate_bet()

# turn 2
game.draw_event()
game.draw_quest()

# redraw
game.draw_quest()

game.draw_card('p1')
game.bet('p2', 'p1', 3)
game.bet('p3', None)
game.bet('p4', 'p1', 3)

game.show_card()

game.play('p1', 0)
# replay
game.play('p1', 9950000)
game.play('p2', 9950000)
game.play('p3', 9850000)
game.play('p4', 9800000)

game.evaluate_score()

game.evaluate_bet()

# game finished
if game.finished:
    print(f'Game is finished. Congratulations to the winner: {game.winner}!')
else:
    print(f'Game is not finished. remaining turn: {game.turns}!')

""" game.reset_round(1)
game.enroll('p5555')
game.enroll('p6666')
game.remove('p3333')
game.start()

# another turn 1
game.draw_event()
game.draw_quest()
print(game, '\n')

# redraw
game.draw_quest()

game.bet('p1', None)
# rebet
game.bet('p1', 'p2', 3)
game.bet('p2', 'p1', 1)
game.bet('p5', 'p1', 1)
game.bet('p4', 'p1', 1)
game.bet('p6', None)

game.play('p1', 0)
# replay
game.play('p1', 9750000)
game.play('p2', 9900000)
game.play('p5', 9950000)
game.play('p4', 9800000)
game.play('p6', 0)

game.evaluate_score()

print(game, '\n')

game.evaluate_bet()

print(game, '\n')

# game finished
if game.finished:
    print(f'Game is finished. Congratulations to the winner: {game.winner}!')
else:
    print(f'Game is not finished. remaining turn: {game.turns}!') """