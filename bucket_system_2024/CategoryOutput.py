import pandas as pd
import os

class CategoryOutput:
    def __init__(self, transaction_list, course_project_title):
        self.list_of_categories = []
        self.course_project_title = course_project_title
        self.transaction_list = transaction_list
        other_transactions = ["login", "logout", "exit"]
        self.transaction_list += other_transactions

    def transaction_finder(self, filename, transaction, validation_result, failed_param_name, failed_param_value, logout_line, user_type=None):
        # if transaction log is not refund, add to list
        if (transaction != "refund"):
            self.list_of_categories.append([self.course_project_title, filename, transaction, validation_result, failed_param_name, failed_param_value, user_type, logout_line])

    def create_dataframe(self, course_project_title):
        # create dataframe with specified columns
        df = pd.DataFrame(self.list_of_categories, columns=["Project Title", "Filename", "Transaction", "Bucket Category", "Failed Param", "Failed Value", "User Type", "Logout Line"])

        # analyze the input that failed and add tags/attributes
        analysis_col = df["Failed Value"].apply(self.analyze_inputs)
        df_analysis = pd.DataFrame(analysis_col.tolist())
        df_combined = pd.concat([df, df_analysis], axis=1)

        # export to excel
        df_combined.to_excel(f"excel_data/after_cases/{course_project_title}-after.xlsx", index=False)

    def analyze_inputs(self, input_data):
        # find type of input data that failed
        data_info = {"type": type(input_data).__name__}

        # try to change to digit
        try:
            if (input_data.isdigit()):
                input_data = int(input_data)
            else:
                input_data = float(input_data)

            data_info = {"type": type(input_data).__name__}
        
            # Additional information for numbers
            if isinstance(input_data, (int, float)):
                if input_data > 0:
                    data_info["number_type"] = "positive"
                elif input_data < 0:
                    data_info["number_type"] = "negative"
                else:
                    data_info["number_type"] = "zero"
        # if none type, pass the error and go to next column
        except (TypeError, AttributeError):
            pass
        # if str type, add attributes/tags
        except ValueError as e:
            data_info = {"type": type(input_data).__name__}

            data_info["str_length"] = len(input_data)

            if (input_data in self.transaction_list):
                data_info["fail_transaction_call"] = True
            else:
                data_info["fail_transaction_call"] = False

            if any(ord(char) > 127 for char in input_data):  # Check for non-ASCII characters
                data_info["contains_non_ascii"] = True
            else:
                data_info["contains_non_ascii"] = False

        return data_info
    
    def compare_excel_before_after(self, course_project_title):
        # save file path
        before_filepath = f"excel_data/before_cases/{course_project_title}-before.xlsx"
        after_filepath = f"excel_data/after_cases/{course_project_title}-after.xlsx"

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
        df_before['Bucket Category'] = df_before['Bucket Category'].str.lower()
        df_after['Bucket Category'] = df_after['Bucket Category'].str.lower()

        # find differences in cases
        changed_cases = df_before['Bucket Category'] != df_after['Bucket Category']

        # filter rows where cases have changed
        changed_filenames = changed_cases[changed_cases].index

        # create new df with changes
        df_changes = pd.DataFrame({
            'filename': changed_filenames,
            'Before Case': df_before.loc[changed_filenames, 'Bucket Category'],
            'After Case': df_after.loc[changed_filenames, 'Bucket Category']
        }).reset_index(drop=True)

        # check if there are any row changes
        rows = len(df_changes)
        print(f"\nCOMPARE REPORT: {rows} rows...\n")

        df_changes.to_excel(f"excel_data/compare_reports/{course_project_title}-report.xlsx", index=False)