from init_arc import *

reset(2)
add('p1111')
add('p2222')
add('p3333')
add('p4444')

start()

# turn 1
event()
quest()
verify()

bet('p1', 'p3', 2)
bet('p2', 'p3', 1)
bet('p3', 'p1', 1)
bet('p4', 'p1', 1)
bet('p4', None)

play('p1', 9950000)
play('p2', 9900000)
play('p3', 9850000)
play('p4', 9500000)
play('p4', 9800000)

result()

# turn 2
event()
quest()
quest()
verify()

bet('p1', None)
bet('p1', 'p3', 1)
bet('p2', 'p3', 3)
bet('p3', 'p1', 3)
bet('p4', 'p1', 3)

play('p1', 0)
play('p1', 9950000)
play('p2', 9950000)
play('p3', 9850000)
play('p4', 9800000)

result()

# another round
reset(1)
add('p5555')
add('p6666')
remove('p3333')
start()

# another turn 1
event()
quest()
quest()
verify()

bet('p1', None)
bet('p1', 'p2', 3)
bet('p2', 'p1', 1)
bet('p5', 'p1', 1)
bet('p4', 'p1', 1)
bet('p6', None)

play('p1', 0)
play('p1', 9750000)
play('p2', 9900000)
play('p5', 9950000)
play('p4', 9800000)
play('p6', 0)

result()
