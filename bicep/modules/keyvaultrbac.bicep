param keyVaultName string
param principalIds array

var keyVaultSecretUserId = '4633458b-17de-408a-b874-0445c86b69e6'

resource kv 'Microsoft.KeyVault/vaults@2022-07-01' existing = {
  name: keyVaultName
}

// get the role definition id for the key vault
resource secretUserDefinitionId 'Microsoft.Authorization/roleDefinitions@2022-04-01' existing = {
  scope: kv
  name: keyVaultSecretUserId
}

// assign the RBAC role to the webapp
resource webappRoleAssignment 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = [ for principalId in principalIds :{
  name: guid(kv.id, principalId, secretUserDefinitionId.id)
  scope: kv
  properties: {
    roleDefinitionId: secretUserDefinitionId.id
    principalId: principalId
    principalType: 'ServicePrincipal'  }
}]

