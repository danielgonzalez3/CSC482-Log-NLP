import requests
import os

token = os.environ.get('GITHUB_TOKEN')
headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json',
}
top_java_repos = [
    "google/guava", # 25 most starred repos
    "CyC2018/CS-Notes",
    "Snailclimb/JavaGuide",
    "iluwatar/java-design-patterns",
    "doocs/advanced-java",
    "macrozheng/mall",
    "spring-projects/spring-boot",
    "elastic/elasticsearch",
    "kdn251/interviews",
    "TheAlgorithms/Java",
    "azl397985856/leetcode",
    "google/guava",
    "ReactiveX/RxJava",
    "square/okhttp",
    "youngyangyang04/leetcode-master",
    "square/retrofit",
    "apache/dubbo",
    "apache/spark",
    "skylot/jadx",
    "PhilJay/MPAndroidChart",
    "jeecgboot/jeecg-boot",
    "autonomousapps/dependency-analysis-gradle-plugin", # common gradle plugins
    "modrinth/minotaur",
    "klawson88/liquiprime",
    "klawson88/liquigen",
    "bkmbigo/epit",
    "TanVD/kosogor",
    "kazurayam/inspectus4katalon-gradle-plugin",
    "robertfmurdock/jsmints",
    "steklopod/gradle-ssh-plugin",
    "gesellix/gradle-docker-plugin",
    "steklopod/gradle-ssh-plugin",
    "robertfmurdock/testmints",
    "DanySK/gradle-kotlin-qa",
    "JetBrains/kotlin", # common libs
    "FasterXML/jackson",
    "apache/commons-lang",
    "mockito/mockito",
    "scala/scala",
    "qos-ch/slf4j",
    "junit-team/junit5",
    "junit-team/junit4"
]

def get_workflows(owner, repo):
    url = f'https://api.github.com/repos/{owner}/{repo}/actions/workflows'
    print(url)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['workflows']
    else:
        raise Exception(f"Error fetching workflows: {response.content}")

def get_workflow_runs(owner, repo, workflow_id):
    url = f'https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['workflow_runs']
    else:
        raise Exception(f"Error fetching workflow runs: {response.content}")

def get_run_logs(owner, repo, run_id):
    url = f'https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/logs'
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        with open(f'data/logs_{owner}-{repo}-{run_id}.zip', 'wb') as file:
            for chunk in response.iter_content(chunk_size=128):
                file.write(chunk)
    else:
        raise Exception(f"Error fetching run logs: {response.content}")

def main():
    for java_repo in top_java_repos:
        owner, repo = java_repo.split("/")
        try:
            workflows = get_workflows(owner, repo)
            for workflow in workflows:
                print(f"Workflow: {workflow['name']}")
                
                runs = get_workflow_runs(owner, repo, workflow['id'])
                for run in runs:
                    print(f"  Run id: {run['id']}, Status: {run['status']}")
                    get_run_logs(owner, repo, run['id'])
                    print(f"  Logs downloaded for run id: {run['id']}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
