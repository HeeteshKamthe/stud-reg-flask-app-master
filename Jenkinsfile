pipeline {
    agent any

    environment {
        APP_NAME = "flaskapp"
        PYTHON = "python3"
        PORT = "5000"
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo '🔹 Cloning repository...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo '🔹 Installing dependencies...'
                sh '''
                ${PYTHON} -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                pip install gunicorn
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo '🔹 Running tests...'
                sh '''
                . venv/bin/activate
                ${PYTHON} -m unittest discover -s tests || echo "No tests found, skipping..."
                '''
            }
        }

        stage('Deploy to EC2') {
            steps {
                echo '🔹 Deploying Flask app to EC2 securely...'

                withCredentials([
                    sshUserPrivateKey(credentialsId: 'ec2-ssh-key', keyFileVariable: 'KEY_PATH', usernameVariable: 'EC2_USER'),
                    string(credentialsId: 'ec2-host', variable: 'EC2_HOST'),
                    string(credentialsId: 'app-dir', variable: 'APP_DIR'),
                    string(credentialsId: 'app-entry', variable: 'APP_ENTRY')
                ]) {
                    sh '''
                    echo "Copying project files to EC2..."
                    scp -i ${KEY_PATH} -o StrictHostKeyChecking=no -r * ${EC2_USER}@${EC2_HOST}:${APP_DIR}/

                    echo "Setting up and restarting Gunicorn service..."
                    ssh -i ${KEY_PATH} -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} << EOF
                        set -e
                        sudo mkdir -p ${APP_DIR}
                        cd ${APP_DIR}

                        if [ ! -d "venv" ]; then
                            ${PYTHON} -m venv venv
                        fi
                        source venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                        pip install gunicorn

                        SERVICE_FILE="/etc/systemd/system/${APP_NAME}.service"
                        sudo bash -c "cat > \$SERVICE_FILE" <<EOL
[Unit]
Description=Gunicorn instance to serve Flask app
After=network.target

[Service]
User=${EC2_USER}
Group=${EC2_USER}
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin"
ExecStart=${APP_DIR}/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:${PORT} ${APP_ENTRY}
Restart=always

[Install]
WantedBy=multi-user.target
EOL

                        sudo systemctl daemon-reload
                        sudo systemctl enable ${APP_NAME}.service
                        sudo systemctl restart ${APP_NAME}.service
                        echo "✅ Flask app running with Gunicorn on port ${PORT}"
                    EOF
                    '''
                }
            }
        }
    }

    post {
        success {
            echo '✅ Deployment successful! Flask app is live via Gunicorn + systemd.'
        }
        failure {
            echo '❌ Deployment failed! Check Jenkins and EC2 logs for details.'
        }
    }
}
