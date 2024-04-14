from TestParser import TestParser

class AddCreditParser(TestParser):
    def __init__(self, UserDB, ItemDB, config, transaction):
        super().__init__(UserDB, ItemDB, config)
        self.transaction = transaction

        self.inputs_to_check_other = {
            "credit": self.validate_credit
        }

        self.inputs_to_check = {
            "username_admin": self.validate_username,
            "credit_admin": self.validate_credit
        }

    def parse(self, test_lines):
        transaction_logout = "addcredit"

        # start parse with finding where input logs out and getting user information
        logout_line, self.curr_username, self.curr_credit, self.curr_user_type = self.start_parse_get_user_and_logout(test_lines)
        #if logout_line == -1:
        #    return [self.transaction, "ERROR_did_not_logout", None, None, self.curr_user_type, logout_line]
        
        # set which inputs to loop through based on if admin
        if (self.curr_user_type == "aa"):
            self.transaction = "addcredit_aa" # change transaction since 2 inputs
            self.get_inputs_to_check()        # order the inputs correctly
            inputs_to_check = self.inputs_to_check
        else:
            self.transaction = "addcredit"
            inputs_to_check = self.inputs_to_check_other

        for key, value in inputs_to_check.items():
            # check if input is valid
            result = self.validate_input(self.transaction, test_lines, key, value, logout_line, self.curr_user_type)
            if (result != "success"):
                return result
            
        logout_check = self.get_config_value("logout", test_lines, self.transaction, logout_line)
        if (logout_check != "none"):
            return self.bucket_category_message(self.transaction, "over_1_transaction_limit", logout_line, self.curr_user_type)
        
        # remove anything after _ in transaction
        transaction = self.transaction.split("_")[0]
        return self.bucket_category_message(transaction, "success", logout_line, self.curr_user_type)
    
    def validate_credit(self, credit):
        # try to get credit, if not a #, testing for string input
        try:
            credit = float(credit)
        except ValueError:
            return "credit_not_digit"

        if ((credit + self.curr_credit) > 999999):
            return "credit_too_high"
        elif (credit > 1000):
            return "over_1000"
        elif (credit <= 0):
            return "less_than_0_or_0"
        
        return "success"
    
    def validate_username(self, username_admin):
        if (self.userDB.is_invalid_username(username_admin)):
            return "user_not_found"
        
        # set credit_user to credit of username to add
        self.curr_credit = self.userDB.get_credit(username_admin)
        
        return "success"