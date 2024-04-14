from TestParser import TestParser

import re

class BidParser(TestParser):
    def __init__(self, UserDB, ItemDB, config, transaction):
        super().__init__(UserDB, ItemDB, config)
        self.item_name = "none"
        self.transaction = transaction

        self.inputs_to_check = {
            "item_name": self.validate_item_name,
            "bid": self.validate_new_bid,
            "seller": self.validate_seller
        }

        self.get_inputs_to_check()

    def parse(self, test_lines):

        # start parse with finding where input logs out and getting user information
        logout_line, self.curr_username, self.curr_credit, self.curr_user_type = self.start_parse_get_user_and_logout(test_lines)
        if logout_line == -1:
            return f"ERROR_did_not_logout_{self.transaction}"

        # check if user is sell-standard, which cannot bid
        user_type_check = self.helper_bid_invalid_user_type(test_lines, self.curr_user_type)
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

    def helper_bid_invalid_user_type(self, test_lines, user_type):
        # if sell-standard, cannot bid so must logout
        if (user_type == "ss"):
            if (test_lines[self.logout_other_transaction] == 'logout'):
                return f"bid_invalid_usertype_SS"
            else:
                return "ERROR_SS_did_not_fail_bid"
            
        return "success"
    
    def validate_item_name(self, item_name):
        if (self.itemDB.is_invalid_item_name(item_name)):
            return "invalid_item_name"
        
        # set the item name for other validate functions
        self.item_name = item_name
        return "success"
    
    def validate_seller(self, seller):
        if (self.itemDB.get_seller(self.item_name) != seller):
            return "incorrect_seller"
        elif (self.curr_username == seller):
            return "user_is_seller"
        
        return "success"
    
    def validate_new_bid(self, bid):
        curr_bid = self.itemDB.get_bid(self.item_name)

        if re.match(r"^\d+\.\d{3,}$", bid):
            return "bid_w_too_many_decimals"

        # try to convert to float, if not digit, different case
        try:
            bid = float(bid)
        except ValueError:
            return "credit_not_digit"
        
        if (bid < (curr_bid * 1.05)):
            return "less_than_curr_bid_5_percent"
        return "success"