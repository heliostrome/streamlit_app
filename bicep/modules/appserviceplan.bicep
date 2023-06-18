param prefix string
param location string
param environment string


// create app service plan within the frontend subnet
resource asp 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: '${prefix}-${environment}-asp'
  location: location
  properties: {    
    reserved: true    
  }
  
}

output appServicePlanName string = asp.name
