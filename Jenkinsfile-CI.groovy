pipeline {
    agent any

	stages {
        stage('Test') {
            steps {
				sh '''
					docker-compose --no-ansi build --pull --build-arg JENKINS_USER_ID=$(id -u jenkins) --build-arg JENKINS_GROUP_ID=$(id -g jenkins)
					docker-compose --no-ansi run --rm --no-deps -u $(id -u jenkins):$(id -g jenkins) app "bash start.sh"
				'''
            }
        }
    }
}
