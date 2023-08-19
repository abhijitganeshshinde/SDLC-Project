#!/bin/bash

install_nginx() {
    if ! command -v nginx &>/dev/null; then
        read -p "nginx is not installed. Do you want to install it? (Y/N): " install_nginx_input
        install_nginx_input=${install_nginx_input,,}
        
        if [ "$install_nginx_input" == "y" ]; then
            echo "Installing nginx..."
            sudo apt update
            sudo apt install nginx
            echo "Nginx has been installed."
        else
            echo "Not installing nginx."
        fi
    fi
}


install_nginx


install_git() {
    if ! command -v git &>/dev/null; then
        read -p "git is not installed. Do you want to install it? (Y/N): " install_git_input
        install_git_input=${install_git_input,,}
        
        if [ "$install_git_input" == "y" ]; then
            echo "Installing git..."
            sudo apt update
            sudo apt install git
            echo "Git has been installed."
        else
            echo "Not installing git."
        fi
    fi
}


install_git


install_python() {
    if ! command -v python3 &>/dev/null; then
        read -p "Python is not installed. Do you want to install it? (Y/N): " install_python_input
        install_python_input=${install_python_input,,}
        
        if [ "$install_python_input" == "y" ]; then
            echo "Installing Python..."
            sudo apt update
            sudo apt install python3
            echo "Python has been installed."
        else
            echo "Not installing Python."
        fi
    fi
}


install_python


equired_packages=(
    "requests"
    "logging"
    "json"
    "os"
    "tarfile"
    "shutil"
    "re"
    "datetime"
    "zipfile"
    "socket"
    "subprocess"
)

install_missing_packages() {
    missing_packages=()

    for package in "${required_packages[@]}"; do
        if ! python3 -c "import $package" &>/dev/null; then
            missing_packages+=("$package")
        fi
    done

    if [ ${#missing_packages[@]} -gt 0 ]; then
        echo "The following Python packages are missing and will be installed: ${missing_packages[*]}"
        pip install "${missing_packages[@]}"
        echo "Packages installed successfully."
    else
        echo "All required packages are already installed."
    fi
}


install_missing_packages

repository_url="https://github.com/abhijitganeshshinde/SDLC-Project.git"
destination_folder="$HOME/Desktop/SDLC-Project"

if [ ! -d "$destination_folder" ]; then
    echo "Cloning repository..."
    echo "$repository_url"
    git clone "$repository_url" "$destination_folder"
    echo "Repository cloned."
else
    echo "Repository folder already exists. Updating..."
    git -C "$destination_folder" pull
    echo "Repository updated."
fi


config_file="$destination_folder/config.json"
read -p "Enter Access Token: " access_token
read -p "Enter Repository Owner: " repo_owner
read -p "Enter Repository Name: " repo_name
read -p "Enter Target Branch: " target_branch
read -p "Enter Deployment On: " deployment_on

json_data='{
    "RepositoriesDetail": [
        {
            "Access_Token": "'$access_token'",
            "Repository_Owner": "'$repo_owner'",
            "Repository_Name": "'$repo_name'",
            "CICD": [
                {
                    "Target_Branch": "'$target_branch'",
                    "Deployment_On": "'$deployment_on'"
                }
            ]
        }
    ]
}'


echo "$json_data" > "$config_file"
echo "JSON file updated."

deploymentcofig_file="$HOME/Desktop/SDLC-Project/deploymentcofig.json"


echo "Select deployment configuration:"
echo "1. Default"
echo "2. Custom"
read deployment_choice


if [ "$deployment_choice" == "1" ]; then
    default_json='{
        "Nginx_Config_File_Location": "/etc/nginx/sites-available",
        "Nginx_Config_File": "default",
        "DeploymentDetails": [
            {
                "Repository_Name": "CICDPipelineForHTML",
                "Deploy": [
                    {
                        "Env": "QA",
                        "Target_Branch": "dev",
                        "Location": "/var/www/qa",
                        "FolderName": "awesomeweb",
                        "Url": "qa-awesomeweb.local",
                        "MainFile": "index.html"
                    }
                ]
            }
        ]
    }'


echo "$default_json" > "$deploymentcofig_file"
echo "Default deployment configuration applied."

elif [ "$deployment_choice" == "2" ]; then

    read -p "Enter Repository Name: " repo_name
    read -p "Enter Environment: " env
    read -p "Enter Deployment On: " deployment_on
    read -p "Enter Target Branch: " target_branch
    read -p "Enter Location: " location
    read -p "Enter Folder Name: " folder_name
    read -p "Enter URL: " url
    read -p "Enter Main File: " main_file
    

    custom_json='{
        "Nginx_Config_File_Location": "/etc/nginx/sites-available",
        "Nginx_Config_File": "default",
        "DeploymentDetails": [
            {
                "Repository_Name": "'$repo_name'",
                "Deploy": [
                    {
                        "Env": "'$env'",
                        "Target_Branch": "'$target_branch'",
                        "Location": "'$location'",
                        "FolderName": "'$folder_name'",
                        "Url": "'$url'",
                        "MainFile": "'$main_file'"
                    }
                ]
            }
        ]
    }'

    echo "$custom_json" > "$deploymentcofig_file"
    echo "Custom deployment configuration applied."

else
    echo "Invalid choice."
fi


sudo chmod 777 /var/www
sudo chmod 777 /etc/nginx/sites-available/default
sudo chmod 777 /etc/hosts
chmod 777 "$destination_folder/checknewcommit.py"
sudo chmod +x "$destination_folder/run_pythonprogram.sh"

bash_script_path="$HOME/Desktop/SDLC-Project/run_pythonprogram.sh"
cron_expression="*/1 * * * *"

add_cron_job() {
    
    if crontab -l | grep -q "$bash_script_path"; then
        echo "Cron job already exists."
    else
        
        (crontab -l ; echo "$cron_expression  $bash_script_path") | crontab -
        echo "Cron job added successfully."
    fi
}

add_cron_job

sudo systemctl restart nginx
sudo systemctl restart cron

echo "Nginx and cron service restarted."
