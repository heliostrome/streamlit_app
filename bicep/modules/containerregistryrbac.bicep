param acrName string
param principalIds array
var acrPullRole = '7f951dda-4ed3-4680-a7ca-43fe172d538d'

resource acr 'Microsoft.ContainerRegistry/registries@2019-05-01' existing = {
  name: acrName
}

// get the role definition id for the key vault
resource acrRoleDefinitionId 'Microsoft.Authorization/roleDefinitions@2022-04-01' existing = {
  scope: acr
  name: acrPullRole
}

// create the role assignment
resource acrRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for principalId in principalIds:{
  name: guid(acr.id, principalId, acrRoleDefinitionId.id)
  scope: acr
  properties: {
    roleDefinitionId: acrRoleDefinitionId.id
    principalId: principalId
    principalType: 'ServicePrincipal'  }
}]
