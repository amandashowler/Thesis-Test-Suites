from UserDB import UserDB
from ItemDB import ItemDB

import re

class TestParser:
    def __init__(self, UserDB, ItemDB, config):
        self.userDB = UserDB
        self.itemDB = ItemDB
        self.config = config
        self.curr_line = 0

        self.logout_just_login = config['logout']['just_login']
        self.logout_other_transaction = config['logout']['invalid_type']

    def get_user(self, curr_username):
        credit_user = self.userDB.get_credit(curr_username)
        user_type = self.userDB.get_user_type(curr_username)

        return curr_username, credit_user, user_type

    def get_logout_line(self, test_lines):
        # set where transaction is dependant on if there is a password
        self.set_curr_line()

        try:
            return test_lines.index("logout")
        except ValueError:
            return -1

    def set_curr_line(self):
        # set where transaction is dependant on if it has a password
        if (self.config['user']['password'] == -1):
            self.curr_line = 2
        else:
            self.curr_line = 3

    def get_config_value(self, transaction, test_lines, line_type, logout_line):
        self.curr_line += 1

        # if user logged out prematurly, no config value
        if (self.curr_line == logout_line):
            return 'none'
        else:
            return test_lines[self.config[transaction][line_type]]
        
    def helper_addcredit_validate_credit(self, credit, credit_user):
        # try to get credit, if not a #, testing for string input
        try:
            credit = float(credit)
        except ValueError:
            return "credit_not_digit"

        if ((credit + credit_user) > 999999):
            return "credit_too_high"
        elif (credit > 1000):
            return "over_1000"
        elif (credit <= 0):
            return "less_than_0_or_0"
        
        return "success"
    
    def helper_addcredit_validate_username(self, username_admin, curr_username):
        
        if (self.userDB.is_invalid_username(username_admin)):
            return "user_not_found"
        elif (username_admin != curr_username):
            return "success_diff_user"
        
        return "success"

    def parse_addcredit(self, test_lines, transaction):
        transaction_logout = "addcredit"

        logout_line = self.get_logout_line(test_lines)
        if (logout_line == -1):
            return f"ERROR_did_not_logout_{transaction}"

        # get user information from valid username
        curr_username, credit_user, user_type = self.get_user(test_lines[1])
        
        # set which row to get from config file
        line_type = 'credit_admin' if user_type == 'AA' else 'credit'

        # if logout before invalid input, error, premature logout
        credit = self.get_config_value(transaction, test_lines, line_type, logout_line)
        if (credit == 'none'):
            return f"ERROR_premature_logout_{transaction}"
        
        # check if valid credit
        credit_check = self.helper_addcredit_validate_credit(credit, credit_user)
        if (credit_check != "success"):
            return f"{transaction}_{credit_check}_{user_type}"
        
        # if admin user, check validity of username entered
        if (user_type == 'AA'):
            username_admin = self.get_config_value(transaction, test_lines, 'username_admin', logout_line)
            if (username_admin == 'none'):
                return f"ERROR_premature_logout_{transaction}"
            
            # check if valid username
            username_check = self.helper_addcredit_validate_username(username_admin, curr_username)
            if (username_check != "success"):
                return f"{transaction}_{username_check}_{user_type}"
            
            # change transaction for logout check
            transaction_logout = "addcredit_AA"
            
        logout_check = self.get_config_value("logout", test_lines, transaction, logout_line)
        if (logout_check != "none"):
            return f"{transaction}_over_1_transaction_limit_{user_type}"
        
        return f"{transaction}_success_{user_type}"
    
    def helper_advertise_invalid_user_type(self, test_lines, user_type):
        # if buy-standard, cannot advertise so must logout
        if (user_type == 'BS'):
            if (test_lines[self.logout_other_transaction] == 'logout'):
                return f"advertise_invalid_usertype_BS"
            else:
                return "ERROR_BS_did_not_fail_advertise"
            
        return "success"
    
    def helper_advertise_validate_item_name(self, item_name):
        # check if item name too long
        if (len(item_name) > 25):
            return "item_name_over_25_chars"
        # check if item name already exists
        elif (not (self.itemDB.is_invalid_item_name(item_name))):
            return "item_name_already_exists"
        return "success"
    
    def helper_advertise_validate_initial_bid(self, initial_bid):
    
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
        
    def helper_advertise_validate_auction_length(self, auction_length):
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

    def parse_advertise(self, test_lines, transaction):

        logout_line = self.get_logout_line(test_lines)
        if (logout_line == -1):
            return f"ERROR_did_not_logout_{transaction}"

        # get user information from valid username
        curr_username, credit_user, user_type = self.get_user(test_lines[1])

        # check if user is buy-standard, which cannot advertise
        user_type_check = self.helper_advertise_invalid_user_type(test_lines, user_type)
        if (user_type_check != "success"):
            return user_type_check

        # check if item_name is valid
        item_name = self.get_config_value(transaction, test_lines, 'item_name', logout_line)
        if (item_name == 'none'):
            return f"ERROR_premature_logout_{transaction}"
        
        item_name_check = self.helper_advertise_validate_item_name(item_name)
        if (item_name_check != "success"):
            return f"{transaction}_{item_name_check}_{user_type}"
        
        # check if initial bid is valid
        initial_bid = self.get_config_value(transaction, test_lines, 'initial_bid', logout_line)
        if (initial_bid == 'none'):
            return f"ERROR_premature_logout_{transaction}"

        initial_bid_check = self.helper_advertise_validate_initial_bid(initial_bid)
        if (initial_bid_check != "success"):
            return f"{transaction}_{initial_bid_check}_{user_type}"
        
        # check if auction_length is valid
        auction_length = self.get_config_value(transaction, test_lines, 'auction_length', logout_line)
        if (auction_length == 'none'):
            return "ERROR_premature_logout_" + transaction
        
        auction_length_check = self.helper_advertise_validate_auction_length(auction_length)
        if (auction_length_check != "success"):
            return f"{transaction}_{auction_length_check}_{user_type}"
        
        logout_check = self.get_config_value("logout", test_lines, transaction, logout_line)
        if (logout_check != "none"):
            return f"{transaction}_over_1_transaction_limit_{user_type}"
        
        return f"{transaction}_success_{user_type}"
    
    def parse_allitems(self, test_lines):
        transaction = "allitems"

        logout_line = self.get_logout_line(test_lines)
        if (logout_line == -1):
            return f"ERROR_did_not_logout_{transaction}"
        
        user_type = self.userDB.get_user_type(test_lines[1]) # username always on line 1

        return f"{transaction}_success_{user_type}"
    
    def parse_allusers(self, test_lines):
        transaction = "allusers"

        logout_line = self.get_logout_line(test_lines)
        if (logout_line == -1):
            return f"ERROR_did_not_logout_{transaction}"
        
        user_type = self.userDB.get_user_type(test_lines[1]) # username always on line 1

        return f"{transaction}_success_{user_type}"
    
    def helper_bid_invalid_user_type(self, test_lines, user_type):
        # if sell-standard, cannot bid so must logout
        if (user_type == 'SS'):
            if (test_lines[self.logout_other_transaction] == 'logout'):
                return f"bid_invalid_usertype_SS"
            else:
                return "ERROR_SS_did_not_fail_bid"
            
        return "success"
    
    def helper_bid_validate_item_name(self, item_name):
        if (self.itemDB.is_invalid_item_name(item_name)):
            return "invalid_item_name"
        
        return "success"
    
    def helper_bid_validate_seller(self, curr_username, item_name, seller):
        if (self.itemDB.get_seller(item_name) != seller):
            return "incorrect_seller"
        elif (curr_username == seller):
            return "user_is_seller"
        
        return "success"
    
    def helper_bid_validate_new_bid(self, item_name, bid):
        curr_bid = self.itemDB.get_bid(item_name)

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
    
    def parse_bid(self, test_lines, transaction):

        logout_line = self.get_logout_line(test_lines)
        if (logout_line == -1):
            return f"ERROR_did_not_logout_{transaction}"

        # get user information from valid username
        curr_username, credit_user, user_type = self.get_user(test_lines[1])

        # check if user is sell-standard, which cannot bid
        user_type_check = self.helper_bid_invalid_user_type(test_lines, user_type)
        if (user_type_check != "success"):
            return user_type_check

        # check if item_name is valid
        item_name = self.get_config_value(transaction, test_lines, 'item_name', logout_line)
        if (item_name == 'none'):
            return "ERROR_premature_logout_" + transaction

        item_name_check = self.helper_bid_validate_item_name(item_name)
        if (item_name_check != "success"):
            return f"{transaction}_{item_name_check}_{user_type}"
        
        # check if seller name is valid
        seller = self.get_config_value(transaction, test_lines, 'seller', logout_line)
        if (seller == 'none'):
            return "ERROR_premature_logout_" + transaction

        seller_check = self.helper_bid_validate_seller(curr_username, item_name, seller)
        if (seller_check != "success"):
            return f"{transaction}_{seller_check}_{user_type}"
        
        # check if new bid is valid
        bid = self.get_config_value(transaction, test_lines, 'bid', logout_line)
        if (bid == 'none'):
            return "ERROR_premature_logout_" + transaction
        
        bid_check = self.helper_bid_validate_new_bid(item_name, bid)
        if (bid_check != "success"):
            return f"{transaction}_{bid_check}_{user_type}"
        
        logout_check = self.get_config_value("logout", test_lines, transaction, logout_line)
        if (logout_check != "none"):
            return f"{transaction}_over_1_transaction_limit_{user_type}"
        
        return f"{transaction}_success_{user_type}"
    
    def helper_invalid_user_type(self, test_lines, user_type, logout_line):
        # if user is not admin, fail to use create or delete, must logout
        if (user_type != 'AA'):
            if (logout_line == self.logout_other_transaction):
                return "not_admin"
            return "ERROR_not_AA_did_not_fail"
        
        # if it is an admin, test the other lines
        return "success"
    
    def helper_create_validate_username_to_create(self, username_to_create):
        if (len(username_to_create) > 15):
            return "username_long"
        elif (len(username_to_create) < 1):
            return "username_short"
        elif (not self.userDB.is_invalid_username(username_to_create)): # if username already exists
            return "username_already_exists"
        
        return "success"
    
    def helper_create_validate_type_to_create(self, type_to_create):
        if (type_to_create != 'AA' and type_to_create != 'FS'and type_to_create != 'SS'and type_to_create != 'BS'):
            return "user_type_not_valid"
        return "success"
    
    def helper_create_validate_password_to_create(self, password_to_create):
        if (len(password_to_create) > 15):
            return "password_long"
        elif (len(password_to_create) < 1):
            return "password_short"
        
        return "success"
    
    def parse_create(self, test_lines, transaction):

        logout_line = self.get_logout_line(test_lines)
        if (logout_line == -1):
            return f"ERROR_did_not_logout_{transaction}"

        # get user information from valid username
        curr_username, credit_user, user_type = self.get_user(test_lines[1])

        # check if valid user_type, must be admin
        user_type_check = self.helper_invalid_user_type(test_lines, user_type, logout_line)
        if (user_type_check != "success"):
            return f"{transaction}_{user_type_check}_{user_type}"
        
        # check if username_to_create is valid
        username_to_create = self.get_config_value(transaction, test_lines, 'username_to_create', logout_line)
        if (username_to_create == 'none'):
            return "ERROR_premature_logout_" + transaction
        
        username_to_create_check = self.helper_create_validate_username_to_create(username_to_create)
        if (username_to_create_check != "success"):
            return f"{transaction}_{username_to_create_check}_{user_type}"
        
        # check if type_to_create is valid
        type_to_create = self.get_config_value(transaction, test_lines, 'type_to_create', logout_line)
        if (type_to_create == 'none'):
            return "ERROR_premature_logout_" + transaction
        
        type_to_create_check = self.helper_create_validate_type_to_create(type_to_create)
        if (type_to_create_check != "success"):
            return f"{transaction}_{type_to_create_check}_{user_type}"
        
        # check if # check if password_to_create is valid
        password_to_create = self.get_config_value(transaction, test_lines, 'password_to_create', logout_line)
        if (password_to_create == 'none'):
            return "ERROR_no_password_new_user_" + transaction
        
        password_to_create_check = self.helper_create_validate_password_to_create(password_to_create)
        if (password_to_create_check != "success"):
            return f"{transaction}_{type_to_create_check}_{user_type}"
        
        logout_check = self.get_config_value("logout", test_lines, transaction, logout_line)
        if (logout_check != "none"):
            return f"{transaction}_over_1_transaction_limit_{user_type}"
            
        return f"{transaction}_success_{user_type}"
    
    def helper_create_validate_username_to_delete(self, username_to_delete, curr_username):
        if (self.userDB.is_invalid_username(username_to_delete)): # username does not exist
            return "username_not_exist"
        elif (username_to_delete == curr_username): # deleting current user
            return "current_account_logged_in"
        
        return "success"

    
    def parse_delete(self, test_lines, transaction):

        logout_line = self.get_logout_line(test_lines)
        if logout_line == -1:
            return f"ERROR_did_not_logout_{transaction}"

        # get user information from valid username
        curr_username, credit_user, user_type = self.get_user(test_lines[1])

        # check if valid user_type, must be admin
        user_type_check = self.helper_invalid_user_type(test_lines, user_type, logout_line)
        if (user_type_check != "success"):
            return f"{transaction}_{user_type_check}_{user_type}"
        
        # check if username_to_delete is valid
        username_to_delete = self.get_config_value(transaction, test_lines, 'username_to_delete', logout_line)
        if (username_to_delete == 'none'):
            return "ERROR_premature_logout_" + transaction
        
        username_to_delete_check = self.helper_create_validate_username_to_delete(username_to_delete, curr_username)
        if (username_to_delete_check != "success"):
            return f"{transaction}_{username_to_delete_check}_{user_type}"
        
        logout_check = self.get_config_value("logout", test_lines, transaction, logout_line)
        if (logout_check != "none"):
            return f"{transaction}_over_1_transaction_limit_{user_type}"

        return f"{transaction}_success_{user_type}"

    def parse_login(self, test_lines):
        transaction = 'login'
        what_failed = 'none'

        self.set_curr_line()

        if (len(test_lines) < 1) or (test_lines[0] != 'login'):
            what_failed = "not_first_fail"

        elif (len(test_lines) < 2) or (self.userDB.is_invalid_username(test_lines[1])):
            what_failed = "username_fail"
        
        elif ((self.userDB.get_password(test_lines[1]) != 'none') and ((len(test_lines) < 3) or (self.userDB.is_invalid_password(test_lines[1], test_lines[2])))):
            what_failed = "password_fail"
        
        elif (test_lines[self.logout_just_login] == 'logout'):
            user_type = self.userDB.get_user_type(test_lines[1])

            what_failed = 'success_' + user_type
        
        elif (test_lines[self.logout_just_login] == 'login'):
            user_type = self.userDB.get_user_type(test_lines[1])

            what_failed = '2nd_login_' + user_type + '_fail'
        
        else:
            # test for another transaction - still = none
            return what_failed
        
        return 'login_' + what_failed
    
    def helper_refund_validate_user(self, username, username_text, type_not_valid):

        if self.userDB.is_invalid_username(username):
            return f"{username_text}_not_exist"
        
        elif (self.userDB.get_user_type(username) == type_not_valid):
            return f"{username_text}_{type_not_valid}_not_valid"
        
        return "none"
    
    def parse_refund(self, test_lines, transaction):

        logout_line = self.get_logout_line(test_lines)
        if logout_line == -1:
            return f"ERROR_did_not_logout_{transaction}"

        # get user information from valid username
        curr_username, credit_user, user_type = self.get_user(test_lines[1])

        # check if valid user_type, must be admin
        user_type_check = self.helper_invalid_user_type(test_lines, user_type, logout_line)
        if (user_type_check != "success"):
            return f"{transaction}_{user_type_check}_{user_type}"

        # find which 1 goes first
        row_seller = self.config[transaction]['seller']
        row_buyer = self.config[transaction]['buyer']
        row_credit = self.config[transaction]['credit']

        # sort dictionary in order
        possible_rows = {"seller": row_seller, "buyer": row_buyer, "credit": row_credit}
        possible_rows = sorted(possible_rows.items(), key=lambda item: item[1])
        
        for key, value in possible_rows:
            if (key == "seller"):
                username_seller = test_lines[row_seller]
                
                what_failed = self.helper_refund_validate_user(username_seller, "seller", "BS")

            elif (key == "buyer" or key == "credit"):
                # check if a valid buyer first
                username_buyer = test_lines[row_buyer]
                
                what_failed = self.helper_refund_validate_user(username_buyer, "buyer", "SS")

                # if buy failed, return
                if ((what_failed != 'unknown') and (what_failed != 'none')):
                    return transaction + '_' + what_failed + '_' + user_type

                # check if valid credit amount
                try:
                    amount_credit = float(test_lines[self.config[transaction]['credit']])
                except ValueError:
                    return transaction + '_' + "credit_not_digit" + '_' + user_type

                buyer_credit = self.userDB.get_credit(username_buyer)

                # if credit amount of buyer's over max of 999,999
                if ((buyer_credit + amount_credit) > 999999):
                    what_failed = "credit_buyer_max_999999"
                # if credit over max
                elif (amount_credit > 1000):
                    what_failed = "credit_over_max_1000"
                elif (amount_credit <= 0):
                    what_failed = "credit_0_or_less"
                
            # invalid input found, return what_failed
            if ((what_failed != 'unknown') and (what_failed != 'none')):
                return transaction + '_' + what_failed + '_' + user_type
                
        # no invalid input found in loop, success case
        what_failed = 'success'

        logout_check = self.get_config_value("logout", test_lines, transaction, logout_line)
        if (logout_check != "none"):
            return f"{transaction}_over_1_transaction_limit_{user_type}"

        return transaction + '_' + what_failed + '_' + user_type