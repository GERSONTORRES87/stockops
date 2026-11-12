pipeline {
    agent any

    // Revisa GitHub cada 2 minutos; si hay commits nuevos, ejecuta el pipeline
    triggers {
        pollSCM('H/2 * * * *')
    }

    options {
        skipDefaultCheckout()
    }

    environment {
        PROYECTO = 'stockops'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        stage('Dependencias') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Pruebas') {
            steps {
                sh '''
                    . venv/bin/activate
                    mkdir -p reports
                    pytest -v --junitxml=reports/pytest.xml
                '''
            }
        }

        stage('Build imagen') {
            steps {
                sh "docker compose -p ${PROYECTO} build app"
            }
        }

        stage('Deploy') {
            steps {
                sh "docker compose -p ${PROYECTO} up -d"
                sh "docker compose -p ${PROYECTO} ps"
            }
        }

        stage('Verificación') {
            steps {
                sh '''
                    for i in $(seq 1 15); do
                        python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/productos')" && echo "StockOps responde correctamente" && exit 0
                        sleep 2
                    done
                    echo "La aplicacion no responde"
                    exit 1
                '''
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'reports/pytest.xml'
        }
        success {
            echo 'Pipeline exitoso: StockOps desplegado en http://localhost:5000'
        }
        failure {
            echo 'Pipeline fallido: el despliegue NO se realizó'
        }
    }
}
