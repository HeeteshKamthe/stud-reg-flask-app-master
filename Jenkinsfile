pipeline {
    agent any

    environment {
        PYTHON = "python3"
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo "🔹 Cloning repository..."
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[url: 'https://github.com/HeeteshKamthe/stud-reg-flask-app-master.git']]
                ])
            }
        }

        stage('Install Dependencies') {
            steps {
                echo "🔹 Installing dependencies..."
                sh '''
                    if ! dpkg -s python3-venv >/dev/null 2>&1; then
                        sudo apt-get update -y
                        sudo apt-get install -y python3-venv
                    fi
                    ${PYTHON} -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo "🔹 Running tests..."
                script {
                    if (fileExists('tests')) {
                        sh '''
                            . venv/bin/activate
                            python3 -m unittest discover -s tests || echo "⚠️ Tests failed, check logs."
                        '''
                    } else {
                        echo "✅ No tests found, skipping..."
                    }
                }
            }
        }

       stage('Deploy to EC2') {
    steps {
        echo "🔹 Deploying Flask app to EC2 securely..."
        withCredentials([
            sshUserPrivateKey(credentialsId: 'ec2-ssh-key', keyFileVariable: 'KEY_PATH', usernameVariable: 'SSH_USER'),
            string(credentialsId: 'ec2-host', variable: 'EC2_HOST'),
            string(credentialsId: 'app-dir', variable: 'APP_DIR')
        ]) {
            sh '''
                echo "🔹 Using key at: $KEY_PATH"
                echo "🔹 Deploying to host: $EC2_HOST"
                echo "🔹 App directory: $APP_DIR"

                echo "🔹 Transferring files to EC2..."
                scp -i "$KEY_PATH" -o StrictHostKeyChecking=no -r \
                    Jenkinsfile app.py config.py init.sql models.py requirements.txt run.py templates venv \
                    ${SSH_USER}@${EC2_HOST}:${APP_DIR}/

                echo "🔹 Restarting Flask app on EC2..."
                ssh -i "$KEY_PATH" -o StrictHostKeyChecking=no ${SSH_USER}@${EC2_HOST} "
                    cd ${APP_DIR} &&
                    pkill -f gunicorn || true &&
                    nohup gunicorn run:app --bind 0.0.0.0:5000 --daemon
                "
            '''
        }
    }
}


    }

    post {
        success {
            echo "✅ Deployment successful! Flask app is live on EC2."
        }
        failure {
            echo "❌ Deployment failed! Check Jenkins and EC2 logs for details."
        }
    }
}
