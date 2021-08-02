// pipeline
pipeline {
    agent none
    environment {
        DOCKER_CONTAINER_NAME = 'app-info-about-movies' 
    }
    stages {
        stage('Linting python code') {
            agent any
            when {branch 'development'}
            steps {
                sh "pyflakes3 ./app-info-about-movies/"
            }
        }
        stage('Build and check Docker Image') {
            agent {dockerfile true}
            when {branch 'staging'}
            steps {
                echo "Building docker image ${DOCKER_CONTAINER_NAME}"
                sh """ 
                    pwd
                    docker image build -t "${DOCKER_CONTAINER_NAME}" .
                    sleep 5 && docker image list
                """ 
                    
                sh  ''' echo "Checking vulnerabilities with trivy"
                        trivy --clear-cache image --ignore-unfixed --severity CRITICAL,HIGH --exit-code 1 app-info-about-movies
                        trivy --clear-cache image --ignore-unfixed --severity MEDIUM,LOW --exit-code 0 app-info-about-movies
                        sleep 5
                    '''
             }
        }
        stage('Check Docker Contrainer locally') {
            agent any
            when {branch 'staging'}
            steps {
                sh  ''' echo "Stop and remove container if exists"
                        docker stop app-info-about-movies || true && docker rm app-info-about-movies || true
                        echo "Run container"
                        docker container run -d -p 5000:5000 --name "app-info-about-movies" app-info-about-movies
                        echo "List running containers"
                        sleep 5 && docker container list
                        echo "Try running app"
                        curl http://localhost:5000
                        echo "Stop and remove container"
                        docker container stop app-info-about-movies && docker container rm app-info-about-movies
                        echo "Pruning docker"
                        docker system prune -f
                    '''
             }
        }
        stage('Push Docker image') {
            agent any
            when {branch 'staging'}
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




