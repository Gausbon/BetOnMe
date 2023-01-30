from functools import cmp_to_key
from .utils import TrieNode, GameplayError

class Player:
    def __init__(self, id:str):
        self.id = id
        self.score = 0
        self.reset_round()

    def reset_round(self):
        self.score = 0
        self.reset_turn()
        
    def reset_turn(self):
        self.took_bet = False
        self.bet_id = None
        self.bet_score = None
        self.betted = None

        self.played = False
        self.playing_score = None
        self.cur_pt = None
        self.rank = None

    def __lt__(self, other):
        return self.score < other.score

    def __str__(self):
        if not self.betted is None:
            return f'{self.id} ({self.score+self.betted-self.cur_pt}+{self.cur_pt}-{self.betted}={self.score})'
        elif not self.cur_pt is None:
            return f'{self.id} ({self.score-self.cur_pt}+{self.cur_pt}={self.score})'
        else:
            return f'{self.id} ({self.score})'
    
class PlayerManager:
    def __init__(self):
        self.betted_decrease = True
        self.bet_failed_decrease = True
        self.player_list = []
        self.player_id_trie = TrieNode()

        # set evaluate function
        self.reset_round()

    def reset_round(self):
        for player in self.player_list:
            player.reset_round()
        self.reset_turn

    # reset function
    def reset_turn(self):
        for player in self.player_list:
            player.reset_turn()
        self.betted_decrease = True
        self.bet_failed_decrease = True
        self.double_reward = False
        self.collision = False
        self.popular = False
        self.patient = False
        self.set_score = self.default_set_score
        self.ranking_cmp = self.default_ranking_cmp
        self.rank_to_score = self.default_rank_to_score

    @property
    def player_num(self):
        return len(self.player_list)

    # player function
    def find_player(self, id:str):
        return self.player_id_trie.find(id)

    def add_player(self, id:str):
        id = str.strip(id)
        if len(id) >= 15:
            raise GameplayError("Player id should be less than 15 character!")
        player = Player(id)
        self.player_list.append(player)
        self.player_id_trie.insert(id, player)

    def remove_player(self, id:str):
        _, player_id = self.player_id_trie.delete(id) 
        for i, player in enumerate(self.player_list):
            if player.id == player_id:
                del(self.player_list[i])
                return

    # default evaluate function
    def default_set_score(self, player:Player, score):
        if not isinstance(score, int):
            raise GameplayError("Score should be an integer")
        player.playing_score = score

    def default_ranking_cmp(self, a:Player, b:Player):
        if not a.rank is None and not b.rank is None and a.rank != b.rank:
            return b.rank - a.rank
        elif a.playing_score != b.playing_score:
            return a.playing_score - b.playing_score
        elif a.score != b.score:
            return b.score - a.score
        else:
            return a.id > b.id

    def default_rank_to_score(self, member):
        pt = (len(member)+1)//2
        for i, player in enumerate(member):
            player.rank = i
            player.cur_pt = pt
            player.score += pt
            if pt > 0:
                pt -= 1

    # evaluate function
    def evaluate_playing_score(self):
        self.player_list = sorted(self.player_list, reverse=True, 
            key=cmp_to_key(self.ranking_cmp))
        if self.betted_decrease:
            for player in self.player_list:
                if player.bet_id:
                    bet_player = self.find_player(player.bet_id)
                    bet_player.score -= 1
                    if bet_player.betted is None:
                        bet_player.betted = 1
                    else:
                        bet_player.betted += 1
        self.rank_to_score(self.player_list)
        
    def evaluate_bet_score(self):
        self.player_list = sorted(self.player_list, reverse=True)
        max_score = self.player_list[0].score
        score_list = [0 for _ in range(self.player_num)]

        for i, player in enumerate(self.player_list):
            if player.bet_id:
                bet_player = self.find_player(player.bet_id)
                if bet_player.score == max_score:
                    if self.double_reward:
                        score_list[i] = player.stake * 2
                    else:
                        score_list[i] = player.stake
                elif self.bet_failed_decrease:
                    score_list[i] = -player.stake

        for i, player in enumerate(self.player_list):
            player.score += score_list[i]
        
        if self.collision or self.popular:
            collision_dict = {}
            max_betted = 0
            for i, player in enumerate(self.player_list):
                if player.bet_id:
                    if player.bet_id in collision_dict.keys():
                        collision_dict[player.bet_id] += 1
                    else:
                        collision_dict[player.bet_id] = 1
                    if collision_dict[player.bet_id] >= max_betted:
                        max_betted = collision_dict[player.bet_id]

            for i, player in enumerate(self.player_list):
                if self.collision:
                    if player.bet_id:
                        player.score -= (collision_dict[player.bet_id]-1)
                if self.popular:
                    if player.id in collision_dict and collision_dict[player.id] == max_betted:
                        player.score += 2 * collision_dict[player.id]

        if self.patient:
            min_score = None
            for player in self.player_list:
                if min_score is None or player.score < min_score:
                    min_score = player.score
            for player in self.player_list:
                if player.score == min_score:
                    player.score += self.player_num

        self.player_list = sorted(self.player_list, reverse=True)

    @property
    def player_num(self):
        return len(self.player_list)

# test
if __name__ == '__main__':
    playerManager = PlayerManager()
    playerManager.add_player("aaa")
    playerManager.add_player("aab")
    playerManager.add_player("abb")
    playerManager.add_player("bcc")

    print(len(playerManager.player_list))   # 4
    print(playerManager.find_player("ab"))  # abb(0)

    playerManager.remove_player("aaa")      # delete aaa
    print(len(playerManager.player_list))   # 3

    print(playerManager.find_player("aa"))  # aab(0)
    playerManager.remove_player("aa")       # delete aab
    print(len(playerManager.player_list))   # 2

    print(playerManager.find_player("ab"))  # abb(0)
    print(playerManager.find_player("b"))   # bcc(0)
    print(playerManager.find_player("aa"))  # error