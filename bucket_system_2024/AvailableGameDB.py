from FileIO import FileIO
import re

class AvailableGameDB:
    def __init__(self, game_fp, config):
        self.game_fp = game_fp
        self.available_games = {}
        self.config = config

        self.load_available_games()

    def load_available_games(self):
        game_lines = FileIO.read_file(self.game_fp)

        # get index # from config file
        index_game_name = self.config['available_game']['game_name']
        index_seller = self.config['available_game']['seller']
        index_price = self.config['available_game']['price']
        end_of_file = self.config['available_game']['end']

        for line in game_lines:
            
            # remove \n and underscores (if any)
            line = line.replace("\n", "")
            line = (re.sub(r'_+', ' ', line)).split()

            # for groups that add END or EXIT etc to the end of the available_items_file
            if ((end_of_file != "none") and (end_of_file == line[0])):
                break
            
            # get values from line at indexes from config file
            game_name = line[index_game_name]
            seller = line[index_seller]
            curr_price_string = line[index_price]

            # configure bid to int
            curr_price_temp = curr_price_string.replace(".00", "")
            price = float(curr_price_temp)

            self.available_games[game_name] = [seller, price]

    def is_invalid_game_name(self, game_name):
        return game_name not in self.available_games
    
    def get_seller(self, game_name):
        return self.available_games.get(game_name)[0]

    def get_price(self, game_name):
        return self.available_games.get(game_name)[1]
