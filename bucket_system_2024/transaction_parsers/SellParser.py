from TestParser import TestParser

import re

class SellParser(TestParser):
    def __init__(self, UserDB, AvailableGameDB, GameCollectionDB, config, transaction):
        super().__init__(UserDB, AvailableGameDB, GameCollectionDB, config)
        self.transaction = transaction

        self.inputs_to_check = {
            "game_name": self.validate_game_name,
            "price": self.validate_price
        }

        self.get_inputs_to_check()

    def parse(self, test_lines):
        # start parse with finding where input logs out and getting user information
        logout_line, self.curr_username, self.curr_credit, self.curr_user_type = self.start_parse_get_user_and_logout(test_lines)
        #if logout_line == -1:
        #    return [self.transaction, "ERROR_did_not_logout", None, None, self.curr_user_type]

        # check if user is buy-standard, which cannot advertise
        user_type_check = self.helper_sell_invalid_user_type(test_lines, self.curr_user_type)
        if (user_type_check != "success"):
            return [self.transaction, user_type_check, None, None, self.curr_user_type, logout_line]

        for key, value in self.inputs_to_check.items():
            # check if input is valid
            result = self.validate_input(self.transaction, test_lines, key, value, logout_line, self.curr_user_type)
            if (result != "success"):
                return result
        
        logout_check = self.get_config_value("logout", test_lines, self.transaction, logout_line)
        if (logout_check != "none"):
            return self.bucket_category_message(self.transaction, "over_1_transaction_limit", logout_line, self.curr_user_type)
        
        return self.bucket_category_message(self.transaction, "success", logout_line, self.curr_user_type)

    def helper_sell_invalid_user_type(self, test_lines, user_type):
        # if buy-standard, cannot advertise so must logout
        if (user_type == "bs"):
            if (len(test_lines) <= self.logout_other_transaction) or (test_lines[self.logout_other_transaction] == self.logout_name):
                return f"invalid_usertype_BS"
            else:
                return "ERROR_BS_did_not_fail"
            
        return "success"
    
    def validate_game_name(self, game_name):
        # check if game name too long
        if (len(game_name) > 25):
            return "game_name_over_25_chars"
        # check if game name already exists
        elif (not (self.available_gameDB.is_invalid_game_name(game_name))):
            return "game_name_already_exists"
        return "success"
    
    def validate_price(self, price):
    
        if re.match(r"^\d+\.\d{3,}$", price):
            return "price_w_too_many_decimals"
        try:
            if (float(price) >= 1000.0):
                return "over_max_price"
            elif (float(price) <= 0):
                return "less_than_0_or_0"
            return "success"
        # not a digit, different case
        except ValueError:
            return "price_not_number"