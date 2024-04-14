from TestParser import TestParser

import re

class AdvertiseParser(TestParser):
    def __init__(self, UserDB, ItemDB, config, transaction):
        super().__init__(UserDB, ItemDB, config)
        self.transaction = transaction

        self.inputs_to_check = {
            "item_name": self.validate_item_name,
            "initial_bid": self.validate_initial_bid,
            "auction_length": self.validate_auction_length
        }

        self.get_inputs_to_check()

    def parse(self, test_lines):
        # start parse with finding where input logs out and getting user information
        logout_line, self.curr_username, self.curr_credit, self.curr_user_type = self.start_parse_get_user_and_logout(test_lines)
        if logout_line == -1:
            return f"ERROR_did_not_logout_{self.transaction}"

        # check if user is buy-standard, which cannot advertise
        user_type_check = self.helper_advertise_invalid_user_type(test_lines, self.curr_user_type)
        if (user_type_check != "success"):
            return user_type_check
        
        for key, value in self.inputs_to_check.items():
            # check if input is valid
            result = self.validate_input(self.transaction, test_lines, key, value, logout_line, self.curr_user_type)
            if (result != "success"):
                return result
        
        logout_check = self.get_config_value("logout", test_lines, self.transaction, logout_line)
        if (logout_check != "none"):
            return self.bucket_category_message(self.transaction, "over_1_transaction_limit", self.curr_user_type)
        
        return self.bucket_category_message(self.transaction, "success", self.curr_user_type)

    def helper_advertise_invalid_user_type(self, test_lines, user_type):
        # if buy-standard, cannot advertise so must logout
        if (user_type == "bs"):
            if (test_lines[self.logout_other_transaction] == 'logout'):
                return f"advertise_invalid_usertype_BS"
            else:
                return "ERROR_BS_did_not_fail_advertise"
            
        return "success"
    
    def validate_item_name(self, item_name):
        # check if item name too long
        if (len(item_name) > 25):
            return "item_name_over_25_chars"
        # check if item name already exists
        elif (not (self.itemDB.is_invalid_item_name(item_name))):
            return "item_name_already_exists"
        return "success"
    
    def validate_initial_bid(self, initial_bid):
    
        if re.match(r"^\d+\.\d{3,}$", initial_bid):
            return "bid_w_too_many_decimals"
        try:
            if (float(initial_bid) >= 1000.0):
                return "over_max_price"
            elif (float(initial_bid) <= 0):
                return "less_than_0_or_0"
            return "success"
        # not a digit, different case
        except ValueError:
            return "initial_bid_not_digit"
        
    def validate_auction_length(self, auction_length):
        try:
            auction_length = int(auction_length)
            
            # test for checking if auction length over 100
            if (int(auction_length) > 100):
                return "over_max_auction_length"
            elif (int(auction_length) <= 0):
                return "under_min_auction_length"
            return "success"
        except ValueError:
            return "auction_length_not_digit"