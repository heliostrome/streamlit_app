param prefix string
param location string
param environment string
param vnetName string
param backendSubnetName string

var databaseName = '${prefix}-${environment}-db'
var privateEndpointName = '${prefix}-${environment}-sqlserver-pe'


resource vnet 'Microsoft.Network/virtualNetworks@2022-11-01' existing = {
  name: vnetName
}

resource subnet 'Microsoft.Network/virtualNetworks/subnets@2022-11-01' existing = {
  name: backendSubnetName
  parent: vnet
}

resource sqlServer 'Microsoft.Sql/servers@2022-11-01-preview' = {
  name: '${prefix}-${environment}-sqlserver'
  location: location
  properties: {
    administratorLogin: 'sqladmin'
    administratorLoginPassword: 'P@ssw0rd'
    version: '12.0'
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2022-11-01-preview' = {
  name: databaseName
  parent: sqlServer
  location: location
  properties: {
    
  }
}

resource privateEndpoint 'Microsoft.Network/privateEndpoints@2021-05-01' = {
  name: privateEndpointName
  location: location
  properties: {
    subnet: {
      id: subnet.id
    }
    privateLinkServiceConnections: [
      {
        name: privateEndpointName
        properties: {
          privateLinkServiceId: sqlServer.id
          groupIds: [
            'sqlServer'
          ]
        }
      }
    ]
  }
}

