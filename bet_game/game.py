from .player import PlayerManager
from .song  import *
from .quest import QuestPool
from .event import RandomEvent
from .utils import GameplayError, Logger
from functools import cmp_to_key

class Game:
    STATUS_000_UNAVAILABLE = 0
    STATUS_100_DRAW_EVENT = 100
    STATUS_101_DRAW_QUEST = 101
    STATUS_102_VERIFY = 102
    STATUS_103_BET = 103
    STATUS_104_PLAY = 104
    STATUS_105_PREPROCESS = 105
    STATUS_106_EVALUATE_SCORE = 106
    STATUS_107_EVALUATE_BET = 107
    STATUS_108_END_TURN = 108
    STATUS_200_FINISHED = 200

    def __init__(self, game_type='arcaea', turns=5):
        self.__game_type = game_type
        if self.__game_type == "arcaea":
            self.song_manager = ArcaeaSongPackageManager()
        elif self.__game_type == "phigros":
            self.song_manager = PhigrosSongPackageManager()
        else:
            raise GameplayError("Currently Only Support arcaea and phigros")
        self.__play_manager = PlayerManager()
        self.__quest_pool = QuestPool()
        self.__logger = Logger()
        self.__random_event = RandomEvent(self.__play_manager, logger=self.__logger, game_type=game_type)

        self.__turns = turns
        self.reset_round(turns)

    @property
    def finished(self):
        return self.__status == self.STATUS_200_FINISHED

    @property
    def winner(self):
        if not self.__winner is None:
            return self.__winner
        if self.__status == self.STATUS_200_FINISHED:
            max_score = None
            for player in self.__play_manager.player_list:
                if max_score is None or player.score > max_score:
                    max_score = player.score

            winner = ""
            for player in self.__play_manager.player_list:
                if player.score == max_score:
                    winner = winner + player.id + ", "
            self.__winner = winner[:-2]
            return self.__winner
        else:
            return ""

    def reset_round(self, turn):
        self.__turns = turn
        self.__cur_turn = 1
        self.__winner = None
        self.__current_quest = None
        self.__status = self.STATUS_000_UNAVAILABLE
        self.__play_manager.reset_round()
        self.reset_turn()

    def reset_turn(self):
        self.__play_manager.reset_turn()
        self.__current_quest = None
        self.__bet_num = 0
        self.__gameplay_num = 0

    def log(self, s:str, file=True):
        self.__logger.log(s, file)

    # helper function
    def check_status(self, status):
        if self.__status != status:
            raise GameplayError(f'Invalid operation. The current status is {self.__status}')

    # player and init
    def enroll(self, id:str):
        self.__play_manager.add_player(id)

    def remove(self, id:str):
        self.__play_manager.remove_player(id)

    def add_quest(self, quest_list:list):
        cur_quest_list = self.song_manager.add_quest_list(quest_list)
        self.__quest_pool.set_quest_list(cur_quest_list)

    def enable_all(self, en_package=True, en_difficulties=True):
        if en_package:
            self.song_manager.enable_all_packages()
        if en_difficulties:
            self.song_manager.enable_all_difficulties()

    def disable_all(self, dis_package=True, dis_difficulties=True):
        if dis_package:
            self.song_manager.disable_all_packages()
        if dis_difficulties:
            self.song_manager.disable_all_difficulties()

    def enable(self, pac:str):
        self.song_manager.enable(pac)

    def disable(self, pac:str):
        self.song_manager.disable(pac)

    # game play
    def start(self):
        self.__logger.reset_log(self.__game_type)
        self.__random_event.reset()
        self.player_num = self.__play_manager.player_num
        if self.player_num < 2:
            raise GameplayError("At least two players are needed!")
        self.__status = self.STATUS_100_DRAW_EVENT
        self.log(f'Starting {self.__game_type} game with {self.__turns} turns.')

    def draw_event(self):
        self.check_status(self.STATUS_100_DRAW_EVENT)
        self.__random_event.draw_event()
        self.__status = self.STATUS_101_DRAW_QUEST
        self.log(f'-----------------------------------------------', False)
        self.log(f'Plaese start to draw the quest', False)

    def draw_quest(self):
        if self.__status == self.STATUS_102_VERIFY:
            if self.__bet_num > 0:
                raise GameplayError(f'Cannot redraw quests. Some players have already bet')
            redraw = True
            self.__quest_pool.remove_quest(self.__current_quest)
        else:
            self.check_status(self.STATUS_101_DRAW_QUEST)
            redraw = False

        self.__current_quest = self.__quest_pool.draw_quest()
        self.__status = self.STATUS_102_VERIFY

        self.log(f'-----------------------------------------------', False)
        if redraw:
            self.log(f'Redrawing quest: {self.__current_quest.description}.', False)
        else:
            self.log(f'Drawing quest: {self.__current_quest.description}.', False)

    def verify(self):
        self.check_status(self.STATUS_102_VERIFY)
        self.__status = self.STATUS_103_BET

    def bet(self, player_id, bet_id, stake=1):
        if self.__status == self.STATUS_104_PLAY:
            if self.__gameplay_num != 0:
                raise GameplayError(f'Cannot re-bet. Some players have already played')
        else:
            self.check_status(self.STATUS_103_BET)
    
        player = self.__play_manager.find_player(player_id)
        if not player.took_bet:
            self.__bet_num += 1
            player.took_bet = True

        if bet_id:
            bet_player = self.__play_manager.find_player(bet_id)
            if (bet_player.id == player.id):
                raise GameplayError(f'Cannoe bet oneself: {bet_player.id}')
            player.bet_id = bet_player.id
            player.stake = max(min(stake, self.player_num), 1)
        else:
            player.bet_id = None


        
        if self.__bet_num == self.player_num:
            self.__status = self.STATUS_104_PLAY
            self.log(f'All players\' bet are set', False)

    def play(self, player_id, score):
        if (self.__status != self.STATUS_105_PREPROCESS):
            self.check_status(self.STATUS_104_PLAY)
        player = self.__play_manager.find_player(player_id)
        self.__play_manager.set_score(player, score)
        if not player.played:
            player.played = True
            self.__gameplay_num += 1
        
        if self.__gameplay_num == self.player_num:
            self.__status = self.STATUS_105_PREPROCESS
            self.log(f'All players\' playing score are set', False)

    def evaluate_preprocess(self):
        self.check_status(self.STATUS_105_PREPROCESS)
        self.__play_manager.preprocess_bet_score()
        self.log(str(self))
        self.__status = self.STATUS_106_EVALUATE_SCORE

    def evaluate_score(self):
        self.check_status(self.STATUS_106_EVALUATE_SCORE)
        self.__play_manager.evaluate_playing_score()
        self.log(str(self))
        self.__status = self.STATUS_107_EVALUATE_BET

    def evaluate_bet(self):
        self.check_status(self.STATUS_107_EVALUATE_BET)
        self.__play_manager.evaluate_bet_score()
        self.log(str(self))
        self.__status = self.STATUS_108_END_TURN

    def end_turn(self):
        self.check_status(self.STATUS_108_END_TURN)
        self.__play_manager.evaluate_end_event()
        self.reset_turn()
        self.log(str(self))
        self.__cur_turn += 1
        if self.__cur_turn > self.__turns:
            self.__status = self.STATUS_200_FINISHED
            self.log(f'-----------------------------------------------')
            self.log(f'The game is over. Congrats to the winner:{self.winner}!')
            self.log(f'-----------------------------------------------')
        else:
            self.__status = self.STATUS_100_DRAW_EVENT

    def __str__(self):
        turn = f'-----------------------------------------------\n'
        turn = turn + f'turn: {self.__cur_turn}/{self.__turns}\n'

        head = ''
        if self.__status == self.STATUS_100_DRAW_EVENT:
            head = f'Drawing the next event------.\n'
        if self.__status == self.STATUS_101_DRAW_QUEST:
            head = f'Drawing the next quest.\n'
        elif self.__status == self.STATUS_103_BET:
            head = f'The quest is {self.__current_quest.description}. Players are betting.\n'
        elif self.__status == self.STATUS_104_PLAY:
            head = f'Playing {self.__current_quest.description}.\n'
        elif self.__status == self.STATUS_105_PREPROCESS:
            head = f'Prerpocess for points deduction of bet.\n'
        elif self.__status == self.STATUS_106_EVALUATE_SCORE:
            head = f'Evaluating scores of {self.__current_quest.description}.\n'
        elif self.__status == self.STATUS_107_EVALUATE_BET:
            head = f'Evaluating bet results.\n'

        player_infos = []
        if self.__status == self.STATUS_105_PREPROCESS:
            for player in sorted(self.__play_manager.player_list, reverse=True):
                if not player.betted is None:
                    player_infos.append(f'    {player} got betted {player.betted} time(s)')
                else:
                    player_infos.append(f'    {player} didn\'t get betted')
        elif self.__status == self.STATUS_106_EVALUATE_SCORE:
            for player in sorted(self.__play_manager.player_list, reverse=True,
                    key=cmp_to_key(self.__play_manager.score_cmp)):
                player_infos.append(f'    {player} result in {player.playing_score}')
        elif self.__status == self.STATUS_107_EVALUATE_BET:
            for player in sorted(self.__play_manager.player_list, reverse=True):
                if player.bet_id is None:
                    player_infos.append(f'    {player} not betting')
                elif player.bet_reward > 0:
                    player_infos.append(f'    {player} bets {player.stake} point(s) on {player.bet_id}: succuessed')
                else:
                    player_infos.append(f'    {player} bets {player.stake} point(s) on {player.bet_id}: failed')
        else:
            player_infos = [f'    {player}' for player in sorted(self.__play_manager.player_list, reverse=True)]
        player_infos_str = '\n'.join(player_infos)
        return f'{turn}{head}{player_infos_str}'
