targetScope = 'resourceGroup'

@description('GitHub organization or user that owns the repository.')
param githubOwner string

@description('GitHub repository name.')
param githubRepo string = 'crooked-numbers-statcast-ingestion'

@description('Optional GitHub owner ID for immutable OIDC subject claims.')
param githubOwnerId string = ''

@description('Optional GitHub repository ID for immutable OIDC subject claims.')
param githubRepoId string = ''

@description('Azure location for the managed identity.')
param location string = resourceGroup().location

@description('Name of the GitHub Actions managed identity.')
param identityName string = 'id-github-crooked-numbers-dev'

@description('Existing Azure Storage account that receives Statcast data.')
param storageAccountName string = 'crookednumbers'

var storageBlobDataContributorRoleDefinitionId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
)
var federatedCredentialName = 'github-main'
var useImmutableSubject = !empty(githubOwnerId) && !empty(githubRepoId)
var githubSubject = useImmutableSubject
  ? 'repo:${githubOwner}@${githubOwnerId}/${githubRepo}@${githubRepoId}:ref:refs/heads/main'
  : 'repo:${githubOwner}/${githubRepo}:ref:refs/heads/main'

resource githubIngestionIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
}

resource githubMainFederatedCredential 'Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials@2024-11-30' = {
  parent: githubIngestionIdentity
  name: federatedCredentialName
  properties: {
    issuer: 'https://token.actions.githubusercontent.com'
    subject: githubSubject
    audiences: [
      'api://AzureADTokenExchange'
    ]
  }
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: storageAccountName
}

resource storageBlobDataContributorAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, githubIngestionIdentity.id, 'storage-blob-data-contributor')
  scope: storageAccount
  properties: {
    roleDefinitionId: storageBlobDataContributorRoleDefinitionId
    principalId: githubIngestionIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

output clientId string = githubIngestionIdentity.properties.clientId
output principalId string = githubIngestionIdentity.properties.principalId
output federatedSubject string = githubSubject
output tenantId string = tenant().tenantId
output subscriptionId string = subscription().subscriptionId
