// pipeline
pipeline {
    agent none
    environment {
        DOCKER_IMAGE_NAME = 'app_info_about_movies' 
        DOCKER_CONTAINER_NAME = 'info-about-movies' 
    }
    stages {
        stage('Linting and testing python code') {
            agent any
            when {branch 'development'}
            steps {
                sh """
                    echo "Current directory"
                    pwd
                    echo "List of files"
                    ls
                    echo "Scan Filesystem for Vulnerabilities and Misconfigurations"
                    trivy fs --ignore-unfixed --severity CRITICAL,HIGH --exit-code 1 --security-checks vuln,config .
                """ 
            }
            {
                sh """ 
                    echo "Linting code with pyflakes"
                    pyflakes *.py  ./app_info_about_movies/
                """ 
            }
            {
                sh """ 
                    echo "Performing pytest"
                    pytest
                """                         
            }
            {
                sh 'python3 ./run_flask_metadaten.py &'
                sh 'sleep 5 && curl -f localhost:5000'
            }
        }
        stage('Build and check Docker Image') {
            agent any
            when { anyOf {branch 'development'; branch 'staging'} }
            steps {
                echo "Building docker image ${DOCKER_IMAGE_NAME}"
                sh """ 
                    pwd
                    docker image build -t ${DOCKER_IMAGE_NAME} .
                    sleep 5 && docker image list
                """ 
                    
                echo "Checking vulnerabilities with trivy"
                sh """  
                        trivy --clear-cache image --ignore-unfixed --severity CRITICAL,HIGH --exit-code 1 ${DOCKER_IMAGE_NAME}
                        trivy --clear-cache image --ignore-unfixed --severity MEDIUM,LOW --exit-code 0 ${DOCKER_IMAGE_NAME}
                        sleep 5
                   """ 
             }
        }
        stage('Check locally that Docker Contrainer is running') {
            agent any
            when {branch 'staging'}
            steps {
                echo "Stop and remove container if exists"
                sh "docker stop ${DOCKER_CONTAINER_NAME} || true && docker rm ${DOCKER_CONTAINER_NAME} || true"
                
                echo "Run container"
                sh "docker container run -d -p 5001:5000 --name ${DOCKER_CONTAINER_NAME}  ${DOCKER_IMAGE_NAME}"
                
                echo "List running containers"
                sh "sleep 7 && docker container list"

                echo "Try running app"
                sh "curl -f  http://localhost:5001 && sleep 5"
                
                echo "Stop and remove container"
                sh "docker container stop ${DOCKER_CONTAINER_NAME} && docker container rm ${DOCKER_CONTAINER_NAME}"
                
                echo "Pruning docker"
                sh "docker system prune -f"
                    
             }
        }
        stage('Push Docker image') {
            agent any
            when {branch 'production'}
            steps {
                sh 'echo "Pushihg docker image"'
                withDockerRegistry([url: "", credentialsId: "dockerhub_id"]) {
                    sh "docker tag app_info_about_movies olalakul/app_info_about_movies"
                    sh 'docker push olalakul/app_info_about_movies'
                }
            }
        }
        stage('Deploy locally from Docker Container') {
            agent any
            when {branch 'production'}
            steps{
                sh  ''' echo "Run container"
                        docker container run -d -p 5000:5000 --name "app_info_about_movies" olalakul/app_info_about_movies
                    '''
                input message: 'Finished using the web site? (Click "Proceed" button in BlueOcean to continue)'
                sh 'docker container stop app_info_about_movies && docker container rm app_info_about_movies'
                sh 'echo "Pruning docker"  && docker system prune -f'
            }
        }
    }
}




