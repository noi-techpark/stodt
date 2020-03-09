pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID = credentials('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
		DOCKER_PROJECT_NAME = "davinci-stodt"
		DOCKER_SERVER_URL = "docker02.testingmachine.eu"
        DOCKER_SERVER_DIRECTORY = "/var/docker/davinci-stodt"
		DOCKER_IMAGE = '755952719952.dkr.ecr.eu-west-1.amazonaws.com/davinci-stodt'
		DOCKER_TAG = "test-$BUILD_NUMBER"
		HOST = "https://stodt.davinci.testingmachine.eu"
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
					echo 'HOST=${HOST}' >> .env
				"""
            }
        }
        stage('Test') {
            steps {
				sh '''
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
					    ssh -o StrictHostKeyChecking=no ${DOCKER_SERVER_URL} bash -euc "'
							mkdir -p ${DOCKER_SERVER_DIRECTORY}
							ls -1t ${DOCKER_SERVER_DIRECTORY}/releases/ | tail -n +10 | grep -v `readlink -f ${DOCKER_SERVER_DIRECTORY}/current | xargs basename --` -- | xargs -r printf \"${DOCKER_SERVER_DIRECTORY}/releases/%s\\n\" | xargs -r rm -rf --
							mkdir -p ${DOCKER_SERVER_DIRECTORY}/releases/${BUILD_NUMBER}
						'"

						scp -o StrictHostKeyChecking=no docker-compose.run.yml ${DOCKER_SERVER_URL}:${DOCKER_SERVER_DIRECTORY}/releases/${BUILD_NUMBER}/docker-compose.yml
						scp -o StrictHostKeyChecking=no .env ${DOCKER_SERVER_URL}:${DOCKER_SERVER_DIRECTORY}/releases/${BUILD_NUMBER}/.env

						ssh -o StrictHostKeyChecking=no ${DOCKER_SERVER_URL} bash -euc "'
							AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" aws ecr get-login --region eu-west-1 --no-include-email | bash
							cd ${DOCKER_SERVER_DIRECTORY}/releases/${BUILD_NUMBER} && docker-compose --no-ansi pull
							[ -d \"${DOCKER_SERVER_DIRECTORY}/current\" ] && (cd ${DOCKER_SERVER_DIRECTORY}/current && docker-compose --no-ansi down) || true
							ln -sfn ${DOCKER_SERVER_DIRECTORY}/releases/${BUILD_NUMBER} ${DOCKER_SERVER_DIRECTORY}/current
							cd ${DOCKER_SERVER_DIRECTORY}/current && docker-compose --no-ansi up --detach
						'"
					"""
                }
            }
        }
    }
}
