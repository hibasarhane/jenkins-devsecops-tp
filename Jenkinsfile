pipeline {
    agent any
    
    environment {
        PATH = "/usr/local/bin:${env.PATH}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', 
                    url: 'https://github.com/hibasarhane/jenkins-devsecops-tp.git'
                echo '✅ Code récupéré depuis GitHub'
            }
        }
        
        stage('Installer les dépendances') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    
                    # Installation des versions vulnérables
                    pip install requests==2.25.1 flask==1.1.2 jinja2==2.11.3 pyyaml==5.3.1 pytest==6.2.5 || true
                    pip install safety bandit
                    
                    echo "✅ Dépendances vulnérables installées"
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
        
        stage('Scan SCA - Safety') {
            steps {
                sh '''
                    . venv/bin/activate
                    safety check --full-report || true
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
                timeout(time: 2, unit: 'MINUTES') {
                    script {
                        def sonarUrl = "http://172.17.0.1:9000"
                        def projectKey = "TP-Jenkins-Security"
                        
                        sleep 10
                        
                        def taskId = sh(
                            script: "curl -s '${sonarUrl}/api/ce/component?component=${projectKey}' | grep -o '\"id\":\"[^\"]*\"' | head -1 | cut -d'\"' -f4",
                            returnStdout: true
                        ).trim()
                        
                        if (taskId) {
                            def qualityGate = sh(
                                script: "curl -s '${sonarUrl}/api/qualitygates/project_status?projectKey=${projectKey}' | grep -o '\"status\":\"[^\"]*\"' | head -1 | cut -d'\"' -f4",
                                returnStdout: true
                            ).trim()
                            
                            echo "🏁 Quality Gate: ${qualityGate}"
                            
                            if (qualityGate == "ERROR") {
                                error "❌ Quality Gate échoué!"
                            }
                        }
                    }
                }
            }
        }
        
        stage('🔴 BLOCAGE DES VULNÉRABILITÉS') {
            steps {
                script {
                    def criticalVulns = sh(
                        script: '''
                            . venv/bin/activate
                            safety check --bare | grep -E "CRITICAL|HIGH" | wc -l
                        ''',
                        returnStdout: true
                    ).trim()
                    
                    echo "📊 NOMBRE DE VULNÉRABILITÉS CRITIQUES: $criticalVulns"
                    
                    if (criticalVulns.toInteger() > 0) {
                        echo "❌❌❌ DÉTECTION DE VULNÉRABILITÉS CRITIQUES ! ❌❌❌"
                        error "🚫 BUILD BLOQUÉ POUR CAUSE DE SÉCURITÉ !"
                    }
                }
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: '*.html, reports/**', fingerprint: true
            junit 'test-results.xml'
        }
        success {
            echo '✅✅✅ PIPELINE RÉUSSI - CODE SÉCURISÉ !'
        }
        failure {
            echo '❌❌❌ PIPELINE ÉCHOUÉ - VULNÉRABILITÉS DÉTECTÉES !'
        }
    }
}