param prefix string
param location string
param environment string

var vnetAddressPrefix = '10.0.0.0/16'
var frontendSubnetPrefix = '10.0.1.0/24'
var backendSubnetPrefix = '10.0.2.0/24'
var frontendSubnetName = '${prefix}-${environment}-frontend-subnet'
var backendSubnetName = '${prefix}-${environment}-backend-subnet'

var pvtDnsZoneName = 'privatelink${az.environment().suffixes.sqlServerHostname}'
// var pvtEndpointDnsGroupName = '${prefix}-${environment}-pvtendpointdnsgrp'
var pvtDnsZoneLinkName = '${prefix}-${environment}-pvtdnszonelink'
// var pvtDnsZoneConfigName = 'config1'

//create a vnet
resource vnet 'Microsoft.Network/virtualNetworks@2022-11-01' = {
  name: '${prefix}-${environment}-vnet'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        vnetAddressPrefix
      ]
    }
    subnets: [
      {
        name: frontendSubnetName
        properties: {
          addressPrefix: frontendSubnetPrefix
          delegations: [
            {
              name: 'Microsoft.Web/serverFarms'
              properties: {
                serviceName: 'Microsoft.Web/serverFarms'
              }
            }
          ]
        }
      }
      {
        name: backendSubnetName
        properties: {
          addressPrefix: backendSubnetPrefix
        }
      }
    ]
  }
}

resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: pvtDnsZoneName
  location: 'global'
  properties: {}
}

resource privateDnsZoneLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent: privateDnsZone
  name: pvtDnsZoneLinkName
  location: 'global'
  properties: {
    registrationEnabled: false
    virtualNetwork: {
      id: vnet.id
    }
  }
}

// resource pvtEndpointDnsGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2021-05-01' = {
//   name: pvtEndpointDnsGroupName
//   parent: privateDnsZone
//   properties: {
//     privateDnsZoneConfigs: [
//       {
//         name: pvtDnsZoneConfigName
//         properties: {
//           privateDnsZoneId: privateDnsZone.id
//         }
//       }
//     ]
//   }
// }

output vnetName string = vnet.name
output frontendSubnetName string = vnet.properties.subnets[0].name
output backendSubnetName string = vnet.properties.subnets[1].name


