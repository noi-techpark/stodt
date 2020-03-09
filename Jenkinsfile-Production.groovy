pipeline {
    agent any

    environment {
		AWS_ACCESS_KEY_ID = credentials('AWS_ACCESS_KEY_ID')
		AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
		DOCKER_PROJECT_NAME = "davinci-stodt"
		DOCKER_IMAGE = '755952719952.dkr.ecr.eu-west-1.amazonaws.com/davinci-stodt'
		DOCKER_TAG = "prod-$BUILD_NUMBER"
		SERVER_PORT = "1040"

		HOST = "https://stodt.davinci.bz.it"
    }

	stages {
        stage('Configure') {
            steps {
                sh """
					rm -f .env
					cp .env.example .env
					echo 'COMPOSE_PROJECT_NAME=${DOCKER_PROJECT_NAME}' >> .env
					echo 'DOCKER_IMAGE=${DOCKER_IMAGE}' >> .env
					echo 'DOCKER_TAG=${DOCKER_TAG}' >> .env
					echo 'SERVER_PORT=${SERVER_PORT}' >> .env

					echo 'HOST=${HOST}' >> .env
				"""
            }
        }

        stage('Test') {
            steps {
				sh '''
                    docker network create authentication || true
					docker-compose --no-ansi build --pull --build-arg JENKINS_USER_ID=$(id -u jenkins) --build-arg JENKINS_GROUP_ID=$(id -g jenkins)
				'''
				// We do not have a proper test here, so keep this out for now
				// docker-compose --no-ansi test --rm --no-deps -u $(id -u jenkins):$(id -g jenkins) app
            }
        }
		stage('Build') {
            steps {
				sh '''
					aws ecr get-login --region eu-west-1 --no-include-email | bash
					docker-compose --no-ansi -f docker-compose.build.yml build --pull
					docker-compose --no-ansi -f docker-compose.build.yml push
				'''
            }
        }
		stage('Deploy') {
            steps {
               sshagent(['jenkins-ssh-key']) {
                    sh """
						ansible-galaxy install --force -r ansible/requirements.yml
						ansible-playbook --limit=docker02.opendatahub.bz.it ansible/deploy.yml --extra-vars "build_number=${BUILD_NUMBER}"
					"""
                }
            }
        }
    }
}
