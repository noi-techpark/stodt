pipeline {
    agent any

	stages {
        stage('Test') {
            steps {
				sh '''
					docker-compose --no-ansi build --pull --build-arg JENKINS_USER_ID=$(id -u jenkins) --build-arg JENKINS_GROUP_ID=$(id -g jenkins)
				'''
				// We do not have a proper test here, so keep this out for now
				// docker-compose --no-ansi test --rm --no-deps -u $(id -u jenkins):$(id -g jenkins) app
            }
        }
    }
}
