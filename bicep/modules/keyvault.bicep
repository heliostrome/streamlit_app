param prefix string
param location string
param environment string
param githubActionsPrincipalId string
@secure()
param sqlServerAdminLoginPassword string

resource kv 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: '${prefix}-${environment}-kv'
  location: location
  properties: {
    sku: {
      name: 'standard'
      family: 'A'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
  }
}

module keyVaultRBACModule 'keyvaultrbac.bicep' = {
  name: 'keyVaultRBACDeployment'
  params: {
    keyVaultName: kv.name
    principalIds: [githubActionsPrincipalId]
  }
}

resource secret 'Microsoft.KeyVault/vaults/secrets@2022-11-01' = {
  parent: kv
  name: 'sqlServerAdminLoginPassword'
  properties: {
    value: sqlServerAdminLoginPassword
  }
  dependsOn: [
    keyVaultRBACModule
  ]
}
output keyVaultName string = kv.name
output secretName string = secret.name

