param prefix string
param environment string
param location string
param githubActionsPrincipalId string
@secure()
param sqlServerAdminLoginPassword string
param sqlServerAdminLogin string

module keyVaultModule 'modules/keyvault.bicep' = {
  name: 'keyVaultDeployment'
  params: {
    prefix: prefix
    environment: environment
    location: location
    githubActionsPrincipalId: githubActionsPrincipalId
    sqlServerAdminLoginPassword: sqlServerAdminLoginPassword
  }
}

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
    sqlServerAdminLogin: sqlServerAdminLogin
    sqlServerAdminLoginPassword: sqlServerAdminLoginPassword
  }
}

module keyVaultRBACModule 'modules/keyvaultrbac.bicep' = {
  name: 'keyVaultRBACDeployment'
  params: {
    keyVaultName: keyVaultModule.outputs.keyVaultName
    principalIds: [webAppModule.outputs.webAppPrincipalIdentityId ]
  }
}


