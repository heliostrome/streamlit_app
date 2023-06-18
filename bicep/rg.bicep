param prefix string
param environment string
param location string

module vnetModule 'modules/vnet.bicep' = {
  name: 'vnetDeployment'
  params: {
    prefix: prefix
    environment: environment
    location: location
  }
}

module aspModule 'modules/appserviceplan.bicep' = {
  name: 'aspDeployment'
  params: {
    prefix: prefix
    environment: environment
    location: location
  }
}

module webAppModule 'modules/webapp.bicep' = {
  name: 'webAppDeployment'
  params: {
    prefix: prefix
    environment: environment
    location: location
    appServicePlanName: aspModule.outputs.appServicePlanName
    vnetName: vnetModule.outputs.vnetName
    frontendSubNetName: vnetModule.outputs.frontendSubnetName
  }
}

module sqlServerModule 'modules/sqldatabase.bicep' = {
  name: 'sqlServerDeployment'
  params: {
    prefix: prefix
    environment: environment
    location: location
    vnetName: vnetModule.outputs.vnetName
    backendSubnetName: vnetModule.outputs.backendSubnetName
  }
}


