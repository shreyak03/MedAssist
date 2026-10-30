
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'medassist-api'
        IMAGE_TAG = '1.0'
        PYTHON_EXE = 'C:\\Users\\Admin\\AppData\\Local\\Programs\\Python\\Python311\\python.exe'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out MedAssist AI source code'
                checkout scm
            }
        }

        stage('Verify Environment') {
            steps {
                bat '''
                    echo Checking Python version
                    "%PYTHON_EXE%" --version

                    echo Checking Docker version
                    docker --version

                    echo Checking Docker Compose
                    docker compose version
                '''
            }
        }

        stage('Setup Python and Install') {
            steps {
                bat '''
                    echo Creating Python virtual environment
                    "%PYTHON_EXE%" -m venv .venv

                    echo Upgrading pip
                    .venv\\Scripts\\python.exe -m pip install --upgrade pip

                    echo Installing project dependencies
                    .venv\\Scripts\\python.exe -m pip install -r requirements.txt

                    echo Installing pytest
                    .venv\\Scripts\\python.exe -m pip install pytest
                '''
            }
        }

        stage('Run Tests') {
            steps {
                bat '''
                    echo Running automated tests
                    .venv\\Scripts\\python.exe -m pytest -v
                '''
            }
        }

        stage('Build Backend Docker Image') {
            steps {
                bat '''
                    echo Building MedAssist backend Docker image
                    docker build -t %IMAGE_NAME%:%IMAGE_TAG% .
                '''
            }
        }

        stage('Build Frontend Docker Image') {
            steps {
                bat '''
                    echo Building MedAssist frontend Docker image
                    docker build -t medassist-frontend:1.0 -f frontend/Dockerfile .
                '''
            }
        }

        stage('Verify Docker Images') {
            steps {
                bat '''
                    echo Listing generated Docker images
                    docker images
                '''
            }
        }
    }

    post {
        success {
            echo 'MedAssist AI CI Pipeline completed successfully!'
        }

        failure {
            echo 'MedAssist AI CI Pipeline failed. Check the console output.'
        }

        always {
            echo 'Pipeline execution finished.'
        }
    }
}
