param prefix string
param location string
param environment string

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

