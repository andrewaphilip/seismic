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

arm='''{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "resourceName": {
            "type": "string",
            "metadata": {
                "description": "The name of the Managed Cluster resource."
            }
        },
        "location": {
            "type": "string",
            "metadata": {
                "description": "The location of AKS resource."
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
                "description": "Disk size (in GiB) to provision for each of the agent pool nodes. This value ranges from 0 to 1023. Specifying 0 will apply the default disk size for that agentVMSize."
            },
            "minValue": 0,
            "maxValue": 1023
        },
        "agentCount": {
            "type": "int",
            "defaultValue": 3,
            "metadata": {
                "description": "The number of agent nodes for the cluster."
            },
            "minValue": 1,
            "maxValue": 50
        },
        "agentVMSize": {
            "type": "string",
            "defaultValue": "Standard_D2_v2",
            "metadata": {
                "description": "The size of the Virtual Machine."
            }
        },
        "servicePrincipalClientId": {
            "metadata": {
                "description": "Client ID (used by cloudprovider)."
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
            "defaultValue": "1.7.7",
            "metadata": {
                "description": "The version of Kubernetes."
            }
        },
        "networkPlugin": {
            "type": "string",
            "allowedValues": [
                "azure",
                "kubenet"
            ],
            "metadata": {
                "description": "Network plugin used for building Kubernetes network."
            }
        },
        "maxPods": {
            "type": "int",
            "defaultValue": 30,
            "metadata": {
                "description": "Maximum number of pods that can run on a node."
            }
        },
        "enableRBAC": {
            "type": "bool",
            "defaultValue": true,
            "metadata": {
                "description": "Boolean flag to turn on and off of RBAC."
            }
        },
        "vmssNodePool": {
            "type": "bool",
            "defaultValue": false,
            "metadata": {
                "description": "Boolean flag to turn on and off of VM scale sets"
            }
        },
        "windowsProfile": {
            "type": "bool",
            "defaultValue": false,
            "metadata": {
                "description": "Boolean flag to turn on and off of VM scale sets"
            }
        },
        "enableHttpApplicationRouting": {
            "type": "bool",
            "defaultValue": true,
            "metadata": {
                "description": "Boolean flag to turn on and off of http application routing."
            }
        },
        "vnetSubnetID": {
            "type": "string",
            "metadata": {
                "description": "Resource ID of virtual network subnet used for nodes and/or pods IP assignment."
            }
        },
        "serviceCidr": {
            "type": "string",
            "metadata": {
                "description": "A CIDR notation IP range from which to assign service cluster IPs."
            }
        },
        "dnsServiceIP": {
            "type": "string",
            "metadata": {
                "description": "Containers DNS server IP address."
            }
        },
        "dockerBridgeCidr": {
            "type": "string",
            "metadata": {
                "description": "A CIDR notation IP for Docker bridge."
            }
        },
        "principalId": {
            "type": "string",
            "metadata": {
                "description": "The objectId of service principal."
            }
        },
        "aciVnetSubnetName": {
            "type": "string",
            "metadata": {
                "description": "Name of virtual network subnet used for the ACI Connector."
            }
        },
        "aciConnectorLinuxEnabled": {
            "type": "bool",
            "metadata": {
                "description": "Enables the Linux ACI Connector."
            }
        }
    },
    "resources": [
        {
            "apiVersion": "2019-06-01",
            "dependsOn": [
                "Microsoft.Network/virtualNetworks/aks9.12-vnet",
                "[concat('Microsoft.Resources/deployments/', 'ClusterSubnetRoleAssignmentDeployment-20190912213137')]",
                "[concat('Microsoft.Resources/deployments/', 'AciSubnetRoleAssignmentDeployment-20190912213137')]"
            ],
            "type": "Microsoft.ContainerService/managedClusters",
            "location": "[parameters('location')]",
            "name": "[parameters('resourceName')]",
            "properties": {
                "kubernetesVersion": "[parameters('kubernetesVersion')]",
                "enableRBAC": "[parameters('enableRBAC')]",
                "dnsPrefix": "[parameters('dnsPrefix')]",
                "agentPoolProfiles": [
                    {
                        "name": "agentpool",
                        "osDiskSizeGB": "[parameters('osDiskSizeGB')]",
                        "count": "[parameters('agentCount')]",
                        "vmSize": "[parameters('agentVMSize')]",
                        "osType": "[parameters('osType')]",
                        "storageProfile": "ManagedDisks",
                        "type": "VirtualMachineScaleSets",
                        "vnetSubnetID": "[parameters('vnetSubnetID')]"
                    }
                ],
                "servicePrincipalProfile": {
                    "ClientId": "[parameters('servicePrincipalClientId')]",
                    "Secret": "[parameters('servicePrincipalClientSecret')]"
                },
                "networkProfile": {
                    "networkPlugin": "[parameters('networkPlugin')]",
                    "serviceCidr": "[parameters('serviceCidr')]",
                    "dnsServiceIP": "[parameters('dnsServiceIP')]",
                    "dockerBridgeCidr": "[parameters('dockerBridgeCidr')]"
                },
                "addonProfiles": {
                    "httpApplicationRouting": {
                        "enabled": "[parameters('enableHttpApplicationRouting')]"
                    },
                    "aciConnectorLinux": {
                        "enabled": "[parameters('aciConnectorLinuxEnabled')]",
                        "config": {
                            "SubnetName": "[parameters('aciVnetSubnetName')]"
                        }
                    }
                }
            },
            "tags": {}
        },
        {
            "apiVersion": "2019-04-01",
            "name": "aks9.12-vnet",
            "type": "Microsoft.Network/virtualNetworks",
            "location": "eastus2",
            "properties": {
                "subnets": [
                    {
                        "name": "default",
                        "id": "/subscriptions/c147212a-2905-4806-8e38-905e4e08f46b/resourceGroups/aks9.12/providers/Microsoft.Network/virtualNetworks/aks9.12-vnet/subnets/default",
                        "properties": {
                            "addressPrefix": "10.240.0.0/16"
                        }
                    },
                    {
                        "name": "virtual-node-aci",
                        "id": "/subscriptions/c147212a-2905-4806-8e38-905e4e08f46b/resourceGroups/aks9.12/providers/Microsoft.Network/virtualNetworks/aks9.12-vnet/subnets/virtual-node-aci",
                        "properties": {
                            "addressPrefix": "10.241.0.0/16",
                            "delegations": [
                                {
                                    "name": "aciDelegation",
                                    "properties": {
                                        "serviceName": "Microsoft.ContainerInstance/containerGroups",
                                        "actions": [
                                            "Microsoft.Network/virtualNetworks/subnets/action"
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                ],
                "addressSpace": {
                    "addressPrefixes": [
                        "10.0.0.0/8"
                    ]
                }
            },
            "tags": {}
        },
        {
            "type": "Microsoft.Resources/deployments",
            "name": "ClusterSubnetRoleAssignmentDeployment-20190912213137",
            "apiVersion": "2017-05-10",
            "resourceGroup": "aks9.12",
            "subscriptionId": "c147212a-2905-4806-8e38-905e4e08f46b",
            "properties": {
                "mode": "Incremental",
                "template": {
                    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
                    "contentVersion": "1.0.0.0",
                    "parameters": {},
                    "variables": {},
                    "resources": [
                        {
                            "type": "Microsoft.Network/virtualNetworks/subnets/providers/roleAssignments",
                            "apiVersion": "2017-05-01",
                            "name": "aks9.12-vnet/default/Microsoft.Authorization/4a66158c-7345-456f-b162-f6a0b567f76d",
                            "properties": {
                                "roleDefinitionId": "[concat('/subscriptions/', subscription().subscriptionId, '/providers/Microsoft.Authorization/roleDefinitions/', '4d97b98b-1d4f-4787-a291-c67834d212e7')]",
                                "principalId": "[parameters('principalId')]",
                                "scope": "/subscriptions/c147212a-2905-4806-8e38-905e4e08f46b/resourceGroups/aks9.12/providers/Microsoft.Network/virtualNetworks/aks9.12-vnet/subnets/default"
                            }
                        }
                    ]
                }
            },
            "dependsOn": [
                "Microsoft.Network/virtualNetworks/aks9.12-vnet"
            ]
        },
        {
            "type": "Microsoft.Resources/deployments",
            "name": "AciSubnetRoleAssignmentDeployment-20190912213137",
            "apiVersion": "2017-05-10",
            "resourceGroup": "aks9.12",
            "subscriptionId": "c147212a-2905-4806-8e38-905e4e08f46b",
            "properties": {
                "mode": "Incremental",
                "template": {
                    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
                    "contentVersion": "1.0.0.0",
                    "parameters": {},
                    "variables": {},
                    "resources": [
                        {
                            "type": "Microsoft.Network/virtualNetworks/subnets/providers/roleAssignments",
                            "apiVersion": "2017-05-01",
                            "name": "aks9.12-vnet/virtual-node-aci/Microsoft.Authorization/b6d22281-fc63-4ae7-a969-916eabecc130",
                            "properties": {
                                "roleDefinitionId": "[concat('/subscriptions/', subscription().subscriptionId, '/providers/Microsoft.Authorization/roleDefinitions/', '4d97b98b-1d4f-4787-a291-c67834d212e7')]",
                                "principalId": "[parameters('principalId')]",
                                "scope": "/subscriptions/c147212a-2905-4806-8e38-905e4e08f46b/resourceGroups/aks9.12/providers/Microsoft.Network/virtualNetworks/aks9.12-vnet/subnets/virtual-node-aci"
                            }
                        }
                    ]
                }
            },
            "dependsOn": [
                "Microsoft.Network/virtualNetworks/aks9.12-vnet"
            ]
        }
    ],
    "outputs": {
        "controlPlaneFQDN": {
            "type": "string",
            "value": "[reference(concat('Microsoft.ContainerService/managedClusters/', parameters('resourceName'))).fqdn]"
        }
    }
}'''

datastore = json.loads(arm)
#print(datastore)

with open('azuredeploy.json', 'w+') as f:
        json.dump(datastore, f, indent=4)

param='''{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "resourceName": {
            "value": "seismiccluster1"
        },
        "location": {
            "value": "eastus2"
        },
        "dnsPrefix": {
            "value": "seismiccluster1-dns"
        },
        "agentCount": {
            "value": %s
        },
        "agentVMSize": {
            "value": "Standard_DS2_v2"
        },
        "servicePrincipalClientId": {
            "value": "99896d62-bbf6-4ccc-b171-adfe366f3c1d"
        },
        "servicePrincipalClientSecret": {
            "value": "HgXKAHST3*C]Riy:T[jHdvh8UpoEss66"
        },
        "kubernetesVersion": {
            "value": "1.13.10"
        },
        "networkPlugin": {
            "value": "azure"
        },
        "enableRBAC": {
            "value": false
        },
        "enableHttpApplicationRouting": {
            "value": false
        },
        "vmssNodePool": {
            "value": true
        },
        "vnetSubnetID": {
            "value": "MC_aks0914_seismiccluster1_EastUS2"
        },
        "serviceCidr": {
            "value": "10.0.0.0/16"
        },
        "dnsServiceIP": {
            "value": "10.0.0.10"
        },
        "dockerBridgeCidr": {
            "value": "172.17.0.1/16"
        },
        "principalId": {
            "value": "f7694109-ed30-424f-9c8a-b133fa32c22b"
        },
        "aciVnetSubnetName": {
            "value": "virtual-node-aci"
        },
        "aciConnectorLinuxEnabled": {
            "value": true
        }
    }
}'''%(container_count_i)
#print(param)

matastore = json.loads(param)
#print(type((datastore))

with open('azuredeploy.parameters.json', 'w+') as f:
        json.dump(matastore, f, indent=4)
#print(datastore)


