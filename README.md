# 程序思路

* 在每回合开始的时候用RandomCard.default_card()生成一个默认卡，大部分情况下程序执行的都是game.__current_card通过各个环节的钩子传进去的默认函数
* 将所有试图买卡的player添加进pending_list中，所有人结束下注之后用game.show_card输出获得者，判断是否使用并用新卡替换game.__current_card，将pending_list写进卡里并将列表传给playmanager.card_deduct执行扣分。
* 卡的所有效果全部通过用钩子传入函数实现，大部分函数功能是从旧的player_list生成新的player_list并返回，有些函数结尾需要把新list排个序再输出

# 主要的其他更改

* 整理了player的属性和注释
* 把所有的命令行文本输出全部改成了走.utils.log()
* 重写了game和player的__str__()