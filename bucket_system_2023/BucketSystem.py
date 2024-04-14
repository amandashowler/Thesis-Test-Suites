import os
import pandas as pd

from transaction_parsers.AddCreditParser import AddCreditParser
from transaction_parsers.AdvertiseParser import AdvertiseParser
from transaction_parsers.BidParser import BidParser
from transaction_parsers.CreateParser import CreateParser
from transaction_parsers.DeleteParser import DeleteParser
from transaction_parsers.ListParser import ListParser
from transaction_parsers.RefundParser import RefundParser
from TestParser import TestParser
from UserDB import UserDB
from ItemDB import ItemDB
from CategoryOutput import CategoryOutput

class BucketSystem:
    def __init__(self, course_project_title, test_input_file_endswith, test_folder_fp, user_fp, item_fp, config): # fp = file path
        self.endswith = test_input_file_endswith
        self.course_project_title = course_project_title
        self.test_fp = test_folder_fp
        self.filename_list = []
        self.bucket_category_list = []
        self.transaction_line = config['password']['transaction_line']
        self.transaction_list = ["addcredit", "advertise", "bid", "create", "delete", "refund"]

        self.parser_finder = {
            "addcredit": AddCreditParser(UserDB(user_fp, config), ItemDB(item_fp, config), config, "addcredit"),
            "advertise": AdvertiseParser(UserDB(user_fp, config), ItemDB(item_fp, config), config, "advertise"),
            "bid": BidParser(UserDB(user_fp, config), ItemDB(item_fp, config), config, "bid"),
            "create": CreateParser(UserDB(user_fp, config), ItemDB(item_fp, config), config, "create"),
            "delete": DeleteParser(UserDB(user_fp, config), ItemDB(item_fp, config), config, "delete"),
            "list": ListParser(UserDB(user_fp, config), ItemDB(item_fp, config), config),
            "refund": RefundParser(UserDB(user_fp, config), ItemDB(item_fp, config), config, "refund"),
        }
        self.parser = TestParser(UserDB(user_fp, config), ItemDB(item_fp, config), config)
        self.CategoryOutput = CategoryOutput(self.transaction_list, self.course_project_title)

        self.print_titles = ['Filename', 'Bucket']

    def process_all_txts(self):
        # loop through the txt files (tests)
        for filename in os.listdir(self.test_fp):

            # only process files for the transaction to test
            if filename.endswith(self.endswith): # and filename.startswith(self.transaction_to_test):

                # concatenate the file path
                file_path = os.path.join(self.test_fp, filename)

                self.process_txt(file_path, filename)

        # output to excel and compare previous run
        self.CategoryOutput.create_dataframe(self.course_project_title)
        self.CategoryOutput.compare_excel_before_after(self.course_project_title)

    def process_txt(self, file_path, filename):

        # open file read only
        with open(file_path, 'r') as file:

            bucket_category = 'unknown'
            file_lines = []

            # add lines with lowercase and no spaces
            for line in file:
                line_no_spaces = line.lower().replace(" ", "")
                line_no_underscores = line_no_spaces.lower().replace("_", "")
                file_lines.append(line_no_underscores.strip())

            # print file info
            #print("-------------------------------------------")
            #print(filename)
            #print(file_lines)

            # check if valid login
            bucket_login = self.parser.parse_login(file_lines)

            # if user logged in, choose parser based on transaction
            if (bucket_login == "none"):
                transaction = file_lines[self.transaction_line].lower()
                
                if (transaction in self.transaction_list):
                    bucket_category = self.parser_finder[transaction].parse(file_lines)
                elif (transaction in ["allitems", "listitems", "listallitems", "list", "viewitems", "viewauctions"]):
                    bucket_category = self.parser_finder["list"].parse_allitems(file_lines)
                elif (transaction in ["allusers", "listusers", "listallusers", "user", "listallaccounts", "viewaccounts", "viewusers"]):
                    bucket_category = self.parser_finder["list"].parse_allusers(file_lines)
                else:
                    bucket_category = [transaction, "ERROR_no_transaction_matched", None, None, None, None]
            else:
                bucket_category = bucket_login

            # add bucket info to dataframe
            #print(f"Bucket: {bucket_category}")

            bucket_length = len(bucket_category)
            if (bucket_length == 6):
                transaction, validation_result, failed_param_name, failed_param_value, user_type, logout_line = bucket_category
            else: 
                print(f"Error: {bucket_length}/6 of items returned for bucket category\nBucket: {bucket_category}")

            self.CategoryOutput.transaction_finder(filename, transaction, validation_result, failed_param_name, failed_param_value, logout_line, user_type)