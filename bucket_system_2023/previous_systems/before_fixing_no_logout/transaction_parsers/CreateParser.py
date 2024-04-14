from TestParser import TestParser

class CreateParser(TestParser):
    def __init__(self, UserDB, ItemDB, config, transaction):
        super().__init__(UserDB, ItemDB, config)
        self.transaction = transaction

        self.inputs_to_check = {
            "username_to_create": self.validate_username_to_create,
            "type_to_create": self.validate_type_to_create,
            "password_to_create": self.validate_password_to_create
        }

        self.get_inputs_to_check()

    def parse(self, test_lines):

        # start parse with finding where input logs out and getting user information
        logout_line, self.curr_username, self.curr_credit, self.curr_user_type = self.start_parse_get_user_and_logout(test_lines)
        if logout_line == -1:
            return f"ERROR_did_not_logout_{self.transaction}"

        # check if valid user_type, must be admin
        user_type_check = self.helper_invalid_user_type(test_lines, self.curr_user_type, logout_line)
        if (user_type_check != "success"):
            return f"{self.transaction}_{user_type_check}_{self.curr_user_type}"
        
        for key, value in self.inputs_to_check.items():
            # check if input is valid
            result = self.validate_input(self.transaction, test_lines, key, value, logout_line, self.curr_user_type)
            if (result != "success"):
                return result
            
        # check for another input line between (ex. adding credit)
        #print(f"Amount added: {test_lines[6]}")
        #sorted_rows = sorted(self.config[self.transaction].values())
        #for i in range(len(sorted_rows) - 1):
        #    if sorted_rows[i+1] - sorted_rows[i] > 1:
        #        print("we got a problem")
        
        logout_check = self.get_config_value("logout", test_lines, self.transaction, logout_line)
        if (logout_check != "none"):
            return self.bucket_category_message(self.transaction, "over_1_transaction_limit", self.curr_user_type)
            
        return self.bucket_category_message(self.transaction, "success", self.curr_user_type)

    def validate_username_to_create(self, username_to_create):
        if (len(username_to_create) > 15):
            return "username_long"
        elif (len(username_to_create) < 1):
            return "username_short"
        elif (not self.userDB.is_invalid_username(username_to_create)): # if username already exists
            return "username_already_exists"
        
        return "success"
    
    def validate_type_to_create(self, type_to_create):
        if (type_to_create != 'aa' and type_to_create != 'fs'and type_to_create != 'ss'and type_to_create != 'bs'):
            return "user_type_not_valid"
        return "success"
    
    def validate_password_to_create(self, password_to_create):
        if (len(password_to_create) > 15):
            return "password_long"
        elif (len(password_to_create) < 1):
            return "password_short"
        
        return "success"