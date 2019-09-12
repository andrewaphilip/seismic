import requests
import sys
import json

#this should not poll at any interval but rather be a decisive batch job as this is a single file
r=requests.get('https://jsonplaceholder.typicode.com/todos/1')
c=r.content
s=str(c)
#mata = json.loads(s)
#for job in mata['jobs']:
#    print(job['block_size'])

# read input - temporarily I manually make a cleaned up json string because the source I'm using produces dirty json
http_string='''{
"jobs":[
        {
            "ip": "10.0.0.1",
            "port": 80,
            "guid": 111,
            "blocks": 1000
        },
        {
            "ip": "10.0.0.2",
            "port": 8080,
            "guid": 222,
            "blocks": 280
        }
        ]   
}'''

data = json.loads(http_string)
#print (type(data))

percontainer=128
x=0
for job in data['jobs']:
    x=x+job['blocks']
container_count_f=x/percontainer
container_count_i=int(container_count_f)
#print(container_count_i)
#print(x)

v=""
namecount = 0
while container_count_i > 0:
    namecount = namecount + 1
    v=v+'''"containername%s": {
      "type": "string",
      "metadata": {
        "description": "Name for the container"
        }
      },'''%(namecount)
    container_count_i=container_count_i-1

container_count_i=int(container_count_f)
#print(container_count_i)
r=""
namecount2 = 0
while container_count_i > 0:
  if container_count_i == 1:
    namecount2 = namecount2 + 1
    r=r+'''{
                        "name": "[parameters('containername%s')]",
                        "properties": {
                            "command": [
                                "bin/bash",
                                "-c",
                                "while sleep 5; do cat /mnt/input/access.log; done"
                            ],
                            "image": "[parameters('image')]",
                            "ports": [
                                      {
                                        "port": "[parameters('port')]"
                                      }
                                    ],
                            "resources": {
                                "requests": {
                                    "cpu": "[parameters('cpuCores')]",
                                    "memoryInGb": "[parameters('memoryInGb')]"
                                }
                            },
                            "volumeMounts": [
                                {
                                    "name": "[parameters('volumename')]",
                                    "mountPath": "/mnt/input",
                                    "readOnly": false
                                }
                            ]
                        }
                    }'''%(namecount2)
    container_count_i=container_count_i-1
  else:
      namecount2 = namecount2 + 1
      r=r+'''{
                        "name": "[parameters('containername%s')]",
                        "properties": {
                            "command": [
                                "bin/bash",
                                "-c",
                                "while sleep 5; do cat /mnt/input/access.log; done"
                            ],
                            "image": "[parameters('image')]",
                            "resources": {
                                "requests": {
                                    "cpu": "[parameters('cpuCores')]",
                                    "memoryInGb": "[parameters('memoryInGb')]"
                                }
                            },
                            "volumeMounts": [
                                {
                                    "name": "[parameters('volumename')]",
                                    "mountPath": "/mnt/input",
                                    "readOnly": false
                                }
                            ]
                        }
                    },'''%(namecount2)
      container_count_i=container_count_i-1

#print(r)


armsection1='''{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
      "containergroupname": {
        "type": "string",
        "metadata": {
          "description": "Name for the container group"
        }
      },'''

armsection2='''"volumename": {
        "type": "string",
        "metadata": {
          "description": "Name for the emptyDir volume"
        }
      },
      "image": {
        "type": "string",
        "metadata": {
          "description": "Container image to deploy. Should be of the form accountName/imagename[:tag] for images stored in Docker Hub or a fully qualified URI for a private registry like the Azure Container Registry."
        },
        "defaultValue": "centos:latest"
      },
      "port": {
        "type": "string",
        "metadata": {
          "description": "Port to open on the container and the public IP address."
        },
        "defaultValue": "80"
      },
      "cpuCores": {
        "type": "string",
        "metadata": {
          "description": "The number of CPU cores to allocate to the container."
        },
        "defaultValue": "1.0"
      },
      "memoryInGb": {
        "type": "string",
        "metadata": {
          "description": "The amount of memory to allocate to the container in gigabytes."
        },
        "defaultValue": "1.5"
      },
      "location": {
        "type": "string",
        "defaultValue": "[resourceGroup().location]",
        "metadata": {
          "description": "Location for all resources."
        }
      }
    },
    "variables": {},
    "resources": [
      {
        "name": "[parameters('containergroupname')]",
        "type": "Microsoft.ContainerInstance/containerGroups",
        "apiVersion": "2017-10-01-preview",
        "location": "[parameters('location')]",
        "properties": {
          "containers": ['''
          
armsection3='''
          ],
          "osType": "Linux",
          "ipAddress": {
            "type": "Public",
            "ports": [
              {
                "protocol": "TCP",
                "port": "[parameters('port')]"
              }
            ]
          },
          "volumes": [
            {
              "name": "[parameters('volumename')]",
              "emptyDir": {}
            }
          ]
        }
      }
    ],
    "outputs": {
      "containerIPv4Address": {
        "type": "string",
        "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', parameters('containergroupname'))).ipAddress.ip]"
      }
    }
  }'''

arm = armsection1 + v + armsection2 + r + armsection3
#print(arm)

datastore = json.loads(arm)
#print(datastore)

with open('azuredeploy.json', 'w+') as f:
        json.dump(datastore, f, indent=4)

paramSection1 = '''{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
      "containergroupname": {
        "value": "processorContainers"
      },'''

#build parameters file
z=""
namecount3 = 0
container_count_i=int(container_count_f)
while container_count_i > 0:
    namecount3 = namecount3 + 1
    z=z+'''"containername%s": {
      "value": "container%s",
      "metadata": {
        "description": "Name for the container"
        }
      },'''%(namecount3,namecount3)
    container_count_i=container_count_i-1

paramSection2 = '''"volumename": {
        "value": "sharedvolume"
      }
    }
}'''

param = paramSection1 + z + paramSection2
#print(param)

datastore = json.loads(param)
#print(datastore)

with open('azuredeploy.parameters.json', 'w+') as f:
        json.dump(datastore, f, indent=4)