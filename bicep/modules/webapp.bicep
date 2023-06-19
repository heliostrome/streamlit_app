param prefix string
param location string
param environment string
param appServicePlanName string
param vnetName string
param frontendSubNetName string


resource vnet 'Microsoft.Network/virtualNetworks@2021-02-01' existing = {
  name: vnetName
}

resource subnet 'Microsoft.Network/virtualNetworks/subnets@2021-02-01' existing = {
  parent: vnet
  name: frontendSubNetName
}

//create a web app within the app service plan
resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' existing = {
  name: appServicePlanName
}

resource webApp 'Microsoft.Web/sites@2022-09-01' = {
  name: '${prefix}-${location}-${environment}-webapp'
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      appSettings: [
        {
          name: 'WEBSITE_NODE_DEFAULT_VERSION'
          value: '14.17.0'
        }
      ]
    }
  }
  identity: {
    type: 'SystemAssigned'
  }
}

resource networkConfig 'Microsoft.Web/sites/networkConfig@2022-09-01' = {
  parent: webApp
  name: 'virtualNetwork'
  properties: {
    subnetResourceId: subnet.id
  }
}

output webAppPrincipalIdentityId string = webApp.identity.principalId
