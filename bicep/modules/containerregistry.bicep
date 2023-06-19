param prefix string
param environment string
param location string
param keyVaultName string

var acrName = toLower(replace('${prefix}-${environment}-acr','-',''))

resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' existing = {
  name: keyVaultName
}

resource acr 'Microsoft.ContainerRegistry/registries@2020-11-01-preview' = {
  name: acrName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
    
  }
}

resource secretPassword 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  parent: keyVault
  name: 'acrpassword'
  properties: {
    value: acr.listCredentials().passwords[0].value
  }
}
resource secretUsername 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  parent: keyVault
  name: 'acrusername'
  properties: {
    value: acr.listCredentials().username
  }
}

output acrName string = acr.name
output secretPasswordName string = secretPassword.name
output secretUsernameName string = secretUsername.name
