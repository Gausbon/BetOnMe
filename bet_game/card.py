from .player import Player
from .utils import GameplayError, log
import random
from math import floor, ceil
from functools import cmp_to_key

# cmp funcs
def score_cmp(a:Player, b:Player):
    if a.score != b.score:
        return a.score - b.score
    else:
        return a.id > b.id

def playing_score_cmp(a:Player, b:Player):
    if not a.rank is None and not b.rank is None and a.rank != b.rank:
        return b.rank - a.rank
    elif a.playing_score != b.playing_score:
        return a.playing_score - b.playing_score
    else:
        return a.id > b.id


def search_player(id, player_list):
    for player in player_list:
        if player.id == id:
            return player

class CardInstance:
    def __init__(
        self,
        description='',
        user='',
        playing_score_preprocess=0,
        score_rank_cmp=0,
        target_rearrange=0,
        bet_deduct=0,
        bet_score_preprocess=0,
        bet_score_evaluate=0,
        bet_score_postprocess=0,
        valid=1
        ):
        self.description = description
        self.user = user
        self.user_deduct_list = []
        self.playing_score_preprocess = playing_score_preprocess if playing_score_preprocess else self.default_playing_score_preprocess
        self.score_rank_cmp = score_rank_cmp if score_rank_cmp else self.default_score_ranking_cmp
        self.target_rearrange = target_rearrange if target_rearrange else self.default_target_rearrange
        self.bet_deduct = bet_deduct if bet_deduct else self.default_bet_deduct
        self.bet_score_preprocess = bet_score_preprocess if bet_score_preprocess else self.default_bet_score_preprocess
        self.bet_score_evaluate = bet_score_evaluate if bet_score_evaluate else self.default_bet_score_evaluate
        self.bet_score_postprocess = bet_score_postprocess if bet_score_postprocess else self.default_bet_score_postprocess
        self.valid = valid

    def set_deduct_list(self, player_list):
        self.user_deduct_list = player_list

    def default_playing_score_preprocess(self, player_list):
        return player_list
    
    def default_score_ranking_cmp(self, a:Player, b:Player):
        if not a.rank is None and not b.rank is None and a.rank != b.rank:
            return b.rank - a.rank
        elif a.playing_score != b.playing_score:
            return a.playing_score - b.playing_score
        elif a.score != b.score:
            return b.score - a.score
        else:
            return a.id > b.id

    def default_target_rearrange(self, player_list):
        return player_list

    def default_bet_deduct(self, player_list):
        deduct_list = player_list
        for player in deduct_list:
            if player.bet_id:
                bet_player = search_player(player.bet_id, deduct_list)
                bet_player.score -= 1
                if bet_player.betted is None:
                    bet_player.betted = 1
                else:
                    bet_player.betted += 1
        for player in deduct_list:
            if player.betted is None:
                player.betted = 0
        deduct_list = sorted(deduct_list, reverse=True, key=cmp_to_key(score_cmp))
        return deduct_list

    def default_bet_score_preprocess(self, player_list):
        return player_list
    
    def default_bet_score_evaluate(self, player_list):
        evaluate_list = sorted(player_list, reverse=True, key=cmp_to_key(score_cmp))
        max_score = evaluate_list[0].score
        score_list = [0 for _ in range(len(evaluate_list))]

        for i, player in enumerate(evaluate_list):
            if player.bet_id:
                bet_player = search_player(player.bet_id, evaluate_list)
                if bet_player.score == max_score:
                    score_list[i] = player.stake
                else:
                    score_list[i] = -player.stake

        for i, player in enumerate(evaluate_list):
            player.bet_reward = score_list[i]
            player.score += score_list[i]
        evaluate_list = sorted(evaluate_list, reverse=True, key=cmp_to_key(score_cmp))
        return evaluate_list

    def default_bet_score_postprocess(self, player_list):
        postprocess_list = player_list
        for player in postprocess_list:
            if not player.card_reward is None:
                player.card_reward_merged = True
                player.score += player.card_reward
        postprocess_list = sorted(player_list, reverse=True, key=cmp_to_key(score_cmp))
        return postprocess_list

class RandomCard:
    STATUS_000_CARD_UNAVAILABLE = 000
    STATUS_110_CARD_AVAILABLE = 110
    STATUS_111_CARD_CALL = 111
    STATUS_112_CARD_DETERMINED = 112

    def __init__(
        self,
        game_type='arcaea',
        random_card=False
    ):
        self.game_type = game_type
        if random_card:
            self.__status = self.STATUS_110_CARD_AVAILABLE
        else:
            self.__status = self.STATUS_000_CARD_UNAVAILABLE

        self.player_rank_list = []
        self.card_pending_list = []

        # card效果只在一个turn内生效
        self.cards = [
            self.target_shift,
            self.successful_escape,
            self.risk_aversion,
            self.safety_reward,
            self.reverse_rank,
            self.random_score,
            self.force_max_score,
            self.fake_card
        ]

    def reset_turn(self):
        self.__status = self.STATUS_110_CARD_AVAILABLE
        self.__card = self.default_card()
        self.card_pending_list = []

    def reset_game(self):
        self.player_rank_list = []
        self.reset_turn()
    
    def default_card(self) -> CardInstance:
        card = CardInstance(valid=0)
        return card

    def set_player_list(self, player_list):
        self.player_rank_list = sorted(player_list, reverse=True,
         key=cmp_to_key(score_cmp))
        self.card_pending_list = []

    def add_pending_queue(self, player:Player):
        if self.__status == self.STATUS_000_CARD_UNAVAILABLE:
            raise GameplayError('Invalid operation. Random card is not activated in the current game.')
        else:
            self.__status = self.STATUS_111_CARD_CALL
            self.card_pending_list.append(player)
            log(f'Player {player.id} uses {floor(len(self.player_rank_list)/2)} points trying to buy a random card.')
    
    def print_card(self) -> CardInstance:
        if self.__status == self.STATUS_000_CARD_UNAVAILABLE:
            raise GameplayError('Invalid operation. Random card is not activated in the current game.')
        else:
            self.card_pending_list = sorted(self.card_pending_list,
             reverse=True, key=cmp_to_key(score_cmp))
            card_func = random.choice(self.cards)
            self.__card = card_func(user=self.card_pending_list[0])
            self.__card.user_deduct_list = self.card_pending_list
            self.__status = self.STATUS_112_CARD_DETERMINED
            return self.__card
    
    # Card details
    def target_shift(self, user) -> CardInstance:
        _desc = "所有对他人下注的目标按上轮总分位次将目标后移一个人"
        _user = user
        def _target_rearrange(player_list):
            rearrange_list = player_list
            for player in rearrange_list:
                if player.bet_id:
                    for i, _player in enumerate(self.player_rank_list):
                        if _player.id == player.bet_id:
                            player.bet_id = self.player_rank_list[(i+1)%len(self.player_rank_list)].id
                            break
            return rearrange_list

        card = CardInstance(
            description=_desc,
            user=_user,
            target_rearrange=_target_rearrange
        )
        return card

    def successful_escape(self, user) -> CardInstance:
        _desc = "若目标为你的下注都失败了，在赌注结算环节后将这些下注总分将平均分给你和所有这次打歌得零分的人"
        _user = user

        def _bet_score_evaluate(player_list):
            playing_score_evaluate_list = sorted(player_list, reverse=True,
              key=cmp_to_key(playing_score_cmp))
            score_reward_list = []
            for i, player in enumerate(playing_score_evaluate_list):
                if i >= (len(playing_score_evaluate_list)+1)//2:
                    score_reward_list.append(player)
                else:
                    if player.id == _user.id:
                        score_reward_list.append(player)
            score_evaluate_list = sorted(player_list, reverse=True,
             key=cmp_to_key(score_cmp))
            max_score = score_evaluate_list[0].score
            score_list = [0 for _ in range(len(score_evaluate_list))]
            score_pool = 0

            for i, player in enumerate(score_evaluate_list):
                if player.bet_id:
                    bet_player = search_player(player.bet_id, score_evaluate_list)
                    if bet_player.score == max_score:
                        score_list[i] = player.stake
                    else:
                        score_list[i] = -player.stake
                        if bet_player.id == user.id:
                            score_pool += player.stake

            score_reward = score_pool // len(score_reward_list)
            for i, player in enumerate(score_evaluate_list):
                player.bet_reward = score_list[i]
                player.score += score_list[i]
                for _player in score_reward_list:
                    if player.id == _player.id:
                        player.card_reward = score_reward
            return score_evaluate_list
        
        card = CardInstance(
            description=_desc,
            user=_user,
            bet_score_evaluate=_bet_score_evaluate
        )
        return card
    
    def safety_reward(self, user) -> CardInstance:
        _desc = "所有未进行下注的玩家加n/4（向上取整）分"
        _user = user
        
        def _bet_score_preprocess(player_list):
            process_list = player_list
            for player in process_list:
                if not player.bet_id:
                    player.card_reward = ceil(len(player_list)/4)
            return process_list
        
        card = CardInstance(
            description=_desc,
            user=_user,
            bet_score_preprocess=_bet_score_preprocess
        )
        return card
    
    def risk_aversion(self, user) -> CardInstance:
        _desc = "bet失败的玩家不会扣除积分"
        _user = user
        def _bet_score_evaluate(player_list):
            evaluate_list = sorted(player_list, reverse=True)
            max_score = evaluate_list[0].score
            score_list = [0 for _ in range(len(evaluate_list))]

            for i, player in enumerate(evaluate_list):
                if player.bet_id:
                    bet_player = search_player(player.bet_id, evaluate_list)
                    if bet_player.score == max_score:
                        score_list[i] = player.stake

            for i, player in enumerate(evaluate_list):
                player.bet_reward = score_list[i]
                player.score += score_list[i]
            evaluate_list = sorted(evaluate_list, reverse=True, key=cmp_to_key(score_cmp))
            return evaluate_list

        card = CardInstance(
            description=_desc,
            user=_user,
            bet_score_evaluate=_bet_score_evaluate
        )
        return card
    
    def reverse_rank(self, user) -> CardInstance:
        _desc = "本轮打歌得分从低到高计算"
        _user = user
        def _score_ranking_cmp(a:Player, b:Player):
            if not a.rank is None and not b.rank is None and a.rank != b.rank:
                return a.rank - b.rank
            elif a.playing_score != b.playing_score:
                return b.playing_score - a.playing_score
            elif a.score != b.score:
                return a.score - b.score
            else:
                return a.id < b.id

        card = CardInstance(
            description=_desc,
            user=_user,
            score_rank_cmp=_score_ranking_cmp
        )
        return card
    
    def random_score(self, user) -> CardInstance:
        _desc = "所有人亮成绩后，你在[本轮最低成绩，满分]范围内roll一个分数出来作为你的本轮打歌成绩"
        _user = user
        if self.game_type == "arcaea":
            max_score = 10010000 # waiting for arcaea parser support
        elif self.game_type == "phigros":
            max_score = 1000000
        else:
            raise GameplayError("Currently Only Support arcaea and phigros")
        
        def _playing_score_preprocess(player_list):
            min_score = max_score
            preprocess_list = player_list
            for player in preprocess_list:
                if player.playing_score < min_score:
                    min_score = player.playing_score
            rand_score = random.randint(min_score, max_score)
            for player in preprocess_list:
                if player.id == user.id:
                    player.playing_score = rand_score
            return player_list

        card = CardInstance(
            description=_desc,
            user=_user,
            playing_score_preprocess=_playing_score_preprocess
        )
        return card
    
    def force_max_score(self, user) -> CardInstance:
        _desc = "你本轮打歌成绩强制视为理论值"
        _user = user
        if self.game_type == "arcaea":
            max_score = 10010000 # waiting for arcaea parser support
        elif self.game_type == "phigros":
            max_score = 1000000
        else:
            raise GameplayError("Currently Only Support arcaea and phigros")
        
        def _playing_score_preprocess(player_list):
            preprocess_list = player_list
            for player in preprocess_list:
                if player.id == user.id:
                    player.playing_score = max_score
            return player_list

        card = CardInstance(
            description=_desc,
            user=_user,
            playing_score_preprocess=_playing_score_preprocess
        )
        return card

    def fake_card(self, user) -> CardInstance:
        _desc = "你花的分数打水漂了！哈哈哈哈哈哈哈"
        _user = user

        card = CardInstance(
            description=_desc,
            user=_user)
        return card

    # Logs
    def __str__(self):
        head = ''
        if self.__status == self.STATUS_110_CARD_AVAILABLE:
            head = f'Random card generator ready.\n'
        if self.__status == self.STATUS_111_CARD_CALL:
            head = f'Somebody is trying to buy a random card.\n'
        elif self.__status == self.STATUS_112_CARD_DETERMINED:
            head = f'The card {self.__card.description} is bought by {self.__card.user.id}.\n'
        return f'{head}'