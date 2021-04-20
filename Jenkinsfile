// pipeline
pipeline {
    agent any
    stages {
        stage('Linting python code') {
            steps {
                sh 'pyflakes ./app-info-about-movies/'
            }
        }
        stage('Build Docker Image') {
            steps {
                sh  ''' echo "Building docker image"
                        pwd
                        docker image build -t "app-info-about-movies" .
                        sleep 5 && docker image list
                    '''
                sh  ''' echo "Checking vulnerabilities with trivy"
                        trivy --clear-cache image --ignore-unfixed --severity CRITICAL,HIGH --exit-code 1 app-info-about-movies
                        trivy --clear-cache image --ignore-unfixed --severity MEDIUM,LOW --exit-code 0 app-info-about-movies
                        sleep 5
                    '''
             }
        }
        stage('Check Docker Contrainer locally') {
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
                    '''
             }
        }
        stage('Deploy locally from Docker Container') {
            steps{
                sh  ''' echo "Run container"
                        docker container run -d -p 5000:5000 --name "app-info-about-movies" app-info-about-movies
                    '''
            }
        }
        stage('Clean up') {
            steps{
                sh 'echo "Pruning docker"  && docker system prune -f'
            }
        }
    }
}




