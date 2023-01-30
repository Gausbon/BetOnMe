class GameplayError(Exception):
    pass

class ParseError(Exception):
    pass

class TrieNode:
    def __init__(self):
        self.player = None
        self.children = {}

    def find(self, id:str):
        if id == "":
            if self.player:
                return self.player
            else:
                if len(self.children) == 0:
                    raise GameplayError('Invalid Player ID!')
                elif len(self.children) > 1:
                    raise GameplayError('Duplicate Player ID in blurry search!')
                else:
                    return list(self.children.values())[0].find(id)
        else:
            if id[0] not in self.children.keys():
                raise GameplayError("Invalid Player ID!")
            child = self.children[id[0]]
            return child.find(id[1:])

    def delete(self, id:str):
        if id == "":
            if self.player:
                player_id = self.player.id
                self.player = None
            else:
                if len(self.children) == 0:
                    raise GameplayError('Invalid Player ID!')
                elif len(self.children) > 1:
                    raise GameplayError('Duplicate Player ID in blurry search!')
                else:
                    node_del, player_id = list(self.children.values())[0].delete(id)
                    if node_del:
                        del(list(self.children.values())[0])
        else:
            if id[0] not in self.children.keys():
                raise GameplayError("Invalid Player ID!")
            child = self.children[id[0]]
            node_del, player_id = child.delete(id[1:])
            if node_del:
                del(self.children[id[0]])

        if self.player is None and len(self.children) == 0:
            return True, player_id
        return False, player_id

    def insert(self, id:str, player):
        if id == "":
            if self.player:
                raise GameplayError("Duplicate Player id!")
            else:
                self.player = player
            return
        else:
            if id[0] not in self.children.keys():
                self.children[id[0]] = TrieNode()
            child = self.children[id[0]]
            child.insert(id[1:], player)
