from TestParser import TestParser

import re

class BuyParser(TestParser):
    def __init__(self, UserDB, AvailableGameDB, GameCollectionDB, config, transaction):
        super().__init__(UserDB, AvailableGameDB, GameCollectionDB, config)
        self.game_name = "none"
        self.transaction = transaction

        self.inputs_to_check = {
            "game_name": self.validate_game_name,
            "seller": self.validate_seller
        }

        self.get_inputs_to_check()

    def parse(self, test_lines):
        # start parse with finding where input logs out and getting user information
        logout_line, self.curr_username, self.curr_credit, self.curr_user_type = self.start_parse_get_user_and_logout(test_lines)
        #if logout_line == -1:
        #    return [self.transaction, "ERROR_did_not_logout", None, None, self.curr_user_type]

        # check if user is sell-standard, which cannot bid
        user_type_check = self.helper_buy_invalid_user_type(test_lines, self.curr_user_type)
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

    def helper_buy_invalid_user_type(self, test_lines, user_type):
        # if sell-standard, cannot bid so must logout
        if (user_type == "ss"):
            if (len(test_lines) <= self.logout_other_transaction) or (test_lines[self.logout_other_transaction] == self.logout_name):
                return f"invalid_usertype_SS"
            else:
                return "ERROR_SS_did_not_fail"
            
        return "success"
    
    def validate_game_name(self, game_name):
        # validate game name
        if (self.available_gameDB.is_invalid_game_name(game_name)):
            return "invalid_game_name"
        elif (self.game_collectionDB.is_already_own_game(game_name, self.curr_username)): # already owns game
            return "already_own_game"
        
        # validate credit - get game cost and user credit
        game_cost = self.available_gameDB.get_price(game_name)
        user_credit = self.curr_credit

        if (game_cost > user_credit):
            return "insuffcient_funds"
    
        # set the game name for other validate functions
        self.game_name = game_name
        return "success"
    
    def validate_seller(self, seller):
        if (self.userDB.is_invalid_username(seller)):
            return "__invalid_seller"
        elif (self.available_gameDB.get_seller(self.game_name) != seller):
            return "__incorrect_seller"
        elif (self.curr_username == seller):
            return "user_is_seller"
        
        return "success"