@description('Prefix to put in front of all the resources')
param prefix string
@allowed(['nonprod', 'prod'])
param environment string
@allowed(['westeurope'])
param location string
@description('The principal id of the github actions service principal')
param githubActionsPrincipalId string
@secure()
param sqlServerAdminLoginPassword string
// param sqlServerAdminLogin string
// set the scope to the subscription for this bicep file
targetScope = 'subscription'

// create resource group
resource rg 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: '${prefix}-${environment}-rg'
  location: location
}

// create the resources within the group
module rg_resources 'rg.bicep' = {
  name: 'rg_resources'
  scope: rg
  params: {
    prefix: prefix
    environment: environment
    location: location
    githubActionsPrincipalId: githubActionsPrincipalId
    sqlServerAdminLoginPassword: sqlServerAdminLoginPassword
    // sqlServerAdminLogin: sqlServerAdminLogin
  }
}

