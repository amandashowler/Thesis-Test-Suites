from UserDB import UserDB
from ItemDB import ItemDB

import re

class TestParser:
    def __init__(self, UserDB, ItemDB, config):
        self.userDB = UserDB
        self.itemDB = ItemDB
        self.config = config
        self.curr_line = 0
        self.prev_param = ""

        # store current user info
        self.curr_username = "none"
        self.curr_credit = 0
        self.curr_user_type = "none"

        # get line for certain logout cases
        self.logout_just_login = config['logout']['just_login']
        self.logout_other_transaction = config['logout']['invalid_type']
        # no self.logout_name for 2023 data

    def start_parse_get_user_and_logout(self, test_lines):
        # set where transaction is dependant on if there is a password
        self.set_curr_line()
        self.prev_param = ""

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

    def get_inputs_to_check(self):
        # get the config file info for the transaction
        info = self.config[self.transaction]

        # sort the config file by the value
        sorted_key = sorted(info, key=info.get)

        # re-write inputs_to_check in the right order
        self.inputs_to_check = {key: self.inputs_to_check[key] for key in sorted_key}
    
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
        if (len(test_lines) <= self.curr_line):
            return "none"
        else:
            return test_lines[line]
        
    def validate_input(self, transaction, test_lines, param_name, validation_function, logout_line, user_type=None):
        # get config value
        param_value = self.get_config_value(transaction, test_lines, param_name, logout_line)
        
        # remove anything after _ in transaction
        transaction = transaction.split("_")[0]
        
        # if config value is none, input has premature logout
        if (param_value == "none"):
            validation_result = "premature_logout"

            # if first param to be checked, output current param, else, output past param
            if (self.prev_param == ""):
                return [transaction, validation_result, param_name, "logout", user_type, logout_line]
            else:
                return [transaction, validation_result, self.prev_param, "logout", user_type, logout_line]
            
        elif (param_value == "not-applicable"): # if no password case
            return "success"
        
        # save prev param
        self.prev_param = param_name

        # check if already in transaction list
        if_transaction = self.check_transaction_list(transaction, param_value)
        if (if_transaction != "success"):
            return [transaction, if_transaction, param_name, param_value, user_type, logout_line]

        validation_result = validation_function(param_value)

        if (validation_result != "success"):
            # remove anything after _ in transaction
            transaction = transaction.split("_")[0]

            # return category
            return [transaction, validation_result, param_name, param_value, user_type, logout_line]

        return "success"
        
    def check_transaction_list(self, transaction, input):
        transaction_list = ["addcredit", "advertise", "bid", "create", "delete", "refund"]

        if input in transaction_list:
            return f"new_transaction_before_other_completed"
        else:
            return "success"
    
    def helper_invalid_user_type(self, test_lines, user_type, logout_line):
        # if user is not admin, fail to use create or delete, must logout
        if (user_type != "aa"):
            if (len(test_lines) <= self.logout_other_transaction) or (logout_line == self.logout_other_transaction):
                return "invalid_user_type"
            return "ERROR_non_AA_did_not_fail"
        
        # if it is an admin, test the other lines
        return "success"
    
    def bucket_category_message(self, transaction, error_type, logout_line, user_type=None):
        return [transaction, error_type, None, None, user_type, logout_line]
    
    def parse_login(self, test_lines):
        transaction = "login"
        what_failed = "none"
        user_type = None
        param = None
        value = None
        
        self.set_curr_line()

        # if file empty
        if not test_lines:
            return self.bucket_category_message(transaction, "file_empty", None)
        
        login_check, param, value = self.categorize_login(test_lines)

        if (login_check == "none"):
            return login_check
        else:
            return [transaction, login_check, param, value, user_type, None]
        
    def get_user_type_for_username(self, username):
        try:
            return self.userDB.get_user_type(username)
        except (IndexError, TypeError) as e:
            return None

    def categorize_login(self, test_lines):
        logout_names = ["exit", "logout"]

        if (test_lines[0] != 'login'):
                return "not_first", None, test_lines[0]

        try:
            user_type = self.get_user_type_for_username(test_lines[1])

            if (len(test_lines) < 2) or (self.userDB.is_invalid_username(test_lines[1])):
                return "wrong_username", "username", test_lines[1]
            
            elif ((self.userDB.get_password(test_lines[1]) != 'none') and ((len(test_lines) <= 3) or (self.userDB.is_invalid_password(test_lines[1], test_lines[2])))):
                return "wrong_password", "password", test_lines[2]
            
            # changed to self.logout_name so it will work with exit and logout
            elif (test_lines[self.logout_just_login] in logout_names):
                return "success", None, None
            
            elif (test_lines[self.logout_just_login] == 'login'):
                return "2nd_login", None, test_lines[self.logout_just_login]
            
        except IndexError:
            return "only_login", None, None
        
        return "none", None, None