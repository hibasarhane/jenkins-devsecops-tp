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
                    # Créer un environnement virtuel pour éviter les problèmes de permission
                    python3 -m venv venv
                    
                    # Activer l'environnement virtuel
                    . venv/bin/activate
                    
                    # Mettre à jour pip
                    pip install --upgrade pip
                    
                    # Installer les dépendances avec gestion des conflits
                    pip install -r requirements.txt || true
                    pip install pytest safety bandit
                    
                    echo "✅ Dépendances installées dans environnement virtuel"
                '''
            }
        }
        
        stage('Tests unitaires') {
            steps {
                sh '''
                    # Activer l'environnement virtuel
                    . venv/bin/activate
                    
                    # Exécuter les tests
                    pytest test_app.py -v --junitxml=test-results.xml
                    echo "✅ Tests exécutés"
                '''
            }
        }
        
        stage('Scan SAST - Bandit') {
            steps {
                sh '''
                    # Activer l'environnement virtuel
                    . venv/bin/activate
                    
                    # Exécuter Bandit
                    bandit -r . -f html -o bandit-report.html || true
                    echo "✅ Scan SAST terminé"
                '''
            }
        }
        
        stage('Scan SCA - Safety') {
            steps {
                sh '''
                    # Activer l'environnement virtuel
                    . venv/bin/activate
                    
                    # Exécuter Safety
                    safety check --full-report || true
                    echo "✅ Scan Safety terminé"
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
                        // URL correcte de SonarQube
                        def sonarUrl = "http://172.17.0.1:9000"
                        def projectKey = "TP-Jenkins-Security"
                        
                        echo "🔍 Vérification du Quality Gate sur ${sonarUrl}"
                        
                        // Attendre que l'analyse soit terminée
                        sleep 10
                        
                        // Récupérer l'ID de la tâche
                        def taskId = sh(
                            script: """
                                curl -s '${sonarUrl}/api/ce/component?component=${projectKey}' | \
                                grep -o '"id":"[^"]*"' | \
                                head -1 | \
                                cut -d'"' -f4
                            """,
                            returnStdout: true
                        ).trim()
                        
                        if (taskId) {
                            echo "✅ Tâche trouvée: ${taskId}"
                            
                            // Vérifier le statut
                            def status = sh(
                                script: "curl -s '${sonarUrl}/api/ce/task?id=${taskId}' | grep -o '"status":"[^"]*"' | cut -d'"' -f4",
                                returnStdout: true
                            ).trim()
                            
                            echo "📊 Statut de la tâche: ${status}"
                            
                            // Récupérer le résultat du Quality Gate
                            def qualityGate = sh(
                                script: "curl -s '${sonarUrl}/api/qualitygates/project_status?projectKey=${projectKey}' | grep -o '"status":"[^"]*"' | head -1 | cut -d'"' -f4",
                                returnStdout: true
                            ).trim()
                            
                            echo "🏁 Quality Gate: ${qualityGate}"
                            
                            if (qualityGate == "ERROR") {
                                error "❌ Quality Gate échoué!"
                            } else if (qualityGate == "OK") {
                                echo "✅ Quality Gate réussi!"
                            } else {
                                echo "⚠️ Quality Gate: ${qualityGate}"
                            }
                        } else {
                            echo "⚠️ Aucune tâche trouvée, vérification manuelle nécessaire"
                        }
                    }
                }
            }
        }
        
        stage('Scan SCA - OWASP') {
            steps {
                sh '''
                    # Activer l'environnement virtuel (optionnel pour OWASP)
                    . venv/bin/activate
                    
                    # Exécuter OWASP Dependency Check
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
                        script: '''
                            . venv/bin/activate
                            safety check --bare | grep -i "critical" | wc -l
                        ''',
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