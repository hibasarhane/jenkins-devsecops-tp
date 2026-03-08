pipeline {
    agent any
    
    environment {
        // Chemin Python
        PATH = "/usr/local/bin:${env.PATH}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                // Cloner depuis GitHub
               git branch: 'main', 
    url: 'https://github.com/hibasarhane/jenkins-devsecops-tp.git'
                echo '✅ Code récupéré depuis GitHub'
            }
        }
        
        stage('Installer les dépendances') {
            steps {
                sh '''
                    pip3 install -r requirements.txt || true
                    pip3 install pytest safety bandit
                    echo "✅ Dépendances installées"
                '''
            }
        }
        
        stage('Tests unitaires') {
            steps {
                sh '''
                    pytest test_app.py -v --junitxml=test-results.xml
                    echo "✅ Tests exécutés"
                '''
            }
        }
        
        stage('Scan SAST - Bandit') {
            steps {
                sh '''
                    bandit -r . -f html -o bandit-report.html || true
                    echo "✅ Scan SAST terminé"
                '''
            }
        }
        
        stage('Scan SCA - Safety') {
            steps {
                sh '''
                    safety check --full-report || true
                    echo "✅ Scan Safety terminé"
                '''
            }
        }
        
        stage('Scan SCA - OWASP') {
            steps {
                sh '''
                    mkdir -p reports
                    if command -v dependency-check.sh &> /dev/null; then
                        dependency-check.sh --scan . --format HTML --out reports/ --project "TP-Jenkins-GitHub" || true
                        echo "✅ Scan OWASP terminé"
                    else
                        echo "⚠️ OWASP non installé"
                    fi
                '''
            }
        }
        
        stage('Analyse des vulnérabilités') {
            steps {
                script {
                    // Vérifier les vulnérabilités critiques
                    def criticalVulns = sh(
                        script: 'safety check --bare | grep -i "critical" | wc -l',
                        returnStdout: true
                    ).trim()
                    
                    if (criticalVulns.toInteger() > 0) {
                        echo "❌ CRITIQUE: $criticalVulns vulnérabilités critiques détectées!"
                        // Décommentez la ligne suivante pour bloquer le build
                        // error "Build bloqué pour cause de vulnérabilités critiques"
                    } else {
                        echo "✅ Aucune vulnérabilité critique détectée"
                    }
                }
            }
        }
    }
    
    post {
        always {
            // Archiver les rapports
            archiveArtifacts artifacts: '*.html, reports/**', fingerprint: true
            junit 'test-results.xml'
            echo "📊 Rapports archivés"
        }
        success {
            echo '✅✅✅ PIPELINE RÉUSSI ! ✅✅✅'
        }
        failure {
            echo '❌❌❌ PIPELINE ÉCHOUÉ ! ❌❌❌'
        }
    }
}