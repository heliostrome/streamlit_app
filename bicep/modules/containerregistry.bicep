param prefix string
param environment string
param location string

resource acr 'Microsoft.ContainerRegistry/registries@2020-11-01-preview' = {
  name: '${prefix}-${environment}-acr'
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
    
  }
}

output acrName string = acr.name
