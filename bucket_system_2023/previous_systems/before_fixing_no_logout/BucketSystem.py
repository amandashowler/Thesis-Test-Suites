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

class BucketSystem:
    def __init__(self, course_project_title, test_input_file_endswith, test_folder_fp, user_fp, item_fp, config): # fp = file path
        self.endswith = test_input_file_endswith
        self.course_project_title = course_project_title
        self.test_fp = test_folder_fp
        self.filename_list = []
        self.bucket_category_list = []
        self.transaction_line = config['password']['transaction_line']

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

        # for printing only
        self.how_wide = 90
        self.how_wide_bucket = (self.how_wide - 6) // 2
        self.print_titles = ['Filename', 'Bucket']

    def process_all_txts(self):
        #print("-"*self.how_wide)
        #print(f'|  {self.print_titles[0].ljust(self.how_wide_bucket + 1)}| {self.print_titles[1].ljust(self.how_wide_bucket)}|')

        # loop through the txt files (tests)
        for filename in os.listdir(self.test_fp):

            # only process files for the transaction to test
            if filename.endswith(self.endswith): # and filename.startswith(self.transaction_to_test):

                # concatenate the file path
                file_path = os.path.join(self.test_fp, filename)

                self.process_txt(file_path, filename)

        check = self.export_to_excel()
        self.compare_excel_before_after()

    def process_txt(self, file_path, filename):

        # open file read only
        with open(file_path, 'r') as file:
            #print("-"*self.how_wide)
            #print(filename)

            bucket_category = 'unknown'
            file_lines = []

            # add lines with lowercase and no spaces
            for line in file:
                line_no_spaces = line.lower().replace(" ", "")
                file_lines.append(line_no_spaces.strip())

            # check if valid login
            bucket_login = self.parser.parse_login(file_lines)

            if bucket_login == 'none':
                transaction = file_lines[self.transaction_line].lower()
                transaction_list = ["addcredit", "advertise", "bid", "create", "delete", "refund"]

                if (transaction in transaction_list):
                    bucket_category = self.parser_finder[transaction].parse(file_lines)
                elif (transaction in ["allitems", "listitems", "listallitems", "list", "viewitems", "viewauctions"]):
                    bucket_category = self.parser_finder["list"].parse_allitems(file_lines)
                elif (transaction in ["allusers", "listusers", "listallusers", "user", "listallaccounts", "viewaccounts", "viewusers"]):
                    bucket_category = self.parser_finder["list"].parse_allusers(file_lines)
                else:
                    bucket_category = 'ERROR_nothing_matched'
            
            else:
                bucket_category = bucket_login

            self.filename_list.append(filename)
            self.bucket_category_list.append(bucket_category)

            # PRINTING SPOT
            
            # normal print
            # print count: 6 + ljust(30) + ljust(29) = 65
            #print(f'|  {filename.ljust(self.how_wide_bucket + 1)[:self.how_wide_bucket]}| {bucket_category.ljust(self.how_wide_bucket)[:self.how_wide_bucket]}|')

            # filenames
            #print(filename)
            
            # bucket sorting
            #print(bucket_category)

            # debug print
            #print(f'Processing {filename}...')
            #print(f"Case for {filename}:\n{bucket_category}\n")

    def export_to_excel(self):
        # check that they have the same length
        if (len(self.filename_list) != len(self.bucket_category_list)):
            print("ERROR: Filename and cases must be the same length")
            return -1
        
        # create the dataframe
        df = pd.DataFrame({'Filename': self.filename_list, 'Case': self.bucket_category_list})

        # write to excel file with no index
        df.to_excel(f"excel_data/after_cases/{self.course_project_title}.xlsx", index=False)

        return 0
    
    def compare_excel_before_after(self):
        # save file path
        before_filepath = f"excel_data/before_cases/{self.course_project_title}-before.xlsx"
        after_filepath = f"excel_data/after_cases/{self.course_project_title}.xlsx"

        # read in after excel file
        df_after = pd.read_excel(after_filepath)

        # if no before file, first time running this frontend so make one
        if not os.path.exists(before_filepath):
            df_before = df_after.copy()
            df_before.to_excel(before_filepath, index=False)
        else:
            df_before = pd.read_excel(before_filepath)

        # set filename to be the index
        df_before.set_index('Filename', inplace=True)
        df_after.set_index('Filename', inplace=True)

        # convert case to lowercase for comparison
        df_before['Case'] = df_before['Case'].str.lower()
        df_after['Case'] = df_after['Case'].str.lower()

        # find differences in cases
        changed_cases = df_before['Case'] != df_after['Case']

        # filter rows where cases have changed
        changed_filenames = changed_cases[changed_cases].index

        # create new df with changes
        df_changes = pd.DataFrame({
            'filename': changed_filenames,
            'Before Case': df_before.loc[changed_filenames, 'Case'],
            'After Case': df_after.loc[changed_filenames, 'Case']
        }).reset_index(drop=True)

        # check if there are any rows
        rows = len(df_changes)
        if (rows > 0):
            print(f"COMPARE REPORT: {rows} rows...\n")

        df_changes.to_excel(f"excel_data/compare_reports/{self.course_project_title}-report.xlsx", index=False)