from FileIO import FileIO
import re

class ItemDB:
    def __init__(self, item_fp, config):
        self.item_fp = item_fp
        self.item_accounts = {}
        self.config = config

        self.load_item_accounts()

    def load_item_accounts(self):
        item_lines = FileIO.read_file(self.item_fp)

        # get index # from config file
        index_item_name = self.config['item']['item_name']
        index_seller = self.config['item']['seller']
        index_buyer = self.config['item']['buyer']
        index_auction_length = self.config['item']['auction_length']
        index_curr_bid = self.config['item']['curr_bid']
        end_of_file = self.config['item']['end']

        for line in item_lines:
            # for groups that add END or EXIT etc to the end of the available_items_file
            if ((end_of_file != "none") and (end_of_file == line)):
                break
            
            # remove \n and underscores (if any)
            line = line.replace("\n", "")
            line = (re.sub(r'_+', ' ', line)).split()

            # get values from line at indexes from config file
            item_name = line[index_item_name]
            seller = line[index_seller]
            auction_length_string = line[index_auction_length]
            curr_bid_string = line[index_curr_bid]
            
            # if buyer listed, add value
            if (len(line) == 5):
                buyer = line[index_buyer]
            else:
                buyer = 'none'

            # configure bid to int
            curr_bid_temp = curr_bid_string.replace(".00", "")
            curr_bid = float(curr_bid_temp)

            # configure auction length to int
            auction_length = int(auction_length_string)

            self.item_accounts[item_name] = [seller, buyer, curr_bid, auction_length]

    def is_invalid_item_name(self, item_name):
        return item_name not in self.item_accounts
    
    def get_seller(self, item_name):
        return self.item_accounts.get(item_name)[0]

    def get_bidder(self, item_name):
        return self.item_accounts.get(item_name)[1]

    def get_bid(self, item_name):
        return self.item_accounts.get(item_name)[2]

    def get_auction_length(self, item_name):
        return self.item_accounts.get(item_name)[3]

            



