from .player import PlayerManager
from .utils import GameplayError, Logger
import random

class RandomEvent:
    def __init__(
        self,
        pm:PlayerManager,
        logger:Logger,
        game_type='arcaea'
    ):
        self.__player_manager = pm
        self.__logger = logger
        self.event = [
            # 若无特殊说明，event效果只在一个turn内生效
            self.absolute_zero,
            # 绝对零分：玩家分数若为负数，则立刻置零
            self.bonus_time,
            # 福利时间：下注成功的玩家可以获得双倍奖励
            self.risk_aversion,
            # 风险规避：下注失败的玩家不会扣除积分
            self.winner_takes_all,
            # 赢家通吃：游玩阶段仅第一名玩家可以获得ceil(n/2)积分，其余为0积分
            self.normal_distribution,
            # 正态分布：游玩阶段最靠中间的玩家获得floor(n/2积分)，此后每向外一名获得积分少1
            self.poverty_relief,
            # 精准扶贫：所有分数最低的玩家立刻获得n积分
            self.no_need_to_hesitate,
            # 不必犹豫：成为下注目标的玩家不会被扣除积分
            self.traffic_collision,
            # 交通事故：结束阶段，若x个人同时下注到了同一个玩家，则每个玩家扣x-1分
            self.popular_player,
            # 人气选手：结束阶段，被下注次数最多的玩家获得2*x分，x为被下注次数
            self.see_you_next_time,
            # 下次一定：下个回合抽取两个事件
            self.be_patient,
            # 你先别急：结束阶段，所有分数最低的玩家获得n积分
            self.sing_along,
            # 跟着歌唱：游玩时玩家需唱打
            self.nothing_happend
            # 无事发生：真的无事发生
        ]

        self.arc_event = [
            self.the_slower_the_simpler,
            # 越慢越水：游玩时玩家需在2.0以下流速进行游玩
            self.rush_hour
            # 极速时刻：游玩时玩家需使用最高速进行游玩
        ]

        self.phi_event = [
            self.upside_down,
            # 天翻地覆：游玩时玩家需旋转设备180°进行游玩
            self.accurate_hit
        ]

        if game_type == 'arcaea':
            self.event.extend(self.arc_event)
        elif game_type == 'phigros':
            self.event.extend(self.phi_event)
        else:
            raise GameplayError("Currently Only Support arcaea and phigros")
        self.reset()

    def reset(self):
        self.double_event = False

    def draw_event(self):
        if self.double_event:
            self.double_event = False
            event_list = random.sample(self.event, 2)
            for event in event_list:
                event()
        else:
            event = random.choice(self.event)
            event()

    def log(self, s, file=True):
        self.__logger.log(s, file)

    def absolute_zero(self):
        self.log("-----------------------------------------------")
        self.log("Event: \'absolute\' zero")
        self.log("All player scores are immediately taken max(score, 0)")
        for player in self.__player_manager.player_list:
            player.score = max(0, player.score)

    def bonus_time(self):
        self.log("-----------------------------------------------")
        self.log("Event: bonus time")
        self.log("Players who bet successfully can get double rewards")
        self.__player_manager.double_reward = True

    def risk_aversion(self):
        self.log("-----------------------------------------------")
        self.log("Event: risk aversion")
        self.log("Players who lose bets will not be deducted points")
        self.__player_manager.bet_failed_deduct = False

    def winner_takes_all(self):
        self.log("-----------------------------------------------")
        self.log("Event: winner takes all")
        self.log("Only the first player in the game stage can get ceil(n/2) points")
        self.log("        and the rest get 0 points")
        def winner_takes_all_rank_to_score(member):
            pt = (len(member)+1)//2
            for i, player in enumerate(member):
                player.rank = i
                player.cur_pt = pt
                player.score += pt
                if pt > 0:
                    pt = 0
        self.__player_manager.rank_to_score = winner_takes_all_rank_to_score

    def normal_distribution(self):
        self.log("-----------------------------------------------")
        self.log("Event: normal distribution")
        self.log("The player who is closest to the middle of the playing stage gets floor(n/2 points)")
        self.log("        after that, every player outside gets 1 less points")
        def normal_distribution_rank_to_score(member):
            n = self.__player_manager.player_num
            if n % 2 == 0:
                max_posi = [n//2, n//2-1]
                for i, player in enumerate(member):
                    pt = n//2 - min(abs(i-max_posi[0]), abs(i-max_posi[1]))
                    player.rank = i
                    player.cur_pt = pt
                    player.score += pt
            else:
                max_posi = n // 2
                for i, player in enumerate(member):
                    pt = n//2 - abs(i-max_posi)
                    player.rank = i
                    player.cur_pt = pt
                    player.score += pt
        self.__player_manager.rank_to_score = normal_distribution_rank_to_score

    def poverty_relief(self):
        self.log("-----------------------------------------------")
        self.log("Event: poverty relief")
        self.log("All players with the lowest score get n points immediately")
        min_score = None
        for player in self.__player_manager.player_list:
            if min_score is None or player.score < min_score:
                min_score = player.score
        for player in self.__player_manager.player_list:
            if player.score == min_score:
                player.score += self.__player_manager.player_num

    def no_need_to_hesitate(self):
        self.log("-----------------------------------------------")
        self.log("Event: no need to hesitate")
        self.log("Players who become the target of betting will not be deducted points")
        self.__player_manager.betted_deduct = False

    def traffic_collision(self):
        self.log("-----------------------------------------------")
        self.log("Event: traffic collsion")
        self.log("At the end of the turn, if x players bet on the same player")
        self.log("        each player will deduct x-1 points")
        def traffic_collision_inner():
            betted_dict = {}
            most_betted = None
            for player in self.__player_manager.player_list:
                if not player.bet_id is None:
                    if not player.bet_id in betted_dict.keys():
                        betted_dict[player.bet_id] = 0
                    betted_dict[player.bet_id] += 1
                    if most_betted is None or betted_dict[player.bet_id] > most_betted:
                        most_betted = betted_dict[player.bet_id]

            for player in self.__player_manager.player_list:
                if not player.bet_id is None:
                    if betted_dict[player.bet_id] == most_betted:
                        player.score -= (betted_dict[player.bet_id] - 1)
            
        self.__player_manager.after_event.append(traffic_collision_inner)
    
    def popular_player(self):
        self.log("-----------------------------------------------")
        self.log("Event: popular player")
        self.log("At the end of the turn, the player with the most bets targets gets 2*x points")
        self.log("        where x is the number of bets targets")
        def popular_player_inner():
            most_betted = -1
            for player in self.__player_manager.player_list:
                if not player.betted is None and player.betted > most_betted:
                    most_betted = player.betted
                    
            if not most_betted is None:
                for player in self.__player_manager.player_list:
                    if player.betted == most_betted:
                        player.score += 2 * most_betted
        self.__player_manager.after_event.append(popular_player_inner)

    def see_you_next_time(self):
        self.log("-----------------------------------------------")
        self.log("Event: see you next time")
        self.log("Draw two events for the next round")
        self.double_event = True

    def be_patient(self):
        self.log("-----------------------------------------------")
        self.log("Event: be patient")
        self.log("All players with the lowest score get n points at end of the turn")
        def be_patient_inner():
            lowest_score = None
            for player in self.__player_manager.player_list:
                if lowest_score is None or player.score < lowest_score:
                    lowest_score = player.score
            for player in self.__player_manager.player_list:
                if player.score == lowest_score:
                    player.score += self.__player_manager.player_num
        self.__player_manager.after_event.append(be_patient_inner)

    def sing_along(self):
        self.log("-----------------------------------------------")
        self.log("Event: sing along")
        self.log("Player should sing to the song while playing the game")

    def nothing_happend(self):
        self.log("-----------------------------------------------")
        self.log("Event: nothing happened")
        self.log("Literally nothing happened")

    def the_slower_the_simpler(self):
        self.log("-----------------------------------------------")
        self.log("Event: the slower, the simpler")
        self.log("Players should play game in speed restriction less than 2")

    def rush_hour(self):
        self.log("-----------------------------------------------")
        self.log("Event: rush hour")
        self.log("Players should play game in max speed")

    def upside_down(self):
        self.log("-----------------------------------------------")
        self.log("Event: upside down")
        self.log("Player should play game while the device is upside down")

    def accurate_hit(self):
        self.log("-----------------------------------------------")
        self.log("Event: accurate hit")
        self.log("Player should upload the accuracy instead of the score")