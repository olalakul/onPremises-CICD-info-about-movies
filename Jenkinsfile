// pipeline
pipeline {
    agent none
    environment {
        DOCKER_IMAGE_NAME = 'app-info-about-movies' 
        DOCKER_CONTAINER_NAME = 'info-about-movies' 
    }
    stages {
        stage('Linting python code') {
            agent any
            when {branch 'development'}
            steps {
                sh "pyflakes ./app-info-about-movies/"
            }
        }
        stage('Build and check Docker Image') {
            agent any
            when {branch 'staging'}
            steps {
                echo "Building docker image ${DOCKER_IMAGE_NAME}"
                sh """ 
                    pwd
                    docker image build -t ${DOCKER_IMAGE_NAME} .
                    sleep 5 && docker image list
                """ 
                    
                echo "Checking vulnerabilities with trivy"
                sh """  trivy --clear-cache image --ignore-unfixed --severity CRITICAL,HIGH --exit-code 1 ${DOCKER_IMAGE_NAME}
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
                sh "docker container run -d -p 5000:5000 --name ${DOCKER_CONTAINER_NAME}  ${DOCKER_IMAGE_NAME}"
                
                echo "List running containers"
                sh "sleep 5 && docker container list"
                
                echo "Try running app"
                sh "curl http://localhost:5000"
                
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
                    sh "docker tag app-info-about-movies olalakul/app-info-about-movies"
                    sh 'docker push olalakul/app-info-about-movies'
                }
            }
        }
        stage('Deploy locally from Docker Container') {
            agent any
            when {branch 'production'}
            steps{
                sh  ''' echo "Run container"
                        docker container run -d -p 5000:5000 --name "app-info-about-movies" olalakul/app-info-about-movies
                    '''
                input message: 'Finished using the web site? (Click "Proceed button in BlueOcean" to continue)'
                sh 'docker container stop app-info-about-movies && docker container rm app-info-about-movies'
                sh 'echo "Pruning docker"  && docker system prune -f'
            }
        }
    }
}




