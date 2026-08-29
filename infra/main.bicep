@description('Azure location for all new resources.')
param location string = resourceGroup().location

@description('Azure Container Registry name.')
param acrName string

@allowed([
  'Basic'
  'Standard'
  'Premium'
])
@description('Azure Container Registry SKU.')
param acrSku string = 'Basic'

@description('Log Analytics workspace name.')
param logAnalyticsName string

@description('Container Apps managed environment name.')
param containerAppsEnvironmentName string

@description('Container Apps Job name.')
param jobName string

@description('User-assigned managed identity name for the job.')
param jobIdentityName string

@description('Existing storage account name.')
param storageAccountName string

@description('Blob container name.')
param blobContainerName string

@description('Repository and tag path within ACR, for example statcast-ingest:dev.')
param imageName string

@description('Cron expression for the scheduled job.')
param cronExpression string = '0 12 * * *'

@description('CPU cores allocated to the job container.')
param cpu string = '0.5'

@description('Memory allocated to the job container.')
param memory string = '1Gi'

@description('Job timeout in seconds.')
param replicaTimeout int = 1800

@description('Retry limit for a failed replica.')
param replicaRetryLimit int = 1

@description('Statcast lookback days passed to the ingestion job.')
param statcastLookbackDays int = 3

var storageBlobDataContributorRoleDefinitionId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
)
var acrPullRoleDefinitionId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '7f951dda-4ed3-4680-a7ca-43fe172d538d'
)

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  sku: {
    name: acrSku
  }
  properties: {
    adminUserEnabled: false
    publicNetworkAccess: 'Enabled'
  }
}

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      searchVersion: 1
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: containerAppsEnvironmentName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: listKeys(logAnalytics.id, logAnalytics.apiVersion).primarySharedKey
      }
    }
  }
}

resource jobIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: jobIdentityName
  location: location
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: storageAccountName
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' existing = {
  parent: storageAccount
  name: 'default'
}

resource blobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: blobContainerName
  properties: {
    publicAccess: 'None'
  }
}

resource storageBlobDataContributorAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, jobIdentity.id, 'storage-blob-data-contributor')
  scope: storageAccount
  properties: {
    roleDefinitionId: storageBlobDataContributorRoleDefinitionId
    principalId: jobIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource acrPullAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, jobIdentity.id, 'acr-pull')
  scope: acr
  properties: {
    roleDefinitionId: acrPullRoleDefinitionId
    principalId: jobIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource job 'Microsoft.App/jobs@2024-03-01' = {
  name: jobName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${jobIdentity.id}': {}
    }
  }
  properties: {
    environmentId: containerAppsEnvironment.id
    configuration: {
      triggerType: 'Schedule'
      scheduleTriggerConfig: {
        cronExpression: cronExpression
        parallelism: 1
        replicaCompletionCount: 1
      }
      replicaRetryLimit: replicaRetryLimit
      replicaTimeout: replicaTimeout
      registries: [
        {
          server: acr.properties.loginServer
          identity: jobIdentity.id
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'statcast-ingest'
          image: '${acr.properties.loginServer}/${imageName}'
          resources: {
            cpu: json(cpu)
            memory: memory
          }
          env: [
            {
              name: 'BLOB_ACCOUNT_URL'
              value: 'https://crookednumbers.blob.core.windows.net'
            }
            {
              name: 'STATCAST_CONTAINER'
              value: blobContainerName
            }
            {
              name: 'STATCAST_LOOKBACK_DAYS'
              value: string(statcastLookbackDays)
            }
            {
              name: 'INGESTION_MODE'
              value: 'daily_container_app_job'
            }
            {
              name: 'STORAGE_MODE'
              value: 'azure'
            }
            {
              name: 'AZURE_CLIENT_ID'
              value: jobIdentity.properties.clientId
            }
          ]
        }
      ]
    }
  }
}

output acrLoginServer string = acr.properties.loginServer
output containerAppsEnvironmentId string = containerAppsEnvironment.id
output jobIdentityClientId string = jobIdentity.properties.clientId
output jobNameOutput string = job.name
