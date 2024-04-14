from BucketSystem import BucketSystem
import json

def main():
    # project to test
    #course_project_title = "My-Project"
    #course_project_title = "New-Frontend"
    #course_project_title = "Brogrammers-Auctions"
    course_project_title = "CSCI3060_GroupProject"
    
    config_path = "config_files/" + course_project_title + ".json"

    # load json config file
    with open(config_path, 'r') as file:
        config = json.load(file)

    # specify filepath - my data
    test_input_fp = config['file']['test_input_fp']
    test_input_file_endswith = config['file']['test_input_file_endswith']
    user_fp = config['file']['user_fp']
    item_fp = config['file']['item_fp']

    # create system and process test
    system = BucketSystem(test_input_file_endswith, test_input_fp, user_fp, item_fp, config)
    system.process_all_txts()

if __name__ == "__main__":
    main()