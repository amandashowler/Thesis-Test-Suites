from BucketSystem import BucketSystem
import json

def main():
    #"""
    projects_done = ["N-Project-02", "N-Project-03", "N-Project-06", "S-Project-01",
                     "S-Project-02", "S-Project-05", "S-Project-06", "S-Project-10"]
    
    projects_problem = ["S-Project-03", "S-Project-07", "S-Project-08",
                        "S-Project-09", "S-Project-11"]
    
    projects_no_config = ["N-Project-01", "N-Project-04", "N-Project-05", "S-Project-04"]

    projects_to_test = []
    projects_to_test.append(projects_done)
    #projects_to_test.append(projects_problem) # S-Project-07 will fail on password

    projects_to_test = [project for sublist in projects_to_test for project in sublist]
    
    for project in projects_to_test:
        # project to test
        course_project_title = project
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

if __name__ == "__main__":
    main()