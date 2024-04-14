from FileIO import FileIO
import re

class GameCollectionDB:
    def __init__(self, game_collection_fp, config):
        self.game_collection_fp = game_collection_fp
        self.game_collection = []
        self.config = config

        self.load_game_collection()

    def load_game_collection(self):
        game_collection_lines = FileIO.read_file(self.game_collection_fp)

        # get index # from config file
        index_game_name = self.config['game_collection']['game_name']
        index_owner = self.config['game_collection']['owner']
        end_of_file = self.config['game_collection']['end']

        for line in game_collection_lines:
            
            # remove \n and underscores (if any)
            line = line.replace("\n", "")
            line = (re.sub(r'_+', ' ', line)).split()

            # for groups that add END or EXIT etc to the end of the available_items_file
            if ((end_of_file != "none") and (end_of_file == line[0])):
                break
            
            # get values from line at indexes from config file
            game_name = line[index_game_name]
            owner = line[index_owner]

            # append to an array
            self.game_collection.append([game_name, owner])

    def is_already_own_game(self, game_name, owner):
        return [game_name, owner] in self.game_collection
    
    def get_owner(self, game_name):
        # need to fix, array not dictionary now
        return self.game_collection.get(game_name)[0]
    