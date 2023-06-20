param prefix string
param location string
param environment string
param appServicePlanName string
param vnetName string
param frontendSubNetName string
param keyVaultName string
param storageAccountConnectionProperties object
param acrConnectionProperties object

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
  name: '${prefix}-${environment}-webapp'
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'DOCKER'
      alwaysOn: true
      appSettings: [
        {
          name: 'BLOB_ACCOUNT_KEY'
          value: '@Microsoft.KeyVault(VaultName=${keyVaultName};SecretName=${storageAccountConnectionProperties.secretName})'
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'false'
        }
        {
          name: 'ENABLE_ORYX_BUILD'
          value: 'false'
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_PASSWORD'
          value: '@Microsoft.KeyVault(VaultName=${keyVaultName};SecretName=${acrConnectionProperties.secretPasswordName})'
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_URL'
          value: acrConnectionProperties.serverUrl
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_USERNAME'
          value: '@Microsoft.KeyVault(VaultName=${keyVaultName};SecretName=${acrConnectionProperties.secretUsernameName})'
        }
        {
          name: 'WEBSITE_PORT'
          value: '8080'
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
