from FileIO import FileIO
import re

class UserDB:
    def __init__(self, user_fp, config):
        self.user_fp = user_fp
        self.user_accounts = {}
        self.config = config

        self.load_user_accounts()
   
    def load_user_accounts(self):
        user_lines = FileIO.read_file(self.user_fp)

        # get index # from config file
        index_username = self.config['user']['username']
        index_type = self.config['user']['usertype']
        index_credit = self.config['user']['credit']
        index_password = self.config['user']['password']
        end_of_file = self.config['user']['end']

        for line in user_lines:
            # for groups that add END or EXIT etc to the end of the user_accounts_file
            if ((end_of_file != "none") and (end_of_file == line)):
                print("hi")
                break

            # remove \n and underscores (if any)
            line = line.replace("\n","")
            line = (re.sub(r'_+', ' ', line)).split()
            
            username = line[index_username]
            usertype = line[index_type]
            credit_string = line[index_credit]

            if (index_password == -1):
                password = "none"
            else:
                password = line[index_password]

            # cuts down leading zeroes for credit
            creditTemp = credit_string.replace(".00", "")
            credit = float(creditTemp)

            self.user_accounts[username] = [usertype, credit, password]

    def is_invalid_username(self, username):
        return username not in self.user_accounts
    
    def is_invalid_password(self, username, password):
        correct_password = self.user_accounts.get(username)[2]

        if correct_password != password:
            return True
        return False
    
    def get_password(self, username):
        return self.user_accounts.get(username)[2]

    def get_credit(self, username):
        # get credit amount for user
        return self.user_accounts.get(username)[1]

    def get_user_type(self, username):
        # get usertype for user
        return self.user_accounts.get(username)[0]