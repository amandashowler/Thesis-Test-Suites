from BucketSystem import BucketSystem
import json
import os
import time

def main():
    list_projects = []
    
    for filename in os.listdir("config_files"):
        course_project_title = os.path.splitext(filename)[0]
        list_projects.append(course_project_title)

        print("-----------------------------------------------")
        print(f"\nRunning {course_project_title} tests...")
        
        config_path = f"config_files/{course_project_title}.json"

        # load json config file
        with open(config_path, 'r') as file:
            config = json.load(file)

        # specify filepath - my data
        test_input_fp = f"project_files/{course_project_title}/input"
        user_fp = f"project_files/{course_project_title}/databases/user_accounts_file.txt"
        item_fp = f"project_files/{course_project_title}/databases/available_items_file.txt"
        test_input_file_endswith = config['file']['test_input_file_endswith']
        
        # create system and process test
        system = BucketSystem(course_project_title, test_input_file_endswith, test_input_fp, user_fp, item_fp, config)
        system.process_all_txts()

        print(list_projects)
        #time.sleep(10)

if __name__ == "__main__":
    main()