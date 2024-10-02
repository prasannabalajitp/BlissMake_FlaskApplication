pipeline {
    agent any

    stages {
        stage('Clone Repository') {
            steps {
                git url: 'https://github.com/prasannabalajitp/BlissMake_FlaskApplication.git', branch: 'main'
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    def app = docker.build("flask-app:${env.BUILD_ID}")
                }
            }
        }
        stage('Run Docker Container') {
            steps {
                script {
                    docker.image("flask-app:${env.BUILD_ID}").run(
                        "-d --name blissmake -p 5000:5000 " +
                        "-e SECRET_KEY='' " +
                        "-e MONGO_URI='' " +
                        "-e UPI_ID='' " +
                        "-e PAYEE_NAME=''"
                    )
                }
            }
        }
    }

    post {
        always {
            echo 'Cleaning up...'
            sh "docker rm -f blissmake || true"
            sh "docker rmi -f flask-app:${env.BUILD_ID} || true"
        }
    }
}
