from UserDB import UserDB
from ItemDB import ItemDB

import re

class TestParser:
    def __init__(self, UserDB, ItemDB, config):
        self.userDB = UserDB
        self.itemDB = ItemDB
        self.config = config
        self.curr_line = 0

        # store current user info
        self.curr_username = "none"
        self.curr_credit = 0
        self.curr_user_type = "none"

        # get line for certain logout cases
        self.logout_just_login = config['logout']['just_login']
        self.logout_other_transaction = config['logout']['invalid_type']

    def start_parse_get_user_and_logout(self, test_lines):
        # set where transaction is dependant on if there is a password
        self.set_curr_line()

        # try to get logout line, if no logout, return -1
        try:
            logout_line = test_lines.index("logout")
        except ValueError:
            logout_line = -1

        # get user info
        curr_username = test_lines[1]
        credit_user = self.userDB.get_credit(curr_username)
        user_type = self.userDB.get_user_type(curr_username)

        return logout_line, curr_username, credit_user, user_type

    def set_curr_line(self):
        # set where transaction is dependant on if it has a password
        if (self.config['user']['password'] == -1):
            self.curr_line = 2
        else:
            self.curr_line = 3

    def get_config_value(self, transaction, test_lines, line_type, logout_line):
        # if line is -1, it not applicable to test suite
        line = self.config[transaction][line_type]
        if (line == -1):
            return "not-applicable"
        
        # if applicable input, increment current line
        self.curr_line += 1

        # if user logged out prematurly, no config value
        if (self.curr_line == logout_line):
            return "none"
        else:
            return test_lines[line]
    
    def helper_invalid_user_type(self, test_lines, user_type, logout_line):
        # if user is not admin, fail to use create or delete, must logout
        if (user_type != "aa"):
            if (logout_line == self.logout_other_transaction):
                return "not_admin"
            return "ERROR_not_AA_did_not_fail"
        
        # if it is an admin, test the other lines
        return "success"
    
    def validate_input(self, transaction, test_lines, param_name, validation_function, logout_line, user_type=None):
        param_value = self.get_config_value(transaction, test_lines, param_name, logout_line)
        if (param_value == "none"):
            return f"ERROR_premature_logout_{transaction}"
        elif (param_value == "not-applicable"): # if no password case
            return "success"

        validation_result = validation_function(param_value)
        #print(validation_result)
        if (validation_result != "success"):
            # find user_type suffix needs to be added
            user_type_suffix = f"_{user_type.upper()}" if user_type else ""

            # remove anything after _ in transaction
            transaction = transaction.split("_")[0]
            return f"{transaction}_{validation_result}{user_type_suffix}"

        return "success"
    
    def get_inputs_to_check(self):
        # get the config file info for the transaction
        info = self.config[self.transaction]

        # sort the config file by the value
        sorted_key = sorted(info, key=info.get)

        # re-write inputs_to_check in the right order
        self.inputs_to_check = {key: self.inputs_to_check[key] for key in sorted_key}
    
    def bucket_category_message(self, transaction, error_type, user_type=None):
        user_type_suffix = f"_{user_type.upper()}" if user_type else ""
        return f"{transaction}_{error_type}{user_type_suffix}"
    
    def bucket_category_message(self, transaction, error_type, user_type=None):
        user_type_suffix = f"_{user_type.upper()}" if user_type else ""
        return f"{transaction}_{error_type}{user_type_suffix}"
    
    def parse_login(self, test_lines):
        transaction = 'login'
        what_failed = 'none'

        self.set_curr_line()

        if (len(test_lines) == 0):
            what_failed = "file_empty"
        
        #elif ((len(test_lines) <= 1) or (test_lines[0] != 'login')):
        elif (test_lines[0] != 'login'):
            what_failed = "not_first_fail"

        elif (len(test_lines) < 2) or (self.userDB.is_invalid_username(test_lines[1])):
            what_failed = "username_fail"
        
        elif ((self.userDB.get_password(test_lines[1]) != 'none') and ((len(test_lines) <= 3) or (self.userDB.is_invalid_password(test_lines[1], test_lines[2])))):
            what_failed = "password_fail"
        
        elif (test_lines[self.logout_just_login] == 'logout'):
            user_type = self.userDB.get_user_type(test_lines[1])

            what_failed = 'success_' + user_type.upper()
        
        elif (test_lines[self.logout_just_login] == 'login'):
            user_type = self.userDB.get_user_type(test_lines[1])

            what_failed = '2nd_login_' + user_type.upper() + '_fail'
        
        else:
            # test for another transaction - still = none
            return what_failed
        
        return 'login_' + what_failed