from TestParser import TestParser

class RefundParser(TestParser):
    def __init__(self, UserDB, ItemDB, config, transaction):
        super().__init__(UserDB, ItemDB, config)

        self.transaction = transaction

    def parse(self, test_lines):
        # start parse with finding where input logs out and getting user information
        logout_line, self.curr_username, self.curr_credit, self.curr_user_type = self.start_parse_get_user_and_logout(test_lines)
        #if logout_line == -1:
        #    return [self.transaction, "ERROR_did_not_logout", None, None, self.curr_user_type, logout_line]

        # check if valid user_type, must be admin
        user_type_check = self.helper_invalid_user_type(test_lines, self.curr_user_type, logout_line)
        if (user_type_check != "success"):
            return [self.transaction, user_type_check, None, None, self.curr_user_type, logout_line]

        # check buyer, seller and credit in order in case you run into a logout
        category = self.helper_refund_buyer_seller_order(self.transaction, test_lines, logout_line, self.curr_user_type)
        if (category != "success"):
            return category

        logout_check = self.get_config_value("logout", test_lines, self.transaction, logout_line)
        if (logout_check != "none"):
            return self.bucket_category_message(self.transaction, "over_1_transaction_limit", logout_line, self.curr_user_type)

        return self.bucket_category_message(self.transaction, "success", logout_line, self.curr_user_type)
    
    def helper_refund_buyer_seller_order(self, transaction, test_lines, logout_line, user_type):
        order = ["buyer", "seller", "credit"] if self.config[transaction]['buyer'] < self.config[transaction]['seller'] else ["seller", "buyer", "credit"]

        for role in order:
            if (role == "buyer"):
                category, username_buyer = self.helper_refund_categorize_user(transaction, test_lines, logout_line, user_type, "buyer", "ss")
            elif (role == "seller"):
                category, username_seller = self.helper_refund_categorize_user(transaction, test_lines, logout_line, user_type, "seller", "bs")
            else:
                category = self.helper_refund_categorize_credit(transaction, test_lines, logout_line, user_type, username_buyer)

            if category != "success":
                return category
        return "success"
    
    def helper_refund_categorize_user(self, transaction, test_lines, logout_line, user_type, new_user, new_type):
        # check if username_buyer is valid
        username = self.get_config_value(transaction, test_lines, new_user, logout_line)
        if (username == 'none'):
            return [transaction, "premature_logout", new_user, "logout", user_type, logout_line], username
        
        username_check = self.helper_refund_validate_username(username, new_user, new_type)
        if (username_check != "success"):
            return [transaction, username_check, new_user, username, user_type, logout_line], username
                
        return "success", username
        
    def helper_refund_categorize_credit(self, transaction, test_lines, logout_line, user_type, username_buyer):
        # check if credit is valid
        credit = self.get_config_value(transaction, test_lines, "credit", logout_line)
        if (credit == 'none'):
            return [transaction, "premature_logout", credit, "logout", user_type, logout_line]
        
        credit_check = self.helper_refund_validate_credit(credit, username_buyer)
        if (credit_check != "success"):
            return [transaction, credit_check, "credit", credit, user_type, logout_line]
        
        return "success"

    def helper_refund_validate_username(self, username, username_text, type_not_valid):

        if self.userDB.is_invalid_username(username):
            return f"{username_text}_not_exist"
        
        elif (self.userDB.get_user_type(username) == type_not_valid):
            return f"{username_text}_{type_not_valid}_not_valid"
        
        return "success"
    
    def helper_refund_validate_credit(self, credit, username_buyer):
        # check if valid credit amount
        try:
            amount_credit = float(credit)
        except ValueError:
            return "credit_not_digit"

        buyer_credit = self.userDB.get_credit(username_buyer)

        # if credit amount of buyer's over max of 999,999
        if ((buyer_credit + amount_credit) > 999999):
            return "credit_buyer_max_999999"
        # if credit over max
        elif (amount_credit > 1000):
            return "credit_over_max_1000"
        elif (amount_credit <= 0):
            return "credit_0_or_less"

        return "success"