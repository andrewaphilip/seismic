import requests
import sys
import json

# read input - temporarily I manually make a cleaned up json string because the source I'm using produces dirty json
http_string='''{
"jobs":[
        {
            "ip": "10.0.0.1",
            "port": 80,
            "guid": 111,
            "numberOfBlocks": 300
        },
        {
            "ip": "10.0.0.2",
            "port": 8080,
            "guid": 222,
            "numberOfBlocks": 200
        }
        ]   
}'''

data = json.loads(http_string)
#print (type(data))

perpod=128
x=0
for job in data['jobs']:
    x=x+job['numberOfBlocks']
container_count_f=x/perpod #container count is actually pod count in aks
container_count_i=int(container_count_f)
#print(container_count_i)
#print(x)

param='''{
	"$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
	"contentVersion": "1.0.0.0",
	"parameters": {
        "clusterName": {
			"value": "seismic_cluster1"
		},
		"dnsPrefix": {
			"value": "seismic"
        },
        "agentCount": {
			"value": %s
		},
		"linuxAdminUsername": {
			"value": null
		},
		"sshRSAPublicKey": {
			"value": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDnMuSaTJxWGWvmTH+6m8tuh18s4jT0neYNXlrRK1WC+6q6WZEcRQdDjUDKifkzbUFZCWakaFsWDtkTU2sioX4PrlbHgM+N+RXiMvTtKriwy1QnwZzXbNAb+JK8gtTqKdyArCAc4ruju7hjiVOSrtjKoS2FLWQ5C1UQSOoeWCkk/9UgbQ/T5q0nB+XTt9Ybyo2gcJSYo0RUiN/j92cAx7Hirg1agTiXeEGNl1uNOuLA1SzBO1XmvKiY/Ox0bVrPsbu/UaUcCxAD2VdfB/Jm3tC/IkocyWvz8Cc9urduzPEEvs4+OwXESBdrMmySLUfG9L17f3VPAy5KNNguG0J27MA7 plasne@Peters-iMac"
		},
		"servicePrincipalClientId": {
			"value": "99896d62-bbf6-4ccc-b171-adfe366f3c1d"
		},
		"servicePrincipalClientSecret": {
			"value": "HgXKAHST3*C]Riy:T[jHdvh8UpoEss66"
		}
	}
}'''%(container_count_i)
#print(param)

datastore = json.loads(param)
#print(datastore)

with open('azuredeploy.parameters.json', 'w+') as f:
        json.dump(datastore, f, indent=4)

arm='''{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.1",
    "parameters": {
        "clusterName": {
            "type": "string",
            "defaultValue":"aks101cluster",
            "metadata": {
                "description": "The name of the Managed Cluster resource."
            }
        },
        "location": {
            "type": "string",
            "defaultValue": "[resourceGroup().location]",
            "metadata": {
                "description": "The location of the Managed Cluster resource."
            }
        },
        "dnsPrefix": {
            "type": "string",
            "metadata": {
                "description": "Optional DNS prefix to use with hosted Kubernetes API server FQDN."
            }
        },
        "osDiskSizeGB": {
            "type": "int",
            "defaultValue": 30,
            "metadata": {
                "description": "Disk size (in GB) to provision for each of the agent pool nodes. This value ranges from 0 to 1023. Specifying 0 will apply the default disk size for that agentVMSize."
            },
            "minValue": 0,
            "maxValue": 1023
        },
        "agentCount": {
            "type": "int",
            "defaultValue": 3,
            "metadata": {
                "description": "The number of nodes for the cluster."
            },
            "minValue": 1,
            "maxValue": 50
        },
        "agentVMSize": {
            "type": "string",
            "defaultValue": "Standard_F32s_v2",
            "metadata": {
                "description": "The size of the Virtual Machine."
            }
        },
        "linuxAdminUsername": {
            "type": "string",
            "metadata": {
                "description": "User name for the Linux Virtual Machines."
            }
        },
        "sshRSAPublicKey": {
            "type": "string",
            "metadata": {
                "description": "Configure all linux machines with the SSH RSA public key string. Your key should include three parts, for example 'ssh-rsa AAAAB...snip...UcyupgH azureuser@linuxvm'"
            }
        },
        "servicePrincipalClientId": {
            "metadata": {
                "description": "Client ID (used by cloudprovider)"
            },
            "type": "securestring"
        },
        "servicePrincipalClientSecret": {
            "metadata": {
                "description": "The Service Principal Client Secret."
            },
            "type": "securestring"
        },
        "osType": {
            "type": "string",
            "defaultValue": "Linux",
            "allowedValues": [
                "Linux"
            ],
            "metadata": {
                "description": "The type of operating system."
            }
        },
        "kubernetesVersion": {
            "type": "string",
            "defaultValue": "1.14.6",
            "allowedValues": [
                "1.10.13",
                "1.11.10",
                "1.12.8",
                "1.13.10",
                "1.14.6"
            ],
            "metadata": {
                "description": "The version of Kubernetes."
            }
        }
    },
    "resources": [
        {
            "apiVersion": "2018-03-31",
            "type": "Microsoft.ContainerService/managedClusters",
            "location": "[parameters('location')]",
            "name": "[parameters('clusterName')]",
            "properties": {
                "kubernetesVersion": "[parameters('kubernetesVersion')]",
                "dnsPrefix": "[parameters('dnsPrefix')]",
                "agentPoolProfiles": [
                    {
                        "name": "agentpool",
                        "osDiskSizeGB": "[parameters('osDiskSizeGB')]",
                        "count": "[parameters('agentCount')]",
                        "vmSize": "[parameters('agentVMSize')]",
                        "osType": "[parameters('osType')]",
                        "storageProfile": "ManagedDisks"
                    }
                ],
                "linuxProfile": {
                    "adminUsername": "[parameters('linuxAdminUsername')]",
                    "ssh": {
                        "publicKeys": [
                            {
                                "keyData": "[parameters('sshRSAPublicKey')]"
                            }
                        ]
                    }
                },
                "servicePrincipalProfile": {
                    "clientId": "[parameters('servicePrincipalClientId')]",
                    "Secret": "[parameters('servicePrincipalClientSecret')]"
                }
            }
        }
    ],
    "outputs": {
        "controlPlaneFQDN": {
            "type": "string",
            "value": "[reference(parameters('clusterName')).fqdn]"
        }
    }
}'''

datastore = json.loads(arm)
#print(datastore)

with open('azuredeploy.json', 'w+') as f:
        json.dump(datastore, f, indent=4)