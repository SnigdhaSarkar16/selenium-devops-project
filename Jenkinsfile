pipeline {

    agent any

    options {
        timestamps()
    }

    stages {

        stage('Checkout Code') {
            steps {
                echo 'Retrieving project from GitHub...'
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                echo 'Creating Python virtual environment...'
                bat 'python -m venv .venv'
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing project dependencies...'
                bat '''
                    .venv\\Scripts\\python.exe -m pip install --upgrade pip
                    .venv\\Scripts\\python.exe -m pip install -r requirements.txt
                '''
            }
        }

        stage('Run Selenium Tests') {
            steps {
                echo 'Running Selenium automated tests...'
                bat '''
                    if not exist test-results mkdir test-results
                    .venv\\Scripts\\python.exe -m pytest tests/ -v --junitxml=test-results\\results.xml
                '''
            }
        }
    }

    post {

        always {
            echo 'Publishing test results...'

            junit(
                testResults: 'test-results/results.xml',
                allowEmptyResults: true
            )
        }

        success {
            echo 'All automated tests passed successfully.'
        }

        failure {
            echo 'Automated testing failed. Check the console output.'
        }
    }
}