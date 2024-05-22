pipeline {
    agent any

    stages {
        stage('build') {
            steps {
                dir("${env.WORKSPACE}/devai-cli") {
                    sh '''
                    apt-get update && apt-get install -y git
                    python3 -m venv ./venv
                    . ./venv/bin/activate
                    ./venv/bin/pip install -r src/requirements.txt
                    ./venv/bin/pip install --editable ./src
                    '''
                    
                    withCredentials([
                            file(credentialsId: 'GOOGLE_APPLICATION_CREDENTIALS', variable: 'GOOGLE_APPLICATION_CREDENTIALS'),
                            string(credentialsId: 'PROJECT_ID', variable: 'PROJECT_ID'),
                            string(credentialsId: 'LOCATION', variable: 'LOCATION'),
                            
                            string(credentialsId: 'GITLAB_PERSONAL_ACCESS_TOKEN', variable: 'GITLAB_PERSONAL_ACCESS_TOKEN'),
                            string(credentialsId: 'GITLAB_URL', variable: 'GITLAB_URL'),
                            string(credentialsId: 'GITLAB_REPOSITORY', variable: 'GITLAB_REPOSITORY'),
                            string(credentialsId: 'GITLAB_BRANCH', variable: 'GITLAB_BRANCH'),
                            string(credentialsId: 'GITLAB_BASE_BRANCH', variable: 'GITLAB_BASE_BRANCH'),
                            
                            string(credentialsId: 'JIRA_API_TOKEN', variable: 'JIRA_API_TOKEN'),
                            string(credentialsId: 'JIRA_USERNAME', variable: 'JIRA_USERNAME'),
                            string(credentialsId: 'JIRA_INSTANCE_URL', variable: 'JIRA_INSTANCE_URL'),
                            string(credentialsId: 'JIRA_PROJECT_KEY', variable: 'JIRA_PROJECT_KEY'),
                            
                            string(credentialsId: 'LANGCHAIN_TRACING_V2', variable: 'LANGCHAIN_TRACING_V2'),
                            string(credentialsId: 'LANGCHAIN_ENDPOINT', variable: 'LANGCHAIN_ENDPOINT'),
                            string(credentialsId: 'LANGCHAIN_API_KEY', variable: 'LANGCHAIN_API_KEY')
                        ]) {    
                            sh '''
                            ./venv/bin/devai review testcoverage -c /bitnami/jenkins/home/workspace/genai-cicd_genai-for-developers/sample-app/src
                            ./venv/bin/devai review code -c /bitnami/jenkins/home/workspace/genai-cicd_genai-for-developers/sample-app/src/main/java/anthos/samples/bankofanthos/balancereader
                            ./venv/bin/devai review performance -c /bitnami/jenkins/home/workspace/genai-cicd_genai-for-developers/sample-app/src/main/java/anthos/samples/bankofanthos/balancereader
                            ./venv/bin/devai review security -c /bitnami/jenkins/home/workspace/genai-cicd_genai-for-developers/sample-app/src/main/java/anthos/samples/bankofanthos/balancereader
                            '''
                            }
                }
            }
        }
    }
}
