#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import requests
import random

LITMUS_URL = 'http://a0cec0471be1f4a72a704107aafef009-1177770021.us-east-1.elb.amazonaws.com:9091'
LITMUS_USERNAME = 'admin'
LITMUS_PASSWORD = 'litmus'
LITMUS_PROJECT_ID = 'acc81825-c526-47de-af04-8b8cf8547244'
LITMUS_CLUSTER_ID = '3eb02947-4acf-49e1-ae69-e8a5ce9e9149'
POD_DELETE_NAMESPACE = 'default'
POD_DELETE_DEPLOYMENT = 'nginx-deployment'

# def get_cluster_id():
#     response = get_auth_token()
#     access_token = response.json()['access_token']

#     headers = {'authorization': access_token, 'Content-type': 'application/json'}
#     data = {
#         "operationName": "getClusters",
#         "variables": {
#             "project_id": LITMUS_PROJECT_ID
#         },
#         "query": "query getClusters($project_id: String!, $cluster_type: String) {\n  getCluster(project_id: $project_id, cluster_type: $cluster_type) {\n    cluster_id\n    cluster_name\n    description\n    is_active\n    is_registered\n    is_cluster_confirmed\n    updated_at\n    created_at\n    cluster_type\n    no_of_schedules\n    no_of_workflows\n    token\n    last_workflow_timestamp\n    agent_namespace\n    agent_scope\n    version\n    __typename\n  }\n}\n"
#     }
#     response = requests.post(LITMUS_URL + '/api/query', data=json.dumps(data), headers=headers)
#     return response
#     cluster_id = response.json()['data']['getCluster'][0]['cluster_id']
#     return cluster_id

def get_auth_token():
    cred_data = {'username': LITMUS_USERNAME,
                 'password': LITMUS_PASSWORD}
    response = requests.post(LITMUS_URL + '/auth/login',
                             json.dumps(cred_data))
    return response

############################################

def get_random_number():
    return random.randint(99, 99999999).__str__()

############################################


def execute_pod_kill_experiment():
    response = get_auth_token()

    access_token = response.json()['access_token']
    # print(access_token)

    headers = {'authorization': access_token,
               'Content-type': 'application/json'}

    workflow_name = 'pod-kill-workflow-' + get_random_number()
    json_data = get_pod_kill_request_body(workflow_name, POD_DELETE_NAMESPACE, POD_DELETE_DEPLOYMENT)
    # print(json_data)
    
    pod_kill_response = requests.post(LITMUS_URL + '/api/query', data=json_data, headers=headers)
    print(pod_kill_response.json())
    print(pod_kill_response.status_code)

####################################################
def get_pod_kill_request_body(workflow_name, namespace, deployment):
    project_id = LITMUS_PROJECT_ID
    cluster_id = LITMUS_CLUSTER_ID
    isCustomWorkflow = bool(True)

    data = {
      "operationName": "createChaosWorkFlow",
      "variables": {
          "request": {
              "workflowManifest": "{\n  \"apiVersion\": \"argoproj.io/v1alpha1\",\n  \"kind\": \"Workflow\",\n  \"metadata\": {\n    \"name\": \"updated_workflow_name\",\n    \"namespace\": \"litmus\",\n    \"labels\": {\n      \"subject\": \"custom-chaos-workflow_litmus\"\n    }\n  },\n  \"spec\": {\n    \"arguments\": {\n      \"parameters\": [\n        {\n          \"name\": \"adminModeNamespace\",\n          \"value\": \"litmus\"\n        }\n      ]\n    },\n    \"entrypoint\": \"custom-chaos\",\n    \"securityContext\": {\n      \"runAsNonRoot\": true,\n      \"runAsUser\": 1000\n    },\n    \"serviceAccountName\": \"argo-chaos\",\n    \"templates\": [\n      {\n        \"name\": \"custom-chaos\",\n        \"steps\": [\n          [\n            {\n              \"name\": \"install-chaos-experiments\",\n              \"template\": \"install-chaos-experiments\"\n            }\n          ],\n          [\n            {\n              \"name\": \"pod-delete-zqn\",\n              \"template\": \"pod-delete-zqn\"\n            }\n          ],\n          [\n            {\n              \"name\": \"revert-chaos\",\n              \"template\": \"revert-chaos\"\n            }\n          ]\n        ]\n      },\n      {\n        \"name\": \"install-chaos-experiments\",\n        \"inputs\": {\n          \"artifacts\": [\n            {\n              \"name\": \"pod-delete-zqn\",\n              \"path\": \"/tmp/pod-delete-zqn.yaml\",\n              \"raw\": {\n                \"data\": \"apiVersion: litmuschaos.io/v1alpha1\\ndescription:\\n  message: |\\n    Deletes a pod belonging to a deployment/statefulset/daemonset\\nkind: ChaosExperiment\\nmetadata:\\n  name: pod-delete\\n  labels:\\n    name: pod-delete\\n    app.kubernetes.io/part-of: litmus\\n    app.kubernetes.io/component: chaosexperiment\\n    app.kubernetes.io/version: 2.9.0\\nspec:\\n  definition:\\n    scope: Namespaced\\n    permissions:\\n      - apiGroups:\\n          - \\\"\\\"\\n        resources:\\n          - pods\\n        verbs:\\n          - create\\n          - delete\\n          - get\\n          - list\\n          - patch\\n          - update\\n          - deletecollection\\n      - apiGroups:\\n          - \\\"\\\"\\n        resources:\\n          - events\\n        verbs:\\n          - create\\n          - get\\n          - list\\n          - patch\\n          - update\\n      - apiGroups:\\n          - \\\"\\\"\\n        resources:\\n          - configmaps\\n        verbs:\\n          - get\\n          - list\\n      - apiGroups:\\n          - \\\"\\\"\\n        resources:\\n          - pods/log\\n        verbs:\\n          - get\\n          - list\\n          - watch\\n      - apiGroups:\\n          - \\\"\\\"\\n        resources:\\n          - pods/exec\\n        verbs:\\n          - get\\n          - list\\n          - create\\n      - apiGroups:\\n          - apps\\n        resources:\\n          - deployments\\n          - statefulsets\\n          - replicasets\\n          - daemonsets\\n        verbs:\\n          - list\\n          - get\\n      - apiGroups:\\n          - apps.openshift.io\\n        resources:\\n          - deploymentconfigs\\n        verbs:\\n          - list\\n          - get\\n      - apiGroups:\\n          - \\\"\\\"\\n        resources:\\n          - replicationcontrollers\\n        verbs:\\n          - get\\n          - list\\n      - apiGroups:\\n          - argoproj.io\\n        resources:\\n          - rollouts\\n        verbs:\\n          - list\\n          - get\\n      - apiGroups:\\n          - batch\\n        resources:\\n          - jobs\\n        verbs:\\n          - create\\n          - list\\n          - get\\n          - delete\\n          - deletecollection\\n      - apiGroups:\\n          - litmuschaos.io\\n        resources:\\n          - chaosengines\\n          - chaosexperiments\\n          - chaosresults\\n        verbs:\\n          - create\\n          - list\\n          - get\\n          - patch\\n          - update\\n          - delete\\n    image: litmuschaos/go-runner:2.9.0\\n    imagePullPolicy: Always\\n    args:\\n      - -c\\n      - ./experiments -name pod-delete\\n    command:\\n      - /bin/bash\\n    env:\\n      - name: TOTAL_CHAOS_DURATION\\n        value: \\\"15\\\"\\n      - name: RAMP_TIME\\n        value: \\\"\\\"\\n      - name: FORCE\\n        value: \\\"true\\\"\\n      - name: CHAOS_INTERVAL\\n        value: \\\"5\\\"\\n      - name: PODS_AFFECTED_PERC\\n        value: \\\"\\\"\\n      - name: LIB\\n        value: litmus\\n      - name: TARGET_PODS\\n        value: \\\"\\\"\\n      - name: NODE_LABEL\\n        value: \\\"\\\"\\n      - name: SEQUENCE\\n        value: parallel\\n    labels:\\n      name: pod-delete\\n      app.kubernetes.io/part-of: litmus\\n      app.kubernetes.io/component: experiment-job\\n      app.kubernetes.io/version: 2.9.0\\n\"\n              }\n            }\n          ]\n        },\n        \"container\": {\n          \"args\": [\n            \"kubectl apply -f /tmp/pod-delete-zqn.yaml -n {{workflow.parameters.adminModeNamespace}} |  sleep 30\"\n          ],\n          \"command\": [\n            \"sh\",\n            \"-c\"\n          ],\n          \"image\": \"litmuschaos/k8s:2.9.0\"\n        }\n      },\n      {\n        \"name\": \"pod-delete-zqn\",\n        \"inputs\": {\n          \"artifacts\": [\n            {\n              \"name\": \"pod-delete-zqn\",\n              \"path\": \"/tmp/chaosengine-pod-delete-zqn.yaml\",\n              \"raw\": {\n                \"data\": \"apiVersion: litmuschaos.io/v1alpha1\\nkind: ChaosEngine\\nmetadata:\\n  namespace: \\\"{{workflow.parameters.adminModeNamespace}}\\\"\\n  generateName: pod-delete-zqn\\n  labels:\\n    instance_id: 0a88efa2-c9fd-4342-ac9d-261e8303d079\\n    workflow_name: updated_workflow_name\\nspec:\\n  appinfo:\\n    appns: default\\n    applabel: app=nginx\\n    appkind: deployment\\n  engineState: active\\n  chaosServiceAccount: litmus-admin\\n  experiments:\\n    - name: pod-delete\\n      spec:\\n        components:\\n          env:\\n            - name: TOTAL_CHAOS_DURATION\\n              value: \\\"30\\\"\\n            - name: CHAOS_INTERVAL\\n              value: \\\"10\\\"\\n            - name: FORCE\\n              value: \\\"false\\\"\\n            - name: PODS_AFFECTED_PERC\\n              value: \\\"\\\"\\n\"\n              }\n            }\n          ]\n        },\n        \"container\": {\n          \"args\": [\n            \"-file=/tmp/chaosengine-pod-delete-zqn.yaml\",\n            \"-saveName=/tmp/engine-name\"\n          ],\n          \"image\": \"litmuschaos/litmus-checker:2.9.0\"\n        }\n      },\n      {\n        \"name\": \"revert-chaos\",\n        \"container\": {\n          \"image\": \"litmuschaos/k8s:2.9.0\",\n          \"command\": [\n            \"sh\",\n            \"-c\"\n          ],\n          \"args\": [\n            \"kubectl delete chaosengine -l 'instance_id in (0a88efa2-c9fd-4342-ac9d-261e8303d079, )' -n {{workflow.parameters.adminModeNamespace}} \"\n          ]\n        }\n      }\n    ],\n    \"podGC\": {\n      \"strategy\": \"OnWorkflowCompletion\"\n    }\n  }\n}",
              "cronSyntax": "",
              "workflowName": "updated_workflow_name",
              "workflowDescription": "Custom Chaos Workflow",
              "isCustomWorkflow": isCustomWorkflow,
              "weightages": [
                  {
                      "experimentName": "pod-delete-zqn",
                      "weightage": 10
                  }
              ],
              "projectID": "acc81825-c526-47de-af04-8b8cf8547244",
              "clusterID": "3eb02947-4acf-49e1-ae69-e8a5ce9e9149"
          }
      },
      "query": "mutation createChaosWorkFlow($request: ChaosWorkFlowRequest!) {\n  createChaosWorkFlow(request: $request) {\n    workflowID\n    cronSyntax\n    workflowName\n    workflowDescription\n    isCustomWorkflow\n    __typename\n  }\n}\n"
    }

    # replacing values
    updated_workflow_manifest_str = data['variables']['request']['workflowManifest'].replace(
        'updated_workflow_name', workflow_name).replace('updated_namespace', namespace).replace('updated_deployment',
                                                                                                deployment)
    updated_workflow_name_str = data['variables']['request']['workflowName'].replace(
        'updated_workflow_name', workflow_name)
    project_id_str = data['variables']['request']['projectID'].replace('updated_project_id', project_id)
    cluster_id_str = data['variables']['request']['clusterID'].replace('updated_cluster_id', cluster_id)

    # Inserting updated values
    data['variables']['request']['workflowManifest'] = updated_workflow_manifest_str
    data['variables']['request']['workflowName'] = updated_workflow_name_str
    data['variables']['request']['projectID'] = project_id_str
    data['variables']['request']['clusterID'] = cluster_id_str

    return json.dumps(data)

#######################################################
if __name__ == '__main__':
    execute_pod_kill_experiment()
    # print (get_cluster_id());