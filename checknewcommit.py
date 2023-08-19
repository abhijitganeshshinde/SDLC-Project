import os
import files_service 
import git_api_service
import runbash_service
import logging
from datetime import datetime


def CICD(current_path,download_path,config_filepath,lastcommit_filepath,deploymentcofig_filepath,backup_path,nginx_config_server_sample):
    logging.info("Starting the CICD process.")
    try:
        if os.path.exists(config_filepath):
            
            is_configfilereadable,configData = files_service.read_jsonfile(config_filepath)

            if is_configfilereadable:

                repositories_detail = configData["RepositoriesDetail"]

                for  repository_detail in repositories_detail:
                    
                    repository_owner = repository_detail["Repository_Owner"]
                    repository_name = repository_detail["Repository_Name"]
                    access_token = repository_detail["Access_Token"]
                    cicd_details = repository_detail["CICD"]

                    is_repo_exist = git_api_service.check_repository_exists(repository_owner,repository_name,access_token)

                    if is_repo_exist:
                        
                        for entry in cicd_details:
                            
                            files_service.delete_file(download_path)
                            files_service.delete_folder(extracted_code_path)
                            target_branch = entry["Target_Branch"]
                            deployment_on = entry["Deployment_On"]

                            is_branch_exist = git_api_service.check_branch_exists(repository_owner,repository_name,target_branch,access_token)
                            
                            if is_branch_exist:
                                lastcommit_file_exist = True
                                if not os.path.exists(lastcommit_filepath):
                                    lastcommit_file_exist,latcommit_file_data = files_service.create_lastcommitfile(lastcommit_filepath)
                                    result_repo_added = files_service.add_repository(latcommit_file_data,repository_name)
                                    if result_repo_added:
                                        result_branch_added = files_service.add_branch(latcommit_file_data["Repositories"][0],repository_name, target_branch, "")
                                    if result_branch_added:
                                            is_second_lastcommit,second_last_commit_sha = git_api_service.get_commit_sha(access_token,repository_owner, repository_name,target_branch,1)
                                            files_service.update_commit(latcommit_file_data,repository_name,target_branch,second_last_commit_sha)
                                            files_service.update_file(lastcommit_filepath,latcommit_file_data)

                                if lastcommit_file_exist:
                                    is_lastcommitfilereadable,lastcommitfiledata = files_service.read_jsonfile(lastcommit_filepath)
                                    if is_lastcommitfilereadable:
                                        repo_exist_in_cmmmitfile = files_service.repository_exists(lastcommitfiledata,repository_name)

                                        if not repo_exist_in_cmmmitfile:
                                            is_repo_added = files_service.add_repository(lastcommitfiledata,repository_name)

                                            if is_repo_added:
                                                is_branch_added = files_service.add_branch(lastcommitfiledata,repository_name,target_branch,"")
                                                if is_branch_added:
                                                    files_service.update_file(lastcommit_filepath,lastcommitfiledata)
                                        else:
                                            branch_exist_in_cmmmitfile = files_service.branch_exists(lastcommitfiledata,repository_name,target_branch)

                                            if not branch_exist_in_cmmmitfile:
                                                files_service.add_branch(lastcommitfiledata,repository_name,target_branch,"")
                                                files_service.update_file(lastcommit_filepath,lastcommitfiledata)
                                        
                                        is_last_commit,latest_commit_sha = git_api_service.get_commit_sha(access_token,repository_owner, repository_name,target_branch)
                                        commit_sha_for_file =  files_service.get_commit_sha(lastcommitfiledata,repository_name,target_branch)
                                        if is_last_commit and latest_commit_sha != commit_sha_for_file:
                                            is_lastcommitfilereadable,lastcommitfiledata = files_service.read_jsonfile(lastcommit_filepath)

                                            if is_lastcommitfilereadable:

                                                is_update_commit = files_service.update_commit(lastcommitfiledata,repository_name,target_branch,latest_commit_sha)
                                                if is_update_commit:
                                                    is_update_file = files_service.update_file(lastcommit_filepath,lastcommitfiledata)
                                                    if is_update_file:
                                                        is_download_updated_code = git_api_service.download_updated_code(access_token,repository_owner, repository_name, latest_commit_sha,download_path)
                                                        if is_download_updated_code:
                                                            download_path = os.path.join(current_path, "downloaded_code.tar.gz")
                                                            extract_folder = os.path.join(current_path, "extracted_code")
                                                            _latest_commit_sha = latest_commit_sha[:7]
                                                            files_service.extract_archive(download_path, extract_folder)
                                                            print("Code extracted to:", extract_folder)
                                                            old_folder_path = os.path.join(extract_folder,f"{repository_owner}-{repository_name}-{_latest_commit_sha}")
                                                            new_folder_path = os.path.join(extract_folder,repository_name)
                                                            files_service.rename_folder(old_folder_path,new_folder_path)
                                                            is_deploymentfilereadable, deploymentdata = files_service.read_jsonfile(deploymentcofig_filepath)
                                                            if is_deploymentfilereadable:
                                                                is_deployment_forbranchreable,deploymentdata_forbranch = files_service.get_deployment_details(deploymentdata,repository_name,target_branch)
                                                                if is_deployment_forbranchreable:
                                                                    is_env_folder = files_service.create_folder(deploymentdata_forbranch["Location"])
                                                                    #result_env_folder = files_service.create_folder(os.path.join("var","www","qa/"))
                                                                    if is_env_folder:
                                                                        result_folder = files_service.create_folder(os.path.join(deploymentdata_forbranch["Location"],deploymentdata_forbranch["FolderName"]))
                                                                        if result_folder:
                                                                            files_service.backup_and_compress_folder(os.path.join(deploymentdata_forbranch["Location"],deploymentdata_forbranch["FolderName"]),backup_path)
                                                                            files_service.copy_data(new_folder_path,os.path.join(deploymentdata_forbranch["Location"],deploymentdata_forbranch["FolderName"]))
                                                                            result_ngixs,ngixs_data = files_service.read_nginx_config(os.path.join(deploymentdata["Nginx_Config_File_Location"],deploymentdata["Nginx_Config_File"]))
                                                                            ressultngixs_serverdata,ngixs_serverdata = files_service.read_all_server_blocks(ngixs_data)
                                                                            resultsec_ngixs_serverdata,sec_ngixs_serverdata = files_service.read_server_block_by_name(ngixs_data,deploymentdata_forbranch["Url"])
                                                                            if resultsec_ngixs_serverdata:
                                                                                is_hostfile_entry = files_service.is_host_entry_present(deploymentdata_forbranch["Url"])
                                                                                if is_hostfile_entry:
                                                                                    runbash_service.restart_nginx()
                                                                                    
                                                                                else:

                                                                                   is_hostfile =files_service.add_host_entry(deploymentdata_forbranch["Url"])
                                                                                   if is_hostfile:
                                                                                        runbash_service.restart_nginx()
                                                                                    
                                                                                
                                                                            else:
                                                                                result_ngixs_server_sample,ngixs_server_sample = files_service.read_nginx_config(nginx_config_server_sample)
                                                                                if result_ngixs_server_sample:
                                                                                    ngixs_server_sample = ngixs_server_sample.replace("@domain",deploymentdata_forbranch["Url"])
                                                                                    ngixs_server_sample = ngixs_server_sample.replace("@location",os.path.join(deploymentdata_forbranch["Location"],deploymentdata_forbranch["FolderName"]))
                                                                                    ngixs_server_sample = ngixs_server_sample.replace("@index",deploymentdata_forbranch["MainFile"])
                                                                                    add_server,add_server_data = files_service.add_server_block(ngixs_data,ngixs_server_sample)
                                                                                    if add_server:
                                                                                        files_service.update_nginx_config(os.path.join(deploymentdata["Nginx_Config_File_Location"],deploymentdata["Nginx_Config_File"]),add_server_data)
                                                                                        is_hostfile_entry = files_service.is_host_entry_present(deploymentdata_forbranch["Url"])
                                                                                        if is_hostfile_entry:
                                                                                            runbash_service.restart_nginx()
                                                                                            
                                                                                        else:
                                                                                            is_hostfile =files_service.add_host_entry(deploymentdata_forbranch["Url"])
                                                                                            if is_hostfile:
                                                                                                runbash_service.restart_nginx()
                                                                                                
                                                                            
            else:
                print("Some issue with config file")
                logging.info("Some issue with config file")

        else:
            logging.error("Config file not found.")
            print(
                "config file required*.\n"
                "File Name : config.json\n"
                "Format:\n"
                '''{
                    "RepositoryDetails": [
                        {
                            "Repository_Owner": "repository_owner",
                            "Repository_Name": "repository_name",
                            "CICD": [
                                {
                                    "Target_Branch": "dev",
                                    "Deployment_On": "QA"
                                },
                                {
                                    "Target_Branch": "qa",
                                    "Deployment_On": "UAT"
                                },
                                {
                                    "Target_Branch": "prod",
                                    "Deployment_On": "PROD"
                                }
                            ]
                        }
                    ]
                }'''
            )
    except Exception as e:
        print(f"An error occurred: {e}")


    
if __name__ == "__main__":
    try:
            
        current_path = os.getcwd()
        log_folder = os.path.join(current_path, "logs")
        os.makedirs(log_folder, exist_ok=True)
        current_date = datetime.now().strftime("%d-%m-%y")
        log_file_path = os.path.join(log_folder, f"{current_date}.log")
        logging.basicConfig(filename=log_file_path,level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        download_path = os.path.join(current_path, "downloaded_code.tar.gz")
        config_filepath =   os.path.join(current_path, "config.json")
        lastcommit_filepath =  os.path.join(current_path, "last_commit.json")
        deploymentcofig_filepath =  os.path.join(current_path, "deploymentcofig.json")
        extracted_code_path = os.path.join(current_path, "extracted_code")
        backup_path = os.path.join(current_path, "backup_code")
        nginx_config_server_sample = os.path.join(current_path, "nginx_config_server_sample.txt")
        CICD(current_path,download_path,config_filepath,lastcommit_filepath,deploymentcofig_filepath,backup_path,nginx_config_server_sample)
    except Exception as e:
        logging.exception("An exception occurred during program execution: %s", e)


    

