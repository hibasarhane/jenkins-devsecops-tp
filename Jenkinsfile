pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', 
                    url: 'https://github.com/hibasarhane/jenkins-devsecops-tp.git'
            }
        }
        
        stage('Installer dépendances') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt || true
                    pip install safety bandit
                '''
            }
        }
        
        stage('Tests unitaires') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest test_app.py -v --junitxml=test-results.xml
                '''
            }
        }
        
        stage('Scan SAST - Bandit') {
            steps {
                sh '''
                    . venv/bin/activate
                    bandit -r . -f html -o bandit-report.html || true
                '''
            }
        }
        
        stage('🔴 Scan SCA - Safety') {
            steps {
                sh '''
                    . venv/bin/activate
                    safety check --full-report
                '''
            }
        }
        
        stage('Scan SAST - SonarQube') {
            steps {
                script {
                    def scannerHome = tool 'SonarQubeScanner'
                    withSonarQubeEnv('SonarQube') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=TP-Jenkins-Security \
                            -Dsonar.sources=. \
                            -Dsonar.python.version=3 \
                            -Dsonar.host.url=http://172.17.0.1:9000 \
                            -Dsonar.login=sqp_8112f02c51e4b2453eb5a6dfc1378e35bba0ba37
                        """
                    }
                }
            }
        }
        
        stage('Quality Gate') {
            steps {
                timeout(time: 1, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: '*.html, reports/**', fingerprint: true
            junit 'test-results.xml'
        }
        failure {
            echo '❌❌❌ PIPELINE ÉCHOUÉ - VULNÉRABILITÉS DÉTECTÉES !'
        }
    }
}