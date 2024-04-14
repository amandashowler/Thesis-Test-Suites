import os
import pandas as pd

from TestParser import TestParser
from UserDB import UserDB
from ItemDB import ItemDB

class BucketSystem:
    def __init__(self, course_project_title, test_input_file_endswith, test_folder_fp, user_fp, item_fp, config): # fp = file path
        self.endswith = test_input_file_endswith
        self.course_project_title = course_project_title
        self.test_fp = test_folder_fp
        self.userDB = []
        self.itemDB = []
        self.filename_list = []
        self.bucket_category_list = []
        self.transaction_line = config['password']['transaction_line']
        self.parser = TestParser(UserDB(user_fp, config), ItemDB(item_fp, config), config)

        # for printing only
        self.how_wide = 90
        self.how_wide_bucket = (self.how_wide - 6) // 2
        self.print_titles = ['Filename', 'Bucket']

    def export_to_excel(self):
        # check that they have the same length
        if (len(self.filename_list) != len(self.bucket_category_list)):
            print("ERROR: Filename and cases must be the same length")
            return -1
        
        # create the dataframe
        df = pd.DataFrame({'Filename': self.filename_list, 'Case': self.bucket_category_list})

        # write to excel file with no index
        df.to_excel(f"excel_data/{self.course_project_title}.xlsx", index=False)

        return 0

    def process_all_txts(self):
        print("-"*self.how_wide)
        print(f'|  {self.print_titles[0].ljust(self.how_wide_bucket + 1)}| {self.print_titles[1].ljust(self.how_wide_bucket)}|')

        # loop through the txt files (tests)
        for filename in os.listdir(self.test_fp):

            # only process files for the transaction to test
            if filename.endswith(self.endswith): # and filename.startswith(self.transaction_to_test):

                # concatenate the file path
                file_path = os.path.join(self.test_fp, filename)

                self.process_txt(file_path, filename)

        check = self.export_to_excel()

    def process_txt(self, file_path, filename):

        # open file read only
        with open(file_path, 'r') as file:
            print("-"*self.how_wide)
            #print(filename)

            bucket_category = 'unknown'
            file_lines = []

            # add lines to an array
            for line in file:
                file_lines.append(line.strip())

            # check if valid login
            bucket_login = self.parser.parse_login(file_lines)

            if bucket_login == 'none':
                transaction_txt = file_lines[self.transaction_line].lower()


                if (transaction_txt == "addcredit"):
                    bucket_category = self.parser.parse_addcredit(file_lines, transaction_txt)
                elif (transaction_txt == "advertise"):
                    bucket_category = self.parser.parse_advertise(file_lines, transaction_txt)
                elif (transaction_txt == "allitems") or (transaction_txt == "listitems") or (transaction_txt == "listallitems"): #listitems
                    bucket_category = self.parser.parse_allitems(file_lines)
                elif (transaction_txt == "allusers") or (transaction_txt == "listusers") or (transaction_txt == "listallusers"):
                    bucket_category = self.parser.parse_allusers(file_lines)
                elif (transaction_txt == "bid"):
                    bucket_category = self.parser.parse_bid(file_lines, transaction_txt)
                elif (transaction_txt == "create"):
                    bucket_category = self.parser.parse_create(file_lines, transaction_txt)
                elif (transaction_txt == "delete"):
                    bucket_category = self.parser.parse_delete(file_lines, transaction_txt)
                elif (transaction_txt == "refund"):
                    bucket_category = self.parser.parse_refund(file_lines, transaction_txt)
                else:
                    bucket_category = 'ERROR_nothing_matched'
            
            else:
                bucket_category = bucket_login

            self.filename_list.append(filename)
            self.bucket_category_list.append(bucket_category)

            # PRINTING SPOT
            
            # normal print
            # print count: 6 + ljust(30) + ljust(29) = 65
            print(f'|  {filename.ljust(self.how_wide_bucket + 1)[:self.how_wide_bucket]}| {bucket_category.ljust(self.how_wide_bucket)[:self.how_wide_bucket]}|')

            # filenames
            #print(filename)
            
            # bucket sorting
            #print(bucket_category)

            # debug print
            #print(f'Processing {filename}...')
            #print(f"Case for {filename}:\n{bucket_category}\n")

        


            

