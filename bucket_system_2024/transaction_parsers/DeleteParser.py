from TestParser import TestParser
import re

class DeleteParser(TestParser):
    def __init__(self, UserDB, AvailableGameDB, GameCollectionDB, config, transaction):
        super().__init__(UserDB, AvailableGameDB, GameCollectionDB, config)

        self.transaction = transaction

        self.inputs_to_check = {
            "username_to_delete": self.validate_username_to_delete
        }

        self.get_inputs_to_check()

    def parse(self, test_lines):
        # start parse with finding where input logs out and getting user information
        logout_line, self.curr_username, self.curr_credit, self.curr_user_type = self.start_parse_get_user_and_logout(test_lines)
        #if logout_line == -1:
        #    return [self.transaction, "ERROR_did_not_logout", None, None, self.curr_user_type]

        # check if valid user_type, must be admin
        user_type_check = self.helper_invalid_user_type(test_lines, self.curr_user_type, logout_line)
        if (user_type_check != "success"):
            return [self.transaction, user_type_check, None, None, self.curr_user_type, logout_line]
        
        # check if username_to_delete is valid
        for key, value in self.inputs_to_check.items():
            # check if input is valid
            result = self.validate_input(self.transaction, test_lines, key, value, logout_line, self.curr_user_type)
            if (result != "success"):
                return result
        
        logout_check = self.get_config_value("logout", test_lines, self.transaction, logout_line)
        if (logout_check != "none"):
            return self.bucket_category_message(self.transaction, "over_1_transaction_limit", logout_line, self.curr_user_type)

        return self.bucket_category_message(self.transaction, "success", logout_line, self.curr_user_type)
    
    def validate_username_to_delete(self, username_to_delete):
        if re.search(r'[^a-zA-Z0-9]', username_to_delete):
            return "username_special_character"
        elif (self.userDB.is_invalid_username(username_to_delete)): # username does not exist
            return "username_not_exist"
        elif (username_to_delete == self.curr_username): # deleting current user
            return "current_account_logged_in"
        
        return "success"