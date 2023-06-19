param prefix string
param environment string
param location string

var acrName = toLower(replace('${prefix}-${environment}-acr','-',''))
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

output acrName string = acr.name
