from TestParser import TestParser

class ListParser(TestParser):
    def __init__(self, UserDB, ItemDB, config):
        super().__init__(UserDB, ItemDB, config)

    def parse_allitems(self, test_lines):
        transaction = "allitems"

        # start parse with finding where input logs out and getting user information
        logout_line, self.curr_username, self.curr_credit, self.curr_user_type = self.start_parse_get_user_and_logout(test_lines)
        #if logout_line == -1:
        #    return [transaction, "ERROR_did_not_logout", None, None, self.curr_user_type, logout_line]

        return self.bucket_category_message(transaction, "success", logout_line, self.curr_user_type)
    
    def parse_allusers(self, test_lines):
        transaction = "allusers"

        # start parse with finding where input logs out and getting user information
        logout_line, curr_username, credit_user, user_type = self.start_parse_get_user_and_logout(test_lines)
        #if logout_line == -1:
        #    return [transaction, "ERROR_did_not_logout", None, None, self.curr_user_type, logout_line]

        return self.bucket_category_message(transaction, "success", logout_line, user_type)