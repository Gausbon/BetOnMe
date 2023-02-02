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

game = Game('phigros', turns=2, random_p=0, random_card=True)
game.enable_all()
game.disable('ez')
game.disable('hd')
game.add_quest(regular_quests)
game.enroll('p1111')
game.enroll('p2222')
game.enroll('p3333')
game.enroll('p4444')

game.start()

# turn 1
game.draw_event()
game.draw_quest()

game.bet('p1', 'p2', 2)
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
print(game, '\n')

# redraw
game.draw_quest()
print(game, '\n')

game.bet('p1', None)
# rebet
game.bet('p1', 'p2', 1)
game.bet('p2', 'p1', 3)
game.bet('p3', 'p1', 3)
game.bet('p4', 'p1', 3)

game.play('p1', 0)
# replay
game.play('p1', 9950000)
game.play('p2', 9950000)
game.play('p3', 9850000)
game.play('p4', 9800000)

game.evaluate_score()

print(game, '\n')

game.evaluate_bet()

print(game, '\n')

# game finished
if game.finished:
    print(f'Game is finished. Congratulations to the winner: {game.winner}!')
else:
    print(f'Game is not finished. remaining turn: {game.turns}!')

game.reset_round(1)
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
    print(f'Game is not finished. remaining turn: {game.turns}!')