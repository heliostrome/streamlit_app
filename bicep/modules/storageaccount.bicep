param prefix string
param location string
param environment string
param keyVaultName string

//make lowercase and remove the dashes
var prefixClean = toLower(replace('${prefix}-${environment}','-',''))
var storageAccountName = '${prefixClean}sa'

resource storageAccount 'Microsoft.Storage/storageAccounts@2019-06-01' = {
  name: storageAccountName
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    accessTier: 'Hot'
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' existing = {
  name: keyVaultName
}
//add storage account key to key vault
resource secretResource 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  name: 'blob-account-key'
  parent: keyVault
  properties: {
    value: storageAccount.listKeys().keys[0].value
  }
}

output storageAccountConnectionProperties object = {
  secretName: secretResource.name
  storageAccountName: storageAccount.name
}
