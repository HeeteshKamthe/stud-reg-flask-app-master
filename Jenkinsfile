pipeline {
    agent any

    environment {
        PYTHON = "python3"
        DB_USER = "flaskuser"
        DB_PASSWORD = "flask123"   // change this to a strong password
        DB_NAME = "student_db"
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
                        sudo yum install python3 -y
                        sudo apt-get install -y python3-venv
                        sudo yum install python3-pip -y
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
                        echo "No tests found, skipping..."
                    }
                }
            }
        }

        
stage('Setup Database') {
    steps {
        echo "🔹 Installing MariaDB and setting up database..."
        withCredentials([
            string(credentialsId: 'ec2-host', variable: 'EC2_HOST'),
            sshUserPrivateKey(credentialsId: 'ec2-ssh-key', keyFileVariable: 'KEY_PATH', usernameVariable: 'SSH_USER')
        ]) {
            sh """
ssh -o StrictHostKeyChecking=no -i "$KEY_PATH" ${SSH_USER}@${EC2_HOST} 'bash -s' <<'ENDSSH'
echo "🔹 Installing MariaDB..."
sudo yum install -y mariadb105-server
sudo systemctl start mariadb
sudo systemctl enable mariadb

echo "🔹 Creating database, user, and table..."
sudo mysql <<MYSQL_SCRIPT
CREATE DATABASE IF NOT EXISTS student_db;
CREATE USER IF NOT EXISTS 'flaskuser'@'localhost' IDENTIFIED BY 'flask123';
GRANT ALL PRIVILEGES ON student_db.* TO 'flaskuser'@'localhost';
FLUSH PRIVILEGES;
USE student_db;
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    course VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
MYSQL_SCRIPT

echo "Database, user, and table setup completed."
ENDSSH
            """
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

                echo "🔹 Installing dependencies and restarting app on EC2..."
                ssh -o StrictHostKeyChecking=no -i "$KEY_PATH" ${SSH_USER}@${EC2_HOST} "
                    cd ${APP_DIR} &&
                    sudo yum install python3 python3-venv -y 
                    sudo yum install python3-pip -y
                    source venv/bin/activate &&
                    pip install -r requirements.txt &&
                    pip install gunicorn &&
                    pkill gunicorn || true &&
                    nohup gunicorn run:app --bind 0.0.0.0:5000 --daemon
                "
            '''
        }
    }
}


    }

    post {
        success {
            echo " Deployment successful! Flask app is live on EC2."
        }
        failure {
            echo " Deployment failed! Check Jenkins and EC2 logs for details."
        }
    }
}
