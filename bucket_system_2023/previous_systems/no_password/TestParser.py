from UserDB import UserDB
from ItemDB import ItemDB

class TestParser:
    def __init__(self, UserDB, ItemDB, config):
        self.userDB = UserDB
        self.itemDB = ItemDB
        self.config = config
        self.curr_line = 0

        self.logout_just_login = config['password']['logout_just_login']
        self.logout_other_transaction = config['password']['logout_other_transaction']

    def get_config_value(self, transaction, test_lines, line_type, logout_line):
        self.curr_line += 1

        # if user logged out prematurly, no config value
        if (self.curr_line == logout_line):
            return 'none'
        else:
            return test_lines[self.config[transaction][line_type]]

    def parse_addcredit(self, test_lines, transaction_txt):
        transaction = 'addcredit'
        what_failed = 'unknown'

        if (self.config['user']['password'] == -1):
            self.curr_line = 2
        else:
            self.curr_line = 3

        try:
            logout_line = test_lines.index("logout")
        except ValueError:
            return "ERROR_did_not_logout_" + transaction

        # ASSUMPTION: credit on line 5, username on line 6
        # AREA FOR IMPROVEMENT: what if username on line 5, credit on line 6
        # fix this

        curr_username = test_lines[1]
        credit_user = self.userDB.get_credit(curr_username)
        user_type = self.userDB.get_user_type(curr_username)
        
        if (user_type != 'AA'):
            line_type = 'credit'
        else:
            line_type = 'credit_admin'

        credit = self.get_config_value(transaction, test_lines, line_type, logout_line)
        if (credit == 'none'):
            return "ERROR_premature_logout_" + transaction
        
        try:
            credit = float(credit)
        except ValueError:
            return transaction + '_' + "credit_not_digit" + '_' + user_type
        
        if ((credit + credit_user) > 999999):
            what_failed = 'credit_too_high'
        elif (credit > 1000):
            what_failed = 'over_1000'
        elif (credit <= 0):
            what_failed = '0'
        elif (0 < credit <= 1000):
            what_failed = 'success'
        
        if (user_type != 'AA'):
            return transaction + '_' + what_failed + '_' + user_type
        else:
            # find first username in txt
            for j in range(4, len(test_lines)):
                if not test_lines[j].isdigit():
                    # get username to addcredit to
                    admin_username_to_add = test_lines[j]
                    break

            if (self.userDB.is_invalid_username(admin_username_to_add)):
                what_failed = 'user_not_found'
            elif (admin_username_to_add != curr_username):
                what_failed = 'success_diff_user'
            
            return transaction + '_' + what_failed + '_' + user_type
        
    def parse_advertise(self, test_lines, transaction_txt):
        transaction = 'advertise'
        what_failed = 'unknown'
        if (self.config['user']['password'] == -1):
            self.curr_line = 2
        else:
            self.curr_line = 3

        try:
            logout_line = test_lines.index("logout")
        except ValueError:
            return "ERROR_did_not_logout_" + transaction

        curr_username = test_lines[1]
        user_type = self.userDB.get_user_type(curr_username)

        # if buy-standard, cannot advertise so must logout
        if (user_type == 'BS'):
            if (test_lines[self.logout_other_transaction] == 'logout'):
                what_failed = 'invalid_usertype'
            else:
                what_failed = 'ERROR_BS_did_not_fail'

        else:
            line_type = 'item_name'
            item_name = self.get_config_value(transaction, test_lines, line_type, logout_line)
            if (item_name == 'none'):
                return "ERROR_premature_logout_" + transaction

            # check if item name too long
            if (len(item_name) > 25):
                what_failed = "item_name_over_25_chars"
            # check if item name already exists
            elif (not (self.itemDB.is_invalid_item_name(item_name))):
                what_failed = "item_name_already_exists"
            else:
                line_type = 'initial_bid'
                initial_bid = self.get_config_value(transaction, test_lines, line_type, logout_line)
                if (initial_bid == 'none'):
                    return "ERROR_premature_logout_" + transaction

                try:
                    if (float(initial_bid) >= 1000.0):
                        what_failed = "over_max_price"
                    else:
                        line_type = 'auction_length'
                        auction_length = self.get_config_value(transaction, test_lines, line_type, logout_line)
                        if (auction_length == 'none'):
                            return "ERROR_premature_logout_" + transaction
                        
                        try:
                            auction_length = int(auction_length)
                        except ValueError:
                            return transaction + '_' + "auction_length_not_digit" + '_' + user_type

                        if (int(auction_length) > 100):
                            what_failed = "over_max_auction_length"
                        else:
                            what_failed = "success"
                except ValueError:
                        what_failed = "initial_bid_not_digit"
                

        return transaction + '_' + what_failed + '_' + user_type
    
    def parse_allitems(self, test_lines, transaction_txt):
        transaction = 'allitems'
        what_failed = 'success' # is there a way to fail?

        try:
            logout_line = test_lines.index("logout")
        except ValueError:
            return "ERROR_did_not_logout_" + transaction
        
        user_type = self.userDB.get_user_type(test_lines[1])

        return transaction + '_' + what_failed + '_' + user_type
    
    def parse_allusers(self, test_lines, transaction_txt):
        transaction = 'allusers'
        what_failed = 'success' # is there a way to fail?

        # check if the user logs out
        try:
            logout_line = test_lines.index("logout")
        except ValueError:
            what_failed = "ERROR_did_not_logout"
            return what_failed + '_' + transaction
        
        user_type = self.userDB.get_user_type(test_lines[1])

        return transaction + '_' + what_failed + '_' + user_type
    
    def parse_bid(self, test_lines, transaction_txt):
        transaction = 'bid'
        what_failed = ''
        if (self.config['user']['password'] == -1):
            self.curr_line = 2
        else:
            self.curr_line = 3

        try:
            logout_line = test_lines.index("logout")
        except ValueError:
            return "ERROR_did_not_logout_" + transaction

        curr_username = test_lines[1]
        user_type = self.userDB.get_user_type(curr_username)

        # if sell-standard, cannot bid so must logout
        if (user_type == 'SS'):
            if (test_lines[self.logout_other_transaction] == 'logout'):
                what_failed = 'invalid_usertype'
            else:
                what_failed = 'ERROR_SS_did_not_fail'

        else:
            line_type = 'item_name'
            item_name = self.get_config_value(transaction, test_lines, line_type, logout_line)
            if (item_name == 'none'):
                return "ERROR_premature_logout_" + transaction

            # check if item name is invalid
            if (self.itemDB.is_invalid_item_name(item_name)):
                what_failed = 'invalid_item_name'
            else:
                line_type = 'seller'
                seller = self.get_config_value(transaction, test_lines, line_type, logout_line)
                if (seller == 'none'):
                    return "ERROR_premature_logout_" + transaction

                if (self.itemDB.get_seller(item_name) != seller):
                    what_failed += 'incorrect_seller'
                elif (curr_username == seller):
                    what_failed += 'user_is_seller'
                else:
                    line_type = 'bid'
                    bid = self.get_config_value(transaction, test_lines, line_type, logout_line)
                    if (bid == 'none'):
                        return "ERROR_premature_logout_" + transaction
                    
                    curr_bid = self.itemDB.get_bid(item_name)

                    try:
                        bid = float(bid)
                    except ValueError:
                        return transaction + '_' + "credit_not_digit" + '_' + user_type
                    
                    if (bid < (curr_bid * 1.05)):
                        what_failed = 'less_than_curr_bid_5_percent'
                    else:
                        what_failed = 'success'

        return transaction + '_' + what_failed + '_' + user_type
    
    def parse_create(self, test_lines, transaction_txt):
        transaction = 'create'
        what_failed = 'unknown'
        
        try:
            logout_line = test_lines.index("logout")
        except ValueError:
            return "ERROR_did_not_logout_" + transaction

        curr_username = test_lines[1]
        user_type = self.userDB.get_user_type(curr_username)

        # ASSUMPTION: user type is defined as FS, SS, BS, AA
        # AREA FOR IMPROVEMENT: what user type is a number?

        # if user is not admin, fail to use create, must logout
        if (user_type != 'AA'):
            if (logout_line == 4):
                what_failed = 'not_admin'
                
            else:
                what_failed = 'ERROR_not_AA_did_not_fail'
        # if user is admin, test create
        else:
            username_to_create = test_lines[4]
            type_to_create = test_lines[5]

            if (len(username_to_create) > 15):
                what_failed = 'username_long'
            elif (len(username_to_create) < 1):
                what_failed = 'username_short'
            elif (not self.userDB.is_invalid_username(username_to_create)): # if username already exists
                what_failed = 'username_already_exists'

            # ASSUMPTION: assume user_type is AA, FS, SS
            # AREA FOR IMPROVEMENT: what if they use numbers?
            
            # ASSUMPTION: assume new username is on line 4 and type is on line 5
            # AREA FOR IMPROVEMENT: what if the inputs are swapped?
            elif (logout_line >= 6):
                if (type_to_create != 'AA' and type_to_create != 'FS'and type_to_create != 'SS'and type_to_create != 'BS'):
                    what_failed = 'user_type_not_valid'
                else:
                    what_failed = 'success'
            
        return transaction + '_' + what_failed + '_' + user_type
    
    def parse_delete(self, test_lines, transaction_txt):
        transaction = 'delete'
        what_failed = 'unknown'

        try:
            logout_line = test_lines.index("logout")
        except ValueError:
            return "ERROR_did_not_logout_" + transaction

        curr_username = test_lines[1]
        user_type = self.userDB.get_user_type(curr_username)

        if (user_type != 'AA'):
            if (test_lines[4] == 'logout'):
                what_failed = 'not_admin'
                
            else:
                what_failed = 'ERROR_not_AA_did_not_fail'
        else:
            username_to_delete = test_lines[4]

            if (self.userDB.is_invalid_username(username_to_delete)): # username does not exist
                what_failed = 'username_not_exist'
            elif (username_to_delete == curr_username): # deleting current user
                what_failed = 'current_account_logged_in'
            else:
                what_failed = 'success'

        return transaction + '_' + what_failed + '_' + user_type

    def parse_login(self, test_lines):
        transaction = 'login'
        what_failed = 'none'

        if (len(test_lines) < 1) or (test_lines[0] != 'login'):
            what_failed = 'not_first'

        elif (len(test_lines) < 2) or (self.userDB.is_invalid_username(test_lines[1])):
            what_failed = 'username'
        
        elif ((self.userDB.get_password(test_lines[1]) != 'none') and ((len(test_lines) < 3) or (self.userDB.is_invalid_password(test_lines[1], test_lines[2])))):
            what_failed = 'password'
        
        elif (test_lines[self.logout_just_login] == 'logout'):
            user_type = self.userDB.get_user_type(test_lines[1])

            return 'login_success_' + user_type
        
        elif (test_lines[self.logout_just_login] == 'login'):
            user_type = self.userDB.get_user_type(test_lines[1])

            what_failed = '2nd_login_' + user_type
        
        else:
            # test for another transaction - still = none
            return what_failed
        
        return 'login_' + what_failed + '_fail'
    
    def helper_refund(self, transaction, test_lines, username, username_text, type_not_valid):
        if self.userDB.is_invalid_username(username):
            what_failed = username_text + "_not_exist"
            return what_failed
        
        elif (self.userDB.get_user_type(username) == type_not_valid):
            what_failed = username_text + "_" + type_not_valid + "_not_valid"
            return what_failed + '_' + type_not_valid
        
        else:
            return 'none'
    
    def parse_refund(self, test_lines, transaction_txt):
        transaction = 'refund'
        what_failed = 'unknown'

        try:
            logout_line = test_lines.index("logout")
        except ValueError:
            return "ERROR_did_not_logout_" + transaction

        curr_username = test_lines[1]
        user_type = self.userDB.get_user_type(curr_username)

        if (user_type != 'AA'):
            if (test_lines[4] == 'logout'):
                what_failed = 'not_admin'
                
            else:
                what_failed = 'ERROR_not_AA_did_not_fail'

        else:
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

                    what_failed = self.helper_refund(transaction, test_lines, username_seller, key, "BS")

                elif (key == "buyer" or key == "credit"):
                    # check if a valid buyer first
                    username_buyer = test_lines[row_buyer]

                    what_failed = self.helper_refund(transaction, test_lines, username_buyer, "buyer", "SS")

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
                    
                # invalid input found, return what_failed
                if ((what_failed != 'unknown') and (what_failed != 'none')):
                    return transaction + '_' + what_failed + '_' + user_type
                    
            # no invalid input found in loop, success case
            what_failed = 'success'

        return transaction + '_' + what_failed + '_' + user_type