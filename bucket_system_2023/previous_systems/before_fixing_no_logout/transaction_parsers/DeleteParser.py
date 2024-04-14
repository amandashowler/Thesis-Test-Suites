from TestParser import TestParser

class DeleteParser(TestParser):
    def __init__(self, UserDB, ItemDB, config, transaction):
        super().__init__(UserDB, ItemDB, config)

        self.transaction = transaction

    def parse(self, test_lines):
        # start parse with finding where input logs out and getting user information
        logout_line, self.curr_username, self.curr_credit, self.curr_user_type = self.start_parse_get_user_and_logout(test_lines)
        if logout_line == -1:
            return f"ERROR_did_not_logout_{self.transaction}"

        # check if valid user_type, must be admin
        user_type_check = self.helper_invalid_user_type(test_lines, self.curr_user_type, logout_line)
        if (user_type_check != "success"):
            return self.bucket_category_message(self.transaction, user_type_check, self.curr_user_type)
        
        # check if username_to_delete is valid
        username_to_delete = self.get_config_value(self.transaction, test_lines, 'username_to_delete', logout_line)
        if (username_to_delete == 'none'):
            return "ERROR_premature_logout_" + self.transaction
        
        username_to_delete_check = self.helper_delete_validate_username_to_delete(username_to_delete, self.curr_username)
        if (username_to_delete_check != "success"):
            return self.bucket_category_message(self.transaction, username_to_delete_check, self.curr_user_type)
        
        logout_check = self.get_config_value("logout", test_lines, self.transaction, logout_line)
        if (logout_check != "none"):
            return self.bucket_category_message(self.transaction, "over_1_transaction_limit", self.curr_user_type)

        return self.bucket_category_message(self.transaction, "success", self.curr_user_type)
    
    def helper_delete_validate_username_to_delete(self, username_to_delete, curr_username):
        if (self.userDB.is_invalid_username(username_to_delete)): # username does not exist
            return "username_not_exist"
        elif (username_to_delete == curr_username): # deleting current user
            return "current_account_logged_in"
        
        return "success"