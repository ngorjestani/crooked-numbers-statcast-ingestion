targetScope = 'resourceGroup'

@description('GitHub organization or user that owns the repository.')
param githubOwner string

@description('GitHub repository name.')
param githubRepo string

@description('Optional GitHub owner ID for immutable OIDC subject claims.')
param githubOwnerId string = ''

@description('Optional GitHub repository ID for immutable OIDC subject claims.')
param githubRepoId string = ''

@description('Azure location for the managed identity.')
param location string = resourceGroup().location

var contributorRoleDefinitionId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  'b24988ac-6180-42a0-ab88-20f7382dd24c'
)
var federatedCredentialName = 'github-main'
var useImmutableSubject = !empty(githubOwnerId) && !empty(githubRepoId)
var githubSubject = useImmutableSubject
  ? 'repo:${githubOwner}@${githubOwnerId}/${githubRepo}@${githubRepoId}:ref:refs/heads/main'
  : 'repo:${githubOwner}/${githubRepo}:ref:refs/heads/main'

resource githubDeploymentIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-github-crooked-numbers-dev'
  location: location
}

resource githubMainFederatedCredential 'Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials@2024-11-30' = {
  parent: githubDeploymentIdentity
  name: federatedCredentialName
  properties: {
    issuer: 'https://token.actions.githubusercontent.com'
    subject: githubSubject
    audiences: [
      'api://AzureADTokenExchange'
    ]
  }
}

resource contributorAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, githubDeploymentIdentity.id, 'contributor')
  scope: resourceGroup()
  properties: {
    roleDefinitionId: contributorRoleDefinitionId
    principalId: githubDeploymentIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

output clientId string = githubDeploymentIdentity.properties.clientId
output principalId string = githubDeploymentIdentity.properties.principalId
output federatedSubject string = githubSubject
