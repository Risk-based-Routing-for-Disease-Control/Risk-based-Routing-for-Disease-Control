param sites_bioroute_name string = 'bioroute'
param connections_teams_name string = 'teams'
param connections_outlook_name string = 'outlook'
param connections_office365_name string = 'office365'
param actionGroups_collector_name string = 'collector'
param serverfarms_dt4_project2_team1_name string = 'dt4-project2-team1'
param sites_dt4_team1_func_collector_name string = 'dt4-team1-func-collector'
param storageAccounts_dt4team1blob_name string = 'dt4team1blob'
param workflows_dt4_team1_alert_logicapps_name string = 'dt4-team1-alert-logicapps'
param serverfarms_ASP_dt4project2team1_a9bb_name string = 'ASP-dt4project2team1-a9bb'
param workspaces_dt4_team1_databricks_name string = 'dt4_team1_databricks'
param actionGroups_collection_fail_alert_name string = 'collection_fail_alert'
param components_dt4_team1_func_collector_name string = 'dt4-team1-func-collector'
param scheduledqueryrules_collection_fail_name string = 'collection fail'
param flexibleServers_dt4_postgresql_name string = 'dt4-postgresql'
param accessConnectors_dt4_team1_connector_name string = 'dt4_team1_connector'
param scheduledqueryrules_collection_failure_name string = 'collection_failure'
param userAssignedIdentities_bioroute_id_8fa7_name string = 'bioroute-id-8fa7'
param smartdetectoralertrules_failure_anomalies_dt4_team1_func_collector_name string = 'failure anomalies - dt4-team1-func-collector'
param actiongroups_application_insights_smart_detection_externalid string = '/subscriptions/27db5ec6-d206-4028-b5e1-6004dca5eeef/resourceGroups/a000-aml-rg/providers/microsoft.insights/actiongroups/application insights smart detection'
param workspaces_DefaultWorkspace_27db5ec6_d206_4028_b5e1_6004dca5eeef_SE_externalid string = '/subscriptions/27db5ec6-d206-4028-b5e1-6004dca5eeef/resourceGroups/DefaultResourceGroup-SE/providers/Microsoft.OperationalInsights/workspaces/DefaultWorkspace-27db5ec6-d206-4028-b5e1-6004dca5eeef-SE'

resource accessConnectors_dt4_team1_connector_name_resource 'Microsoft.Databricks/accessConnectors@2026-01-01' = {
  name: accessConnectors_dt4_team1_connector_name
  location: 'eastus'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {}
}

resource workspaces_dt4_team1_databricks_name_resource 'Microsoft.Databricks/workspaces@2026-01-01' = {
  name: workspaces_dt4_team1_databricks_name
  location: 'westus2'
  sku: {
    name: 'trial'
  }
  properties: {
    computeMode: 'Hybrid'
    defaultCatalog: {
      initialType: 'UnityCatalog'
    }
    managedResourceGroupId: '/subscriptions/27db5ec6-d206-4028-b5e1-6004dca5eeef/resourceGroups/databricks-rg-${workspaces_dt4_team1_databricks_name}-osohwq5crjhlc'
    parameters: {
      enableNoPublicIp: {
        type: 'Bool'
        value: true
      }
      prepareEncryption: {
        type: 'Bool'
        value: false
      }
      requireInfrastructureEncryption: {
        type: 'Bool'
        value: false
      }
      storageAccountName: {
        type: 'String'
        value: 'dbstorage2ir6sys2wego6'
      }
      storageAccountSkuName: {
        type: 'String'
        value: 'Standard_ZRS'
      }
    }
    authorizations: [
      {
        principalId: '9a74af6f-d153-4348-988a-e2672920bee9'
        roleDefinitionId: '8e3af657-a8ff-443c-a75c-2fe8c4bcb635'
      }
    ]
    createdBy: {}
    updatedBy: {}
  }
}

resource flexibleServers_dt4_postgresql_name_resource 'Microsoft.DBforPostgreSQL/flexibleServers@2026-01-01-preview' = {
  name: flexibleServers_dt4_postgresql_name
  location: 'Korea Central'
  sku: {
    name: 'Standard_B2s'
    tier: 'Burstable'
  }
  properties: {
    dataEncryption: {
      type: 'SystemManaged'
    }
    replica: {
      role: 'Primary'
    }
    storage: {
      type: 'Premium_LRS'
      iops: 120
      tier: 'P4'
      storageSizeGB: 32
      autoGrow: 'Disabled'
    }
    network: {
      publicNetworkAccess: 'Enabled'
    }
    authConfig: {
      activeDirectoryAuth: 'Disabled'
      passwordAuth: 'Enabled'
    }
    version: '16'
    administratorLogin: 'azureuser'
    availabilityZone: '1'
    backup: {
      backupRetentionDays: 8
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
    maintenanceWindow: {
      customWindow: 'Disabled'
      dayOfWeek: 0
      startHour: 0
      startMinute: 0
    }
    replicationRole: 'Primary'
  }
}

resource actionGroups_collection_fail_alert_name_resource 'microsoft.insights/actionGroups@2024-10-01-preview' = {
  name: actionGroups_collection_fail_alert_name
  location: 'eastus'
  properties: {
    groupShortName: '수집 실패'
    enabled: true
    emailReceivers: []
    smsReceivers: []
    webhookReceivers: []
    eventHubReceivers: []
    itsmReceivers: []
    azureAppPushReceivers: []
    automationRunbookReceivers: []
    voiceReceivers: []
    logicAppReceivers: []
    azureFunctionReceivers: []
    armRoleReceivers: []
  }
}

resource actionGroups_collector_name_resource 'microsoft.insights/actionGroups@2024-10-01-preview' = {
  name: actionGroups_collector_name
  location: 'Global'
  properties: {
    groupShortName: '파이프라인 - 수집'
    enabled: true
    emailReceivers: []
    smsReceivers: []
    webhookReceivers: [
      {
        name: 'webhook'
        serviceUri: 'https://prod-16.northcentralus.logic.azure.com:443/workflows/80ee27e8a28346099f80f72c41483ae3/triggers/When_an_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_an_HTTP_request_is_received%2Frun&sv=1.0&sig=EAeqnGhDhfQQV-rYuHxzzu8AaXDrhYNMQA_hLqrG6ak'
        useCommonAlertSchema: true
        useAadAuth: false
      }
    ]
    eventHubReceivers: []
    itsmReceivers: []
    azureAppPushReceivers: []
    automationRunbookReceivers: []
    voiceReceivers: []
    logicAppReceivers: []
    azureFunctionReceivers: []
    armRoleReceivers: []
  }
}

resource components_dt4_team1_func_collector_name_resource 'microsoft.insights/components@2020-02-02' = {
  name: components_dt4_team1_func_collector_name
  location: 'koreacentral'
  kind: 'web'
  properties: {
    Application_Type: 'web'
    Flow_Type: 'Redfield'
    Request_Source: 'IbizaWebAppExtensionCreate'
    RetentionInDays: 90
    WorkspaceResourceId: workspaces_DefaultWorkspace_27db5ec6_d206_4028_b5e1_6004dca5eeef_SE_externalid
    IngestionMode: 'LogAnalytics'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
    DisableLocalAuth: false
  }
}

resource userAssignedIdentities_bioroute_id_8fa7_name_resource 'Microsoft.ManagedIdentity/userAssignedIdentities@2025-05-31-preview' = {
  name: userAssignedIdentities_bioroute_id_8fa7_name
  location: 'koreacentral'
  properties: {
    isolationScope: 'None'
    assignmentRestrictions: {
      providers: []
    }
  }
}

resource storageAccounts_dt4team1blob_name_resource 'Microsoft.Storage/storageAccounts@2026-04-01' = {
  name: storageAccounts_dt4team1blob_name
  location: 'koreacentral'
  sku: {
    name: 'Standard_LRS'
    tier: 'Standard'
  }
  kind: 'StorageV2'
  properties: {
    dualStackEndpointPreference: {
      publishIpv6Endpoint: false
    }
    dnsEndpointType: 'Standard'
    defaultToOAuthAuthentication: false
    publicNetworkAccess: 'Enabled'
    allowCrossTenantReplication: false
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true
    networkAcls: {
      ipv6Rules: []
      resourceAccessRules: []
      bypass: 'AzureServices'
      virtualNetworkRules: []
      ipRules: []
      defaultAction: 'Allow'
    }
    supportsHttpsTrafficOnly: true
    encryption: {
      requireInfrastructureEncryption: false
      services: {
        file: {
          keyType: 'Account'
          enabled: true
        }
        blob: {
          keyType: 'Account'
          enabled: true
        }
      }
      keySource: 'Microsoft.Storage'
    }
    accessTier: 'Hot'
  }
}

resource connections_office365_name_resource 'Microsoft.Web/connections@2016-06-01' = {
  name: connections_office365_name
  location: 'northcentralus'
  kind: 'V1'
  properties: {
    displayName: 'starboy@officestu.seoultech.ac.kr'
    statuses: [
      {
        status: 'Connected'
      }
    ]
    customParameterValues: {}
    nonSecretParameterValues: {}
    createdTime: '2026-07-01T06:06:53.2474347Z'
    changedTime: '2026-07-09T04:58:37.6172371Z'
    api: {
      name: connections_office365_name
      displayName: 'Office 365 Outlook'
      description: 'Microsoft Office 365는 강력한 보안, 안정성 및 사용자 생산성에 대한 조직의 요구를 충족할 수 있도록 설계된 클라우드 기반 서비스입니다.'
      iconUri: 'https://static.powerapps.com/resource/ppcr/releases/v1.0.1817/1.0.1817.4781/${connections_office365_name}/icon.png'
      brandColor: '#0078D4'
      id: '/subscriptions/27db5ec6-d206-4028-b5e1-6004dca5eeef/providers/Microsoft.Web/locations/northcentralus/managedApis/${connections_office365_name}'
      type: 'Microsoft.Web/locations/managedApis'
    }
    testLinks: [
      {
        requestUri: 'https://management.azure.com:443/subscriptions/27db5ec6-d206-4028-b5e1-6004dca5eeef/resourceGroups/dt4_project2_team1/providers/Microsoft.Web/connections/${connections_office365_name}/extensions/proxy/testconnection?api-version=2016-06-01'
        method: 'get'
      }
    ]
  }
}

resource connections_outlook_name_resource 'Microsoft.Web/connections@2016-06-01' = {
  name: connections_outlook_name
  location: 'northcentralus'
  kind: 'V1'
  properties: {
    displayName: 'Outlook.com'
    statuses: [
      {
        status: 'Connected'
      }
    ]
    customParameterValues: {}
    nonSecretParameterValues: {}
    createdTime: '2026-07-01T14:51:28.5177391Z'
    changedTime: '2026-07-01T14:52:45.4477584Z'
    api: {
      name: connections_outlook_name
      displayName: 'Outlook.com'
      description: 'Outlook.com 커넥터를 사용하여 전자 메일, 일정 및 연락처를 관리할 수 있습니다. 전자 메일 보내기, 회의 예약, 연락처 추가 등과 같은 다양한 작업을 수행할 수 있습니다.'
      iconUri: 'https://static.powerapps.com/resource/ppcr/releases/v1.0.1816/1.0.1816.4782/${connections_outlook_name}/icon.png'
      id: '/subscriptions/27db5ec6-d206-4028-b5e1-6004dca5eeef/providers/Microsoft.Web/locations/northcentralus/managedApis/${connections_outlook_name}'
      type: 'Microsoft.Web/locations/managedApis'
    }
    testLinks: [
      {
        requestUri: 'https://management.azure.com:443/subscriptions/27db5ec6-d206-4028-b5e1-6004dca5eeef/resourceGroups/dt4_project2_team1/providers/Microsoft.Web/connections/${connections_outlook_name}/extensions/proxy/testconnection?api-version=2016-06-01'
        method: 'get'
      }
    ]
  }
}

resource connections_teams_name_resource 'Microsoft.Web/connections@2016-06-01' = {
  name: connections_teams_name
  location: 'northcentralus'
  kind: 'V1'
  properties: {
    displayName: '4dt021@dataschool.msai.kr'
    statuses: [
      {
        status: 'Connected'
      }
    ]
    customParameterValues: {}
    nonSecretParameterValues: {}
    createdTime: '2026-07-01T14:57:43.8871539Z'
    changedTime: '2026-07-05T09:27:57.4618165Z'
    api: {
      name: connections_teams_name
      displayName: 'Microsoft Teams'
      description: 'Microsoft Teams를 사용하면 Microsoft 365를 통해 모든 콘텐츠, 도구 및 대화를 팀 작업 영역에 가져올 수 있습니다.'
      iconUri: 'https://static.powerapps.com/resource/ppcr/releases/v1.0.1812/1.0.1812.4744/${connections_teams_name}/icon.png'
      id: '/subscriptions/27db5ec6-d206-4028-b5e1-6004dca5eeef/providers/Microsoft.Web/locations/northcentralus/managedApis/${connections_teams_name}'
      type: 'Microsoft.Web/locations/managedApis'
    }
    testLinks: [
      {
        requestUri: 'https://management.azure.com:443/subscriptions/27db5ec6-d206-4028-b5e1-6004dca5eeef/resourceGroups/dt4_project2_team1/providers/Microsoft.Web/connections/${connections_teams_name}/extensions/proxy/beta/me/teamwork?api-version=2016-06-01'
        method: 'get'
      }
    ]
  }
}

resource serverfarms_ASP_dt4project2team1_a9bb_name_resource 'Microsoft.Web/serverfarms@2024-11-01' = {
  name: serverfarms_ASP_dt4project2team1_a9bb_name
  location: 'Korea Central'
  sku: {
    name: 'FC1'
    tier: 'FlexConsumption'
    size: 'FC1'
    family: 'FC'
    capacity: 0
  }
  kind: 'functionapp'
  properties: {
    perSiteScaling: false
    elasticScaleEnabled: false
    maximumElasticWorkerCount: 1
    isSpot: false
    reserved: true
    isXenon: false
    hyperV: false
    targetWorkerCount: 0
    targetWorkerSizeId: 0
    zoneRedundant: false
    asyncScalingEnabled: false
  }
}

resource serverfarms_dt4_project2_team1_name_resource 'Microsoft.Web/serverfarms@2024-11-01' = {
  name: serverfarms_dt4_project2_team1_name
  location: 'Korea Central'
  sku: {
    name: 'B1'
    tier: 'Basic'
    size: 'B1'
    family: 'B'
    capacity: 1
  }
  kind: 'linux'
  properties: {
    perSiteScaling: false
    elasticScaleEnabled: false
    maximumElasticWorkerCount: 1
    isSpot: false
    freeOfferExpirationTime: '2026-07-26T03:28:48.82'
    reserved: true
    isXenon: false
    hyperV: false
    targetWorkerCount: 0
    targetWorkerSizeId: 0
    zoneRedundant: false
    asyncScalingEnabled: false
  }
}

resource smartdetectoralertrules_failure_anomalies_dt4_team1_func_collector_name_resource 'microsoft.alertsmanagement/smartdetectoralertrules@2021-04-01' = {
  name: smartdetectoralertrules_failure_anomalies_dt4_team1_func_collector_name
  location: 'global'
  properties: {
    description: 'Failure Anomalies notifies you of an unusual rise in the rate of failed HTTP requests or dependency calls.'
    state: 'Enabled'
    severity: 'Sev3'
    frequency: 'PT1M'
    detector: {
      id: 'FailureAnomaliesDetector'
    }
    scope: [
      components_dt4_team1_func_collector_name_resource.id
    ]
    actionGroups: {
      groupIds: [
        actiongroups_application_insights_smart_detection_externalid
      ]
    }
  }
}

resource flexibleServers_dt4_postgresql_name_Default 'Microsoft.DBforPostgreSQL/flexibleServers/advancedThreatProtectionSettings@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'Default'
  properties: {
    state: 'Disabled'
  }
}

resource flexibleServers_dt4_postgresql_name_backup_639186372233515103 'Microsoft.DBforPostgreSQL/flexibleServers/backups@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'backup_639186372233515103'
}

resource flexibleServers_dt4_postgresql_name_backup_639187236874677980 'Microsoft.DBforPostgreSQL/flexibleServers/backups@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'backup_639187236874677980'
}

resource flexibleServers_dt4_postgresql_name_backup_639188101514754670 'Microsoft.DBforPostgreSQL/flexibleServers/backups@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'backup_639188101514754670'
}

resource flexibleServers_dt4_postgresql_name_backup_639188965962463958 'Microsoft.DBforPostgreSQL/flexibleServers/backups@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'backup_639188965962463958'
}

resource flexibleServers_dt4_postgresql_name_backup_639189830606599126 'Microsoft.DBforPostgreSQL/flexibleServers/backups@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'backup_639189830606599126'
}

resource flexibleServers_dt4_postgresql_name_backup_639190695067358653 'Microsoft.DBforPostgreSQL/flexibleServers/backups@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'backup_639190695067358653'
}

resource flexibleServers_dt4_postgresql_name_backup_639191559511505782 'Microsoft.DBforPostgreSQL/flexibleServers/backups@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'backup_639191559511505782'
}

resource flexibleServers_dt4_postgresql_name_backup_639192423952801810 'Microsoft.DBforPostgreSQL/flexibleServers/backups@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'backup_639192423952801810'
}

resource flexibleServers_dt4_postgresql_name_age_enable_containment 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'age.enable_containment'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_allow_in_place_tablespaces 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'allow_in_place_tablespaces'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_allow_system_table_mods 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'allow_system_table_mods'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_anon_algorithm 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'anon.algorithm'
  properties: {
    value: 'sha256'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_anon_k_anonymity_provider 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'anon.k_anonymity_provider'
  properties: {
    value: 'k_anonymity'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_anon_masking_policies 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'anon.masking_policies'
  properties: {
    value: 'anon'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_anon_maskschema 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'anon.maskschema'
  properties: {
    value: 'mask'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_anon_privacy_by_default 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'anon.privacy_by_default'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_anon_restrict_to_trusted_schemas 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'anon.restrict_to_trusted_schemas'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_anon_salt 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'anon.salt'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_anon_sourceschema 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'anon.sourceschema'
  properties: {
    value: 'public'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_anon_strict_mode 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'anon.strict_mode'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_anon_transparent_dynamic_masking 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'anon.transparent_dynamic_masking'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_application_name 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'application_name'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_archive_cleanup_command 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'archive_cleanup_command'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_archive_command 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'archive_command'
  properties: {
    value: 'BlobLogUpload.sh %f %p'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_archive_library 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'archive_library'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_archive_mode 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'archive_mode'
  properties: {
    value: 'always'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_archive_timeout 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'archive_timeout'
  properties: {
    value: '300'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_array_nulls 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'array_nulls'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_authentication_timeout 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'authentication_timeout'
  properties: {
    value: '30'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_auto_explain_log_analyze 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'auto_explain.log_analyze'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_auto_explain_log_buffers 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'auto_explain.log_buffers'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_auto_explain_log_format 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'auto_explain.log_format'
  properties: {
    value: 'text'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_auto_explain_log_level 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'auto_explain.log_level'
  properties: {
    value: 'log'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_auto_explain_log_min_duration 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'auto_explain.log_min_duration'
  properties: {
    value: '-1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_auto_explain_log_nested_statements 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'auto_explain.log_nested_statements'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_auto_explain_log_parameter_max_length 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'auto_explain.log_parameter_max_length'
  properties: {
    value: '-1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_auto_explain_log_settings 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'auto_explain.log_settings'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_auto_explain_log_timing 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'auto_explain.log_timing'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_auto_explain_log_triggers 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'auto_explain.log_triggers'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_auto_explain_log_verbose 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'auto_explain.log_verbose'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_auto_explain_log_wal 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'auto_explain.log_wal'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_auto_explain_sample_rate 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'auto_explain.sample_rate'
  properties: {
    value: '1.0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_autovacuum 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'autovacuum'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_autovacuum_analyze_scale_factor 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'autovacuum_analyze_scale_factor'
  properties: {
    value: '0.1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_autovacuum_analyze_threshold 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'autovacuum_analyze_threshold'
  properties: {
    value: '50'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_autovacuum_freeze_max_age 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'autovacuum_freeze_max_age'
  properties: {
    value: '200000000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_autovacuum_max_workers 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'autovacuum_max_workers'
  properties: {
    value: '3'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_autovacuum_multixact_freeze_max_age 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'autovacuum_multixact_freeze_max_age'
  properties: {
    value: '400000000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_autovacuum_naptime 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'autovacuum_naptime'
  properties: {
    value: '60'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_autovacuum_vacuum_cost_delay 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'autovacuum_vacuum_cost_delay'
  properties: {
    value: '2'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_autovacuum_vacuum_cost_limit 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'autovacuum_vacuum_cost_limit'
  properties: {
    value: '-1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_autovacuum_vacuum_insert_scale_factor 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'autovacuum_vacuum_insert_scale_factor'
  properties: {
    value: '0.2'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_autovacuum_vacuum_insert_threshold 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'autovacuum_vacuum_insert_threshold'
  properties: {
    value: '1000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_autovacuum_vacuum_scale_factor 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'autovacuum_vacuum_scale_factor'
  properties: {
    value: '0.2'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_autovacuum_vacuum_threshold 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'autovacuum_vacuum_threshold'
  properties: {
    value: '50'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_autovacuum_work_mem 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'autovacuum_work_mem'
  properties: {
    value: '-1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_accepted_password_auth_method 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure.accepted_password_auth_method'
  properties: {
    value: 'md5,scram-sha-256'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_enable_temp_tablespaces_on_local_ssd 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure.enable_temp_tablespaces_on_local_ssd'
  properties: {
    value: 'off'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_extensions 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure.extensions'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_fabric_mirror_enabled 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure.fabric_mirror_enabled'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_migration_copy_with_binary 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure.migration_copy_with_binary'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_migration_skip_analyze 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure.migration_skip_analyze'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_migration_skip_extensions 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure.migration_skip_extensions'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_migration_skip_large_objects 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure.migration_skip_large_objects'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_migration_skip_role_user 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure.migration_skip_role_user'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_migration_table_split_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure.migration_table_split_size'
  properties: {
    value: '20480'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_service_principal_id 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure.service_principal_id'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_service_principal_tenant_id 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure.service_principal_tenant_id'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_single_to_flex_migration 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure.single_to_flex_migration'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_cdc_change_batch_buffer_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure_cdc.change_batch_buffer_size'
  properties: {
    value: '16'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_cdc_change_batch_export_timeout 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure_cdc.change_batch_export_timeout'
  properties: {
    value: '30'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_cdc_max_fabric_mirrors 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure_cdc.max_fabric_mirrors'
  properties: {
    value: '3'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_cdc_max_snapshot_workers 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure_cdc.max_snapshot_workers'
  properties: {
    value: '3'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_cdc_onelake_buffer_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure_cdc.onelake_buffer_size'
  properties: {
    value: '100'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_cdc_parquet_compression 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure_cdc.parquet_compression'
  properties: {
    value: 'zstd'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_cdc_snapshot_buffer_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure_cdc.snapshot_buffer_size'
  properties: {
    value: '1000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_cdc_snapshot_export_timeout 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure_cdc.snapshot_export_timeout'
  properties: {
    value: '180'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_storage_allow_network_access 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure_storage.allow_network_access'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_storage_blob_block_size_mb 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure_storage.blob_block_size_mb'
  properties: {
    value: '128'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_storage_log_level 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure_storage.log_level'
  properties: {
    value: 'log'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_storage_public_account_access 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure_storage.public_account_access'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_backend_flush_after 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'backend_flush_after'
  properties: {
    value: '256'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_backslash_quote 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'backslash_quote'
  properties: {
    value: 'safe_encoding'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_backtrace_functions 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'backtrace_functions'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_bgwriter_delay 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'bgwriter_delay'
  properties: {
    value: '20'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_bgwriter_flush_after 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'bgwriter_flush_after'
  properties: {
    value: '64'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_bgwriter_lru_maxpages 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'bgwriter_lru_maxpages'
  properties: {
    value: '100'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_bgwriter_lru_multiplier 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'bgwriter_lru_multiplier'
  properties: {
    value: '2'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_block_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'block_size'
  properties: {
    value: '8192'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_bonjour 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'bonjour'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_bonjour_name 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'bonjour_name'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_bytea_output 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'bytea_output'
  properties: {
    value: 'hex'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_check_function_bodies 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'check_function_bodies'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_checkpoint_completion_target 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'checkpoint_completion_target'
  properties: {
    value: '0.9'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_checkpoint_flush_after 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'checkpoint_flush_after'
  properties: {
    value: '32'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_checkpoint_timeout 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'checkpoint_timeout'
  properties: {
    value: '600'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_checkpoint_warning 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'checkpoint_warning'
  properties: {
    value: '30'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_client_connection_check_interval 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'client_connection_check_interval'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_client_encoding 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'client_encoding'
  properties: {
    value: 'UTF8'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_client_min_messages 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'client_min_messages'
  properties: {
    value: 'notice'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_cluster_name 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'cluster_name'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_commit_delay 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'commit_delay'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_commit_siblings 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'commit_siblings'
  properties: {
    value: '5'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_compute_query_id 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'compute_query_id'
  properties: {
    value: 'auto'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_config_file 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'config_file'
  properties: {
    value: '/datadrive/pg/data/postgresql.conf'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_connection_throttle_bucket_limit 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'connection_throttle.bucket_limit'
  properties: {
    value: '2000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_connection_throttle_enable 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'connection_throttle.enable'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_connection_throttle_factor_bias 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'connection_throttle.factor_bias'
  properties: {
    value: '0.8'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_connection_throttle_hash_entries_max 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'connection_throttle.hash_entries_max'
  properties: {
    value: '500'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_connection_throttle_reset_time 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'connection_throttle.reset_time'
  properties: {
    value: '120'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_connection_throttle_restore_factor 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'connection_throttle.restore_factor'
  properties: {
    value: '2'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_connection_throttle_update_time 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'connection_throttle.update_time'
  properties: {
    value: '20'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_constraint_exclusion 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'constraint_exclusion'
  properties: {
    value: 'partition'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_cpu_index_tuple_cost 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'cpu_index_tuple_cost'
  properties: {
    value: '0.005'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_cpu_operator_cost 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'cpu_operator_cost'
  properties: {
    value: '0.0025'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_cpu_tuple_cost 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'cpu_tuple_cost'
  properties: {
    value: '0.01'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_createrole_self_grant 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'createrole_self_grant'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_auth_delay_ms 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.auth_delay_ms'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_auth_failure_cache_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.auth_failure_cache_size'
  properties: {
    value: '1024'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_encrypted_password_allowed 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.encrypted_password_allowed'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_history_max_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.history_max_size'
  properties: {
    value: '65535'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_max_auth_failure 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.max_auth_failure'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_no_password_logging 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.no_password_logging'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_password_contain 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.password_contain'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_password_contain_username 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.password_contain_username'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_password_ignore_case 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.password_ignore_case'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_password_min_digit 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.password_min_digit'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_password_min_length 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.password_min_length'
  properties: {
    value: '1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_password_min_lower 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.password_min_lower'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_password_min_repeat 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.password_min_repeat'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_password_min_special 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.password_min_special'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_password_min_upper 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.password_min_upper'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_password_not_contain 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.password_not_contain'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_password_reuse_history 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.password_reuse_history'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_password_reuse_interval 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.password_reuse_interval'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_password_valid_max 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.password_valid_max'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_password_valid_until 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.password_valid_until'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_reset_superuser 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.reset_superuser'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_username_contain 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.username_contain'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_username_contain_password 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.username_contain_password'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_username_ignore_case 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.username_ignore_case'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_username_min_digit 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.username_min_digit'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_username_min_length 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.username_min_length'
  properties: {
    value: '1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_username_min_lower 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.username_min_lower'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_username_min_repeat 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.username_min_repeat'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_username_min_special 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.username_min_special'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_username_min_upper 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.username_min_upper'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_username_not_contain 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.username_not_contain'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_whitelist 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.whitelist'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_credcheck_whitelist_auth_failure 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'credcheck.whitelist_auth_failure'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_cron_database_name 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'cron.database_name'
  properties: {
    value: 'postgres'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_cron_enable_superuser_jobs 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'cron.enable_superuser_jobs'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_cron_host 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'cron.host'
  properties: {
    value: '/tmp'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_cron_launch_active_jobs 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'cron.launch_active_jobs'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_cron_log_min_messages 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'cron.log_min_messages'
  properties: {
    value: 'warning'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_cron_log_run 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'cron.log_run'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_cron_log_statement 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'cron.log_statement'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_cron_max_running_jobs 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'cron.max_running_jobs'
  properties: {
    value: '32'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_cron_timezone 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'cron.timezone'
  properties: {
    value: 'GMT'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_cron_use_background_workers 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'cron.use_background_workers'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_cursor_tuple_fraction 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'cursor_tuple_fraction'
  properties: {
    value: '0.1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_data_checksums 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'data_checksums'
  properties: {
    value: 'on'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_data_directory 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'data_directory'
  properties: {
    value: '/datadrive/pg/data'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_data_directory_mode 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'data_directory_mode'
  properties: {
    value: '0700'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_data_sync_retry 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'data_sync_retry'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_DateStyle 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'DateStyle'
  properties: {
    value: 'ISO, MDY'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_db_user_namespace 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'db_user_namespace'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_deadlock_timeout 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'deadlock_timeout'
  properties: {
    value: '1000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_debug_assertions 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'debug_assertions'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_debug_discard_caches 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'debug_discard_caches'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_debug_io_direct 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'debug_io_direct'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_debug_logical_replication_streaming 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'debug_logical_replication_streaming'
  properties: {
    value: 'buffered'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_debug_parallel_query 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'debug_parallel_query'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_debug_pretty_print 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'debug_pretty_print'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_debug_print_parse 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'debug_print_parse'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_debug_print_plan 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'debug_print_plan'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_debug_print_rewritten 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'debug_print_rewritten'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_default_statistics_target 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'default_statistics_target'
  properties: {
    value: '100'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_default_table_access_method 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'default_table_access_method'
  properties: {
    value: 'heap'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_default_tablespace 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'default_tablespace'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_default_text_search_config 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'default_text_search_config'
  properties: {
    value: 'pg_catalog.english'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_default_toast_compression 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'default_toast_compression'
  properties: {
    value: 'lz4'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_default_transaction_deferrable 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'default_transaction_deferrable'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_default_transaction_isolation 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'default_transaction_isolation'
  properties: {
    value: 'read committed'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_default_transaction_read_only 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'default_transaction_read_only'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_duckdb_allow_community_extensions 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'duckdb.allow_community_extensions'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_duckdb_allow_unsigned_extensions 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'duckdb.allow_unsigned_extensions'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_duckdb_autoinstall_known_extensions 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'duckdb.autoinstall_known_extensions'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_duckdb_autoload_known_extensions 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'duckdb.autoload_known_extensions'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_duckdb_disabled_filesystems 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'duckdb.disabled_filesystems'
  properties: {
    value: 'LocalFileSystem'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_duckdb_enable_external_access 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'duckdb.enable_external_access'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_duckdb_force_execution 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'duckdb.force_execution'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_duckdb_max_memory 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'duckdb.max_memory'
  properties: {
    value: '1024'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_duckdb_max_workers_per_postgres_scan 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'duckdb.max_workers_per_postgres_scan'
  properties: {
    value: '2'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_duckdb_memory_limit 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'duckdb.memory_limit'
  properties: {
    value: '1024'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_duckdb_postgres_role 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'duckdb.postgres_role'
  properties: {
    value: 'azure_pg_duckdb_admin'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_duckdb_threads 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'duckdb.threads'
  properties: {
    value: '-1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_duckdb_worker_threads 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'duckdb.worker_threads'
  properties: {
    value: '-1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_dynamic_library_path 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'dynamic_library_path'
  properties: {
    value: '$libdir'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_dynamic_shared_memory_type 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'dynamic_shared_memory_type'
  properties: {
    value: 'posix'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_effective_cache_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'effective_cache_size'
  properties: {
    value: '393216'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_effective_io_concurrency 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'effective_io_concurrency'
  properties: {
    value: '1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_enable_async_append 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'enable_async_append'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_enable_bitmapscan 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'enable_bitmapscan'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_enable_gathermerge 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'enable_gathermerge'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_enable_hashagg 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'enable_hashagg'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_enable_hashjoin 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'enable_hashjoin'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_enable_incremental_sort 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'enable_incremental_sort'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_enable_indexonlyscan 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'enable_indexonlyscan'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_enable_indexscan 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'enable_indexscan'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_enable_material 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'enable_material'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_enable_memoize 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'enable_memoize'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_enable_mergejoin 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'enable_mergejoin'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_enable_nestloop 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'enable_nestloop'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_enable_parallel_append 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'enable_parallel_append'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_enable_parallel_hash 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'enable_parallel_hash'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_enable_partition_pruning 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'enable_partition_pruning'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_enable_partitionwise_aggregate 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'enable_partitionwise_aggregate'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_enable_partitionwise_join 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'enable_partitionwise_join'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_enable_presorted_aggregate 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'enable_presorted_aggregate'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_enable_seqscan 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'enable_seqscan'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_enable_sort 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'enable_sort'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_enable_tidscan 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'enable_tidscan'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_escape_string_warning 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'escape_string_warning'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_event_source 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'event_source'
  properties: {
    value: 'PostgreSQL'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_exit_on_error 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'exit_on_error'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_external_pid_file 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'external_pid_file'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_extra_float_digits 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'extra_float_digits'
  properties: {
    value: '1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_from_collapse_limit 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'from_collapse_limit'
  properties: {
    value: '8'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_fsync 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'fsync'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_full_page_writes 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'full_page_writes'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_geqo 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'geqo'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_geqo_effort 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'geqo_effort'
  properties: {
    value: '5'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_geqo_generations 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'geqo_generations'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_geqo_pool_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'geqo_pool_size'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_geqo_seed 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'geqo_seed'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_geqo_selection_bias 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'geqo_selection_bias'
  properties: {
    value: '2'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_geqo_threshold 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'geqo_threshold'
  properties: {
    value: '12'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_gin_fuzzy_search_limit 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'gin_fuzzy_search_limit'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_gin_pending_list_limit 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'gin_pending_list_limit'
  properties: {
    value: '4096'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_gss_accept_delegation 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'gss_accept_delegation'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_hash_mem_multiplier 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'hash_mem_multiplier'
  properties: {
    value: '2'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_hba_file 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'hba_file'
  properties: {
    value: '/datadrive/pg/data/pg_hba.conf'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_hot_standby 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'hot_standby'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_hot_standby_feedback 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'hot_standby_feedback'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_huge_page_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'huge_page_size'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_huge_pages 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'huge_pages'
  properties: {
    value: 'try'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_icu_validation_level 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'icu_validation_level'
  properties: {
    value: 'warning'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_ident_file 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'ident_file'
  properties: {
    value: '/datadrive/pg/data/pg_ident.conf'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_idle_in_transaction_session_timeout 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'idle_in_transaction_session_timeout'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_idle_session_timeout 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'idle_session_timeout'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_ignore_checksum_failure 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'ignore_checksum_failure'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_ignore_invalid_pages 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'ignore_invalid_pages'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_ignore_system_indexes 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'ignore_system_indexes'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_in_hot_standby 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'in_hot_standby'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_integer_datetimes 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'integer_datetimes'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_intelligent_tuning 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'intelligent_tuning'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_intelligent_tuning_metric_targets 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'intelligent_tuning.metric_targets'
  properties: {
    value: 'none'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_IntervalStyle 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'IntervalStyle'
  properties: {
    value: 'postgres'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_jit 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'jit'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_jit_above_cost 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'jit_above_cost'
  properties: {
    value: '100000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_jit_debugging_support 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'jit_debugging_support'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_jit_dump_bitcode 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'jit_dump_bitcode'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_jit_expressions 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'jit_expressions'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_jit_inline_above_cost 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'jit_inline_above_cost'
  properties: {
    value: '500000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_jit_optimize_above_cost 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'jit_optimize_above_cost'
  properties: {
    value: '500000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_jit_profiling_support 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'jit_profiling_support'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_jit_provider 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'jit_provider'
  properties: {
    value: 'llvmjit'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_jit_tuple_deforming 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'jit_tuple_deforming'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_join_collapse_limit 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'join_collapse_limit'
  properties: {
    value: '8'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_krb_caseins_users 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'krb_caseins_users'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_krb_server_keyfile 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'krb_server_keyfile'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_lc_messages 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'lc_messages'
  properties: {
    value: 'en_US.utf8'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_lc_monetary 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'lc_monetary'
  properties: {
    value: 'en_US.utf-8'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_lc_numeric 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'lc_numeric'
  properties: {
    value: 'en_US.utf-8'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_lc_time 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'lc_time'
  properties: {
    value: 'en_US.utf8'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_listen_addresses 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'listen_addresses'
  properties: {
    value: '*'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_lo_compat_privileges 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'lo_compat_privileges'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_local_preload_libraries 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'local_preload_libraries'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_lock_timeout 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'lock_timeout'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_autovacuum_min_duration 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_autovacuum_min_duration'
  properties: {
    value: '600000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_checkpoints 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_checkpoints'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_connections 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_connections'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_destination 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_destination'
  properties: {
    value: 'stderr'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_directory 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_directory'
  properties: {
    value: 'log'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_disconnections 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_disconnections'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_duration 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_duration'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_error_verbosity 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_error_verbosity'
  properties: {
    value: 'default'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_executor_stats 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_executor_stats'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_file_mode 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_file_mode'
  properties: {
    value: '0600'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_log_filename 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_filename'
  properties: {
    value: 'postgresql-%Y-%m-%d_%H%M%S.log'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_hostname 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_hostname'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_line_prefix 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_line_prefix'
  properties: {
    value: '%t-%c-'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_lock_waits 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_lock_waits'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_min_duration_sample 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_min_duration_sample'
  properties: {
    value: '-1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_min_duration_statement 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_min_duration_statement'
  properties: {
    value: '-1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_min_error_statement 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_min_error_statement'
  properties: {
    value: 'error'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_min_messages 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_min_messages'
  properties: {
    value: 'warning'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_parameter_max_length 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_parameter_max_length'
  properties: {
    value: '-1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_parameter_max_length_on_error 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_parameter_max_length_on_error'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_parser_stats 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_parser_stats'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_planner_stats 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_planner_stats'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_recovery_conflict_waits 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_recovery_conflict_waits'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_replication_commands 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_replication_commands'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_rotation_age 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_rotation_age'
  properties: {
    value: '60'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_log_rotation_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_rotation_size'
  properties: {
    value: '102400'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_log_startup_progress_interval 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_startup_progress_interval'
  properties: {
    value: '10000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_statement 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_statement'
  properties: {
    value: 'none'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_statement_sample_rate 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_statement_sample_rate'
  properties: {
    value: '1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_statement_stats 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_statement_stats'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_temp_files 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_temp_files'
  properties: {
    value: '-1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_timezone 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_timezone'
  properties: {
    value: 'UTC'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_log_transaction_sample_rate 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_transaction_sample_rate'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_log_truncate_on_rotation 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'log_truncate_on_rotation'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_logfiles_download_enable 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'logfiles.download_enable'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_logfiles_retention_days 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'logfiles.retention_days'
  properties: {
    value: '3'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_logging_collector 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'logging_collector'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_logical_decoding_work_mem 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'logical_decoding_work_mem'
  properties: {
    value: '65536'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_maintenance_io_concurrency 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'maintenance_io_concurrency'
  properties: {
    value: '10'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_maintenance_work_mem 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'maintenance_work_mem'
  properties: {
    value: '157696'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_connections 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_connections'
  properties: {
    value: '429'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_files_per_process 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_files_per_process'
  properties: {
    value: '1000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_function_args 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_function_args'
  properties: {
    value: '100'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_identifier_length 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_identifier_length'
  properties: {
    value: '63'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_index_keys 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_index_keys'
  properties: {
    value: '32'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_locks_per_transaction 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_locks_per_transaction'
  properties: {
    value: '64'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_logical_replication_workers 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_logical_replication_workers'
  properties: {
    value: '4'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_parallel_apply_workers_per_subscription 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_parallel_apply_workers_per_subscription'
  properties: {
    value: '2'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_parallel_maintenance_workers 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_parallel_maintenance_workers'
  properties: {
    value: '2'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_parallel_workers 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_parallel_workers'
  properties: {
    value: '8'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_parallel_workers_per_gather 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_parallel_workers_per_gather'
  properties: {
    value: '2'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_pred_locks_per_page 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_pred_locks_per_page'
  properties: {
    value: '2'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_pred_locks_per_relation 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_pred_locks_per_relation'
  properties: {
    value: '-2'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_pred_locks_per_transaction 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_pred_locks_per_transaction'
  properties: {
    value: '64'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_prepared_transactions 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_prepared_transactions'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_replication_slots 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_replication_slots'
  properties: {
    value: '10'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_slot_wal_keep_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_slot_wal_keep_size'
  properties: {
    value: '-1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_stack_depth 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_stack_depth'
  properties: {
    value: '2048'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_max_standby_archive_delay 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_standby_archive_delay'
  properties: {
    value: '30000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_standby_streaming_delay 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_standby_streaming_delay'
  properties: {
    value: '30000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_sync_workers_per_subscription 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_sync_workers_per_subscription'
  properties: {
    value: '2'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_wal_senders 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_wal_senders'
  properties: {
    value: '10'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_wal_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_wal_size'
  properties: {
    value: '2048'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_max_worker_processes 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'max_worker_processes'
  properties: {
    value: '8'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_metrics_autovacuum_diagnostics 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'metrics.autovacuum_diagnostics'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_metrics_collector_database_activity 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'metrics.collector_database_activity'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_metrics_pgbouncer_diagnostics 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'metrics.pgbouncer_diagnostics'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_min_dynamic_shared_memory 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'min_dynamic_shared_memory'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_min_parallel_index_scan_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'min_parallel_index_scan_size'
  properties: {
    value: '64'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_min_parallel_table_scan_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'min_parallel_table_scan_size'
  properties: {
    value: '1024'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_min_wal_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'min_wal_size'
  properties: {
    value: '80'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_old_snapshot_threshold 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'old_snapshot_threshold'
  properties: {
    value: '-1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_parallel_leader_participation 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'parallel_leader_participation'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_parallel_setup_cost 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'parallel_setup_cost'
  properties: {
    value: '1000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_parallel_tuple_cost 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'parallel_tuple_cost'
  properties: {
    value: '0.1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_password_encryption 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'password_encryption'
  properties: {
    value: 'scram-sha-256'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_failover_slots_drop_extra_slots 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_failover_slots.drop_extra_slots'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_failover_slots_primary_dsn 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_failover_slots.primary_dsn'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_failover_slots_standby_slot_names 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_failover_slots.standby_slot_names'
  properties: {
    value: 'azure_standby_, wal_replica_'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_failover_slots_standby_slots_min_confirmed 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_failover_slots.standby_slots_min_confirmed'
  properties: {
    value: '1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_failover_slots_synchronize_slot_names 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_failover_slots.synchronize_slot_names'
  properties: {
    value: 'name_like:%%'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_failover_slots_version 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_failover_slots.version'
  properties: {
    value: '1.0.1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_failover_slots_wait_for_inactive_slots 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_failover_slots.wait_for_inactive_slots'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_hint_plan_debug_print 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_hint_plan.debug_print'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_hint_plan_enable_hint 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_hint_plan.enable_hint'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_hint_plan_enable_hint_table 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_hint_plan.enable_hint_table'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_hint_plan_hints_anywhere 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_hint_plan.hints_anywhere'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_hint_plan_message_level 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_hint_plan.message_level'
  properties: {
    value: 'log'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_hint_plan_parse_messages 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_hint_plan.parse_messages'
  properties: {
    value: 'info'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_partman_bgw_analyze 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_partman_bgw.analyze'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_partman_bgw_dbname 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_partman_bgw.dbname'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_partman_bgw_interval 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_partman_bgw.interval'
  properties: {
    value: '3600'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_partman_bgw_jobmon 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_partman_bgw.jobmon'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_partman_bgw_maintenance_wait 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_partman_bgw.maintenance_wait'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_partman_bgw_role 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_partman_bgw.role'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_prewarm_autoprewarm 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_prewarm.autoprewarm'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_prewarm_autoprewarm_interval 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_prewarm.autoprewarm_interval'
  properties: {
    value: '300'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_qs_emit_query_text 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_qs.emit_query_text'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_qs_interval_length_minutes 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_qs.interval_length_minutes'
  properties: {
    value: '15'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_qs_is_enabled_fs 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_qs.is_enabled_fs'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_qs_max_captured_queries 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_qs.max_captured_queries'
  properties: {
    value: '500'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_qs_max_plan_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_qs.max_plan_size'
  properties: {
    value: '7500'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_qs_max_query_text_length 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_qs.max_query_text_length'
  properties: {
    value: '6000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_qs_parameters_capture_mode 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_qs.parameters_capture_mode'
  properties: {
    value: 'capture_parameterless_only'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_qs_query_capture_mode 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_qs.query_capture_mode'
  properties: {
    value: 'none'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_qs_retention_period_in_days 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_qs.retention_period_in_days'
  properties: {
    value: '7'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_qs_store_query_plans 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_qs.store_query_plans'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_qs_track_utility 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_qs.track_utility'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_stat_statements_max 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_stat_statements.max'
  properties: {
    value: '5000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_stat_statements_save 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_stat_statements.save'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_stat_statements_track 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_stat_statements.track'
  properties: {
    value: 'none'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_stat_statements_track_planning 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_stat_statements.track_planning'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pg_stat_statements_track_utility 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pg_stat_statements.track_utility'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pgaadauth_enable_group_sync 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pgaadauth.enable_group_sync'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pgaudit_log 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pgaudit.log'
  properties: {
    value: 'none'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pgaudit_log_catalog 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pgaudit.log_catalog'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pgaudit_log_client 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pgaudit.log_client'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pgaudit_log_level 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pgaudit.log_level'
  properties: {
    value: 'log'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pgaudit_log_parameter 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pgaudit.log_parameter'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pgaudit_log_parameter_max_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pgaudit.log_parameter_max_size'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pgaudit_log_relation 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pgaudit.log_relation'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pgaudit_log_rows 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pgaudit.log_rows'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pgaudit_log_statement 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pgaudit.log_statement'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pgaudit_log_statement_once 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pgaudit.log_statement_once'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pgaudit_role 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pgaudit.role'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pglogical_batch_inserts 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pglogical.batch_inserts'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pglogical_conflict_log_level 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pglogical.conflict_log_level'
  properties: {
    value: 'log'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pglogical_conflict_resolution 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pglogical.conflict_resolution'
  properties: {
    value: 'apply_remote'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pglogical_extra_connection_options 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pglogical.extra_connection_options'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pglogical_synchronous_commit 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pglogical.synchronous_commit'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pglogical_temp_directory 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pglogical.temp_directory'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pglogical_use_spi 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pglogical.use_spi'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pgms_stats_is_enabled_fs 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pgms_stats.is_enabled_fs'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pgms_wait_sampling_history_period 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pgms_wait_sampling.history_period'
  properties: {
    value: '100'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pgms_wait_sampling_is_enabled_fs 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pgms_wait_sampling.is_enabled_fs'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pgms_wait_sampling_query_capture_mode 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pgms_wait_sampling.query_capture_mode'
  properties: {
    value: 'none'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plan_cache_mode 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plan_cache_mode'
  properties: {
    value: 'auto'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plpgsql_check_compatibility_warnings 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plpgsql_check.compatibility_warnings'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plpgsql_check_constants_tracing 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plpgsql_check.constants_tracing'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plpgsql_check_cursors_leaks 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plpgsql_check.cursors_leaks'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plpgsql_check_cursors_leaks_errlevel 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plpgsql_check.cursors_leaks_errlevel'
  properties: {
    value: 'warning'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plpgsql_check_enable_tracer 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plpgsql_check.enable_tracer'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plpgsql_check_fatal_errors 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plpgsql_check.fatal_errors'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plpgsql_check_mode 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plpgsql_check.mode'
  properties: {
    value: 'by_function'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plpgsql_check_profiler 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plpgsql_check.profiler'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plpgsql_check_profiler_max_shared_chunks 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plpgsql_check.profiler_max_shared_chunks'
  properties: {
    value: '15000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plpgsql_check_regress_test_mode 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plpgsql_check.regress_test_mode'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plpgsql_check_show_nonperformance_extra_warnings 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plpgsql_check.show_nonperformance_extra_warnings'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plpgsql_check_show_nonperformance_warnings 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plpgsql_check.show_nonperformance_warnings'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plpgsql_check_show_performance_warnings 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plpgsql_check.show_performance_warnings'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plpgsql_check_strict_cursors_leaks 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plpgsql_check.strict_cursors_leaks'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plpgsql_check_trace_assert 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plpgsql_check.trace_assert'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plpgsql_check_trace_assert_verbosity 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plpgsql_check.trace_assert_verbosity'
  properties: {
    value: 'default'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plpgsql_check_tracer 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plpgsql_check.tracer'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plpgsql_check_tracer_errlevel 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plpgsql_check.tracer_errlevel'
  properties: {
    value: 'notice'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plpgsql_check_tracer_show_nsubxids 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plpgsql_check.tracer_show_nsubxids'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plpgsql_check_tracer_test_mode 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plpgsql_check.tracer_test_mode'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plpgsql_check_tracer_variable_max_length 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plpgsql_check.tracer_variable_max_length'
  properties: {
    value: '1024'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_plpgsql_check_tracer_verbosity 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'plpgsql_check.tracer_verbosity'
  properties: {
    value: 'default'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_port 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'port'
  properties: {
    value: '5432'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_post_auth_delay 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'post_auth_delay'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_postgis_gdal_enabled_drivers 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'postgis.gdal_enabled_drivers'
  properties: {
    value: 'DISABLE_ALL'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_pre_auth_delay 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'pre_auth_delay'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_primary_conninfo 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'primary_conninfo'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_primary_slot_name 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'primary_slot_name'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_quote_all_identifiers 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'quote_all_identifiers'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_random_page_cost 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'random_page_cost'
  properties: {
    value: '2'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_agent_FP_bit_ratio 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.agent_FP_bit_ratio'
  properties: {
    value: '0.2'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_avalon_fp_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.avalon_fp_size'
  properties: {
    value: '512'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_dice_threshold 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.dice_threshold'
  properties: {
    value: '0.5'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_difference_FP_weight_agents 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.difference_FP_weight_agents'
  properties: {
    value: '1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_difference_FP_weight_nonagents 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.difference_FP_weight_nonagents'
  properties: {
    value: '10'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_do_chiral_sss 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.do_chiral_sss'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_do_enhanced_stereo_sss 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.do_enhanced_stereo_sss'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_featmorgan_fp_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.featmorgan_fp_size'
  properties: {
    value: '512'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_hashed_atompair_fp_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.hashed_atompair_fp_size'
  properties: {
    value: '2048'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_hashed_torsion_fp_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.hashed_torsion_fp_size'
  properties: {
    value: '1024'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_ignore_reaction_agents 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.ignore_reaction_agents'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_init_reaction 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.init_reaction'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_layered_fp_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.layered_fp_size'
  properties: {
    value: '1024'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_morgan_fp_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.morgan_fp_size'
  properties: {
    value: '512'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_move_unmmapped_reactants_to_agents 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.move_unmmapped_reactants_to_agents'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_rdkit_fp_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.rdkit_fp_size'
  properties: {
    value: '1024'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_reaction_difference_fp_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.reaction_difference_fp_size'
  properties: {
    value: '2048'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_reaction_difference_fp_type 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.reaction_difference_fp_type'
  properties: {
    value: '1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_reaction_sss_fp_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.reaction_sss_fp_size'
  properties: {
    value: '4096'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_reaction_sss_fp_type 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.reaction_sss_fp_type'
  properties: {
    value: '5'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_sss_fp_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.sss_fp_size'
  properties: {
    value: '2048'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_tanimoto_threshold 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.tanimoto_threshold'
  properties: {
    value: '0.5'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_rdkit_threshold_unmapped_reactant_atoms 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'rdkit.threshold_unmapped_reactant_atoms'
  properties: {
    value: '0.2'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_recovery_end_command 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'recovery_end_command'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_recovery_init_sync_method 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'recovery_init_sync_method'
  properties: {
    value: 'fsync'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_recovery_min_apply_delay 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'recovery_min_apply_delay'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_recovery_prefetch 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'recovery_prefetch'
  properties: {
    value: 'try'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_recovery_target 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'recovery_target'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_recovery_target_action 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'recovery_target_action'
  properties: {
    value: 'pause'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_recovery_target_inclusive 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'recovery_target_inclusive'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_recovery_target_lsn 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'recovery_target_lsn'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_recovery_target_name 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'recovery_target_name'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_recovery_target_time 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'recovery_target_time'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_recovery_target_timeline 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'recovery_target_timeline'
  properties: {
    value: 'latest'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_recovery_target_xid 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'recovery_target_xid'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_recursive_worktable_factor 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'recursive_worktable_factor'
  properties: {
    value: '10'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_remove_temp_files_after_crash 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'remove_temp_files_after_crash'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_require_secure_transport 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'require_secure_transport'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_reserved_connections 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'reserved_connections'
  properties: {
    value: '5'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_restart_after_crash 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'restart_after_crash'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_restore_command 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'restore_command'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_restrict_nonsystem_relation_kind 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'restrict_nonsystem_relation_kind'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_row_security 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'row_security'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_scram_iterations 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'scram_iterations'
  properties: {
    value: '4096'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_search_path 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'search_path'
  properties: {
    value: '"$user", public'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_segment_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'segment_size'
  properties: {
    value: '131072'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_send_abort_for_crash 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'send_abort_for_crash'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_send_abort_for_kill 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'send_abort_for_kill'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_seq_page_cost 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'seq_page_cost'
  properties: {
    value: '1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_server_encoding 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'server_encoding'
  properties: {
    value: 'UTF8'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_server_version 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'server_version'
  properties: {
    value: '16.14'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_server_version_num 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'server_version_num'
  properties: {
    value: '160014'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_session_preload_libraries 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'session_preload_libraries'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_session_replication_role 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'session_replication_role'
  properties: {
    value: 'origin'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_shared_buffers 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'shared_buffers'
  properties: {
    value: '131072'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_shared_memory_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'shared_memory_size'
  properties: {
    value: '1125'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_shared_memory_size_in_huge_pages 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'shared_memory_size_in_huge_pages'
  properties: {
    value: '563'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_shared_memory_type 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'shared_memory_type'
  properties: {
    value: 'mmap'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_shared_preload_libraries 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'shared_preload_libraries'
  properties: {
    value: 'pg_cron,pg_stat_statements'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_squeeze_max_xlock_time 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'squeeze.max_xlock_time'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_squeeze_worker_autostart 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'squeeze.worker_autostart'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_squeeze_worker_role 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'squeeze.worker_role'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_squeeze_workers_per_database 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'squeeze.workers_per_database'
  properties: {
    value: '1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_ssl 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'ssl'
  properties: {
    value: 'on'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_ssl_ca_file 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'ssl_ca_file'
  properties: {
    value: '/datadrive/certs/ca.pem'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_ssl_cert_file 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'ssl_cert_file'
  properties: {
    value: '/datadrive/certs/cert.pem'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_ssl_ciphers 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'ssl_ciphers'
  properties: {
    value: 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_ssl_crl_dir 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'ssl_crl_dir'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_ssl_crl_file 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'ssl_crl_file'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_ssl_dh_params_file 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'ssl_dh_params_file'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_ssl_ecdh_curve 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'ssl_ecdh_curve'
  properties: {
    value: 'prime256v1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_ssl_key_file 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'ssl_key_file'
  properties: {
    value: '/datadrive/certs/key.pem'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_ssl_library 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'ssl_library'
  properties: {
    value: 'OpenSSL'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_ssl_max_protocol_version 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'ssl_max_protocol_version'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_ssl_min_protocol_version 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'ssl_min_protocol_version'
  properties: {
    value: 'TLSv1.2'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_ssl_passphrase_command 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'ssl_passphrase_command'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_ssl_passphrase_command_supports_reload 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'ssl_passphrase_command_supports_reload'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_ssl_prefer_server_ciphers 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'ssl_prefer_server_ciphers'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_standard_conforming_strings 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'standard_conforming_strings'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_statement_timeout 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'statement_timeout'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_stats_fetch_consistency 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'stats_fetch_consistency'
  properties: {
    value: 'cache'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_superuser_reserved_connections 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'superuser_reserved_connections'
  properties: {
    value: '10'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_synchronize_seqscans 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'synchronize_seqscans'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_synchronous_commit 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'synchronous_commit'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_synchronous_standby_names 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'synchronous_standby_names'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_syslog_facility 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'syslog_facility'
  properties: {
    value: 'local0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_syslog_ident 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'syslog_ident'
  properties: {
    value: 'postgres'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_syslog_sequence_numbers 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'syslog_sequence_numbers'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_syslog_split_messages 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'syslog_split_messages'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_tcp_keepalives_count 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'tcp_keepalives_count'
  properties: {
    value: '9'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_tcp_keepalives_idle 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'tcp_keepalives_idle'
  properties: {
    value: '120'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_tcp_keepalives_interval 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'tcp_keepalives_interval'
  properties: {
    value: '30'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_tcp_user_timeout 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'tcp_user_timeout'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_temp_buffers 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'temp_buffers'
  properties: {
    value: '1024'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_temp_file_limit 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'temp_file_limit'
  properties: {
    value: '-1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_temp_tablespaces 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'temp_tablespaces'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_timescaledb_bgw_launcher_poll_time 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'timescaledb.bgw_launcher_poll_time'
  properties: {
    value: '60000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_timescaledb_disable_load 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'timescaledb.disable_load'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_timescaledb_max_background_workers 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'timescaledb.max_background_workers'
  properties: {
    value: '16'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_timescaledb_osm_disable_load 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'timescaledb_osm.disable_load'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_TimeZone 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'TimeZone'
  properties: {
    value: 'UTC'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_timezone_abbreviations 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'timezone_abbreviations'
  properties: {
    value: 'Default'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_trace_notify 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'trace_notify'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_trace_recovery_messages 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'trace_recovery_messages'
  properties: {
    value: 'log'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_trace_sort 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'trace_sort'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_track_activities 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'track_activities'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_track_activity_query_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'track_activity_query_size'
  properties: {
    value: '1024'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_track_commit_timestamp 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'track_commit_timestamp'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_track_counts 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'track_counts'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_track_functions 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'track_functions'
  properties: {
    value: 'none'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_track_io_timing 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'track_io_timing'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_track_wal_io_timing 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'track_wal_io_timing'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_transaction_deferrable 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'transaction_deferrable'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_transaction_isolation 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'transaction_isolation'
  properties: {
    value: 'read committed'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_transaction_read_only 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'transaction_read_only'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_transform_null_equals 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'transform_null_equals'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_unix_socket_directories 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'unix_socket_directories'
  properties: {
    value: '/tmp,/tmp/tuning_sockets'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_unix_socket_group 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'unix_socket_group'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_unix_socket_permissions 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'unix_socket_permissions'
  properties: {
    value: '0777'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_update_process_title 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'update_process_title'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_vacuum_buffer_usage_limit 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'vacuum_buffer_usage_limit'
  properties: {
    value: '256'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_vacuum_cost_delay 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'vacuum_cost_delay'
  properties: {
    value: '0'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_vacuum_cost_limit 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'vacuum_cost_limit'
  properties: {
    value: '200'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_vacuum_cost_page_dirty 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'vacuum_cost_page_dirty'
  properties: {
    value: '20'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_vacuum_cost_page_hit 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'vacuum_cost_page_hit'
  properties: {
    value: '1'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_vacuum_cost_page_miss 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'vacuum_cost_page_miss'
  properties: {
    value: '10'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_vacuum_failsafe_age 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'vacuum_failsafe_age'
  properties: {
    value: '1600000000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_vacuum_freeze_min_age 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'vacuum_freeze_min_age'
  properties: {
    value: '50000000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_vacuum_freeze_table_age 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'vacuum_freeze_table_age'
  properties: {
    value: '150000000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_vacuum_multixact_failsafe_age 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'vacuum_multixact_failsafe_age'
  properties: {
    value: '1600000000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_vacuum_multixact_freeze_min_age 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'vacuum_multixact_freeze_min_age'
  properties: {
    value: '5000000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_vacuum_multixact_freeze_table_age 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'vacuum_multixact_freeze_table_age'
  properties: {
    value: '150000000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_wal_block_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'wal_block_size'
  properties: {
    value: '8192'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_wal_buffers 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'wal_buffers'
  properties: {
    value: '2048'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_wal_compression 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'wal_compression'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_wal_consistency_checking 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'wal_consistency_checking'
  properties: {
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_wal_decode_buffer_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'wal_decode_buffer_size'
  properties: {
    value: '524288'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_wal_init_zero 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'wal_init_zero'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_wal_keep_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'wal_keep_size'
  properties: {
    value: '400'
    source: 'user-override'
  }
}

resource flexibleServers_dt4_postgresql_name_wal_level 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'wal_level'
  properties: {
    value: 'replica'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_wal_log_hints 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'wal_log_hints'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_wal_receiver_create_temp_slot 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'wal_receiver_create_temp_slot'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_wal_receiver_status_interval 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'wal_receiver_status_interval'
  properties: {
    value: '10'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_wal_receiver_timeout 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'wal_receiver_timeout'
  properties: {
    value: '60000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_wal_recycle 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'wal_recycle'
  properties: {
    value: 'on'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_wal_retrieve_retry_interval 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'wal_retrieve_retry_interval'
  properties: {
    value: '5000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_wal_segment_size 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'wal_segment_size'
  properties: {
    value: '16777216'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_wal_sender_timeout 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'wal_sender_timeout'
  properties: {
    value: '60000'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_wal_skip_threshold 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'wal_skip_threshold'
  properties: {
    value: '2048'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_wal_sync_method 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'wal_sync_method'
  properties: {
    value: 'fdatasync'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_wal_writer_delay 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'wal_writer_delay'
  properties: {
    value: '200'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_wal_writer_flush_after 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'wal_writer_flush_after'
  properties: {
    value: '128'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_work_mem 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'work_mem'
  properties: {
    value: '4096'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_xmlbinary 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'xmlbinary'
  properties: {
    value: 'base64'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_xmloption 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'xmloption'
  properties: {
    value: 'content'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_zero_damaged_pages 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'zero_damaged_pages'
  properties: {
    value: 'off'
    source: 'system-default'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_maintenance 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure_maintenance'
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

resource flexibleServers_dt4_postgresql_name_azure_sys 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'azure_sys'
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

resource flexibleServers_dt4_postgresql_name_bioroute_db 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'bioroute_db'
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

resource flexibleServers_dt4_postgresql_name_postgres 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'postgres'
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

resource flexibleServers_dt4_postgresql_name_AllowAllAzureServicesAndResourcesWithinAzureIps_2026_6_29_9_51_46 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'AllowAllAzureServicesAndResourcesWithinAzureIps_2026-6-29_9-51-46'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

resource flexibleServers_dt4_postgresql_name_ClientIPAddress_2026_6_29_9_33_23 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'ClientIPAddress_2026-6-29_9-33-23'
  properties: {
    startIpAddress: '175.193.34.4'
    endIpAddress: '175.193.34.4'
  }
}

resource flexibleServers_dt4_postgresql_name_ehjeon 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'ehjeon'
  properties: {
    startIpAddress: '162.120.184.41'
    endIpAddress: '162.120.184.41'
  }
}

resource flexibleServers_dt4_postgresql_name_gyim 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'gyim'
  properties: {
    startIpAddress: '61.251.250.9'
    endIpAddress: '61.251.250.9'
  }
}

resource flexibleServers_dt4_postgresql_name_gyim_out 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'gyim_out'
  properties: {
    startIpAddress: '172.30.1.36'
    endIpAddress: '172.30.1.36'
  }
}

resource flexibleServers_dt4_postgresql_name_gyim_out2 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'gyim_out2'
  properties: {
    startIpAddress: '172.30.1.254'
    endIpAddress: '172.30.1.254'
  }
}

resource flexibleServers_dt4_postgresql_name_gyim_out3 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'gyim_out3'
  properties: {
    startIpAddress: '175.192.75.38'
    endIpAddress: '175.192.75.38'
  }
}

resource flexibleServers_dt4_postgresql_name_jwlee 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'jwlee'
  properties: {
    startIpAddress: '124.5.119.193'
    endIpAddress: '124.5.119.193'
  }
}

resource flexibleServers_dt4_postgresql_name_smseo 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'smseo'
  properties: {
    startIpAddress: '14.6.122.176'
    endIpAddress: '14.6.122.176'
  }
}

resource flexibleServers_dt4_postgresql_name_ynlee 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'ynlee'
  properties: {
    startIpAddress: '172.30.1.72'
    endIpAddress: '172.30.1.72'
  }
}

resource flexibleServers_dt4_postgresql_name_yunaleeClientIPAddress_2026_6_29_16_53_41 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2026-01-01-preview' = {
  parent: flexibleServers_dt4_postgresql_name_resource
  name: 'yunaleeClientIPAddress_2026-6-29_16-53-41'
  properties: {
    startIpAddress: '175.204.77.87'
    endIpAddress: '175.204.77.87'
  }
}

resource components_dt4_team1_func_collector_name_degradationindependencyduration 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_dt4_team1_func_collector_name_resource
  name: 'degradationindependencyduration'
  location: 'koreacentral'
  properties: {
    ruleDefinitions: {
      Name: 'degradationindependencyduration'
      DisplayName: 'Degradation in dependency duration'
      Description: 'Smart Detection rules notify you of performance anomaly issues.'
      HelpUrl: 'https://docs.microsoft.com/en-us/azure/application-insights/app-insights-proactive-performance-diagnostics'
      IsHidden: false
      IsEnabledByDefault: true
      IsInPreview: false
      SupportsEmailNotifications: true
    }
    enabled: true
    sendEmailsToSubscriptionOwners: true
    customEmails: []
  }
}

resource components_dt4_team1_func_collector_name_degradationinserverresponsetime 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_dt4_team1_func_collector_name_resource
  name: 'degradationinserverresponsetime'
  location: 'koreacentral'
  properties: {
    ruleDefinitions: {
      Name: 'degradationinserverresponsetime'
      DisplayName: 'Degradation in server response time'
      Description: 'Smart Detection rules notify you of performance anomaly issues.'
      HelpUrl: 'https://docs.microsoft.com/en-us/azure/application-insights/app-insights-proactive-performance-diagnostics'
      IsHidden: false
      IsEnabledByDefault: true
      IsInPreview: false
      SupportsEmailNotifications: true
    }
    enabled: true
    sendEmailsToSubscriptionOwners: true
    customEmails: []
  }
}

resource components_dt4_team1_func_collector_name_digestMailConfiguration 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_dt4_team1_func_collector_name_resource
  name: 'digestMailConfiguration'
  location: 'koreacentral'
  properties: {
    ruleDefinitions: {
      Name: 'digestMailConfiguration'
      DisplayName: 'Digest Mail Configuration'
      Description: 'This rule describes the digest mail preferences'
      HelpUrl: 'www.homail.com'
      IsHidden: true
      IsEnabledByDefault: true
      IsInPreview: false
      SupportsEmailNotifications: true
    }
    enabled: true
    sendEmailsToSubscriptionOwners: true
    customEmails: []
  }
}

resource components_dt4_team1_func_collector_name_extension_billingdatavolumedailyspikeextension 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_dt4_team1_func_collector_name_resource
  name: 'extension_billingdatavolumedailyspikeextension'
  location: 'koreacentral'
  properties: {
    ruleDefinitions: {
      Name: 'extension_billingdatavolumedailyspikeextension'
      DisplayName: 'Abnormal rise in daily data volume (preview)'
      Description: 'This detection rule automatically analyzes the billing data generated by your application, and can warn you about an unusual increase in your application\'s billing costs'
      HelpUrl: 'https://github.com/Microsoft/ApplicationInsights-Home/tree/master/SmartDetection/billing-data-volume-daily-spike.md'
      IsHidden: false
      IsEnabledByDefault: true
      IsInPreview: true
      SupportsEmailNotifications: false
    }
    enabled: true
    sendEmailsToSubscriptionOwners: true
    customEmails: []
  }
}

resource components_dt4_team1_func_collector_name_extension_canaryextension 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_dt4_team1_func_collector_name_resource
  name: 'extension_canaryextension'
  location: 'koreacentral'
  properties: {
    ruleDefinitions: {
      Name: 'extension_canaryextension'
      DisplayName: 'Canary extension'
      Description: 'Canary extension'
      HelpUrl: 'https://github.com/Microsoft/ApplicationInsights-Home/blob/master/SmartDetection/'
      IsHidden: true
      IsEnabledByDefault: true
      IsInPreview: true
      SupportsEmailNotifications: false
    }
    enabled: true
    sendEmailsToSubscriptionOwners: true
    customEmails: []
  }
}

resource components_dt4_team1_func_collector_name_extension_exceptionchangeextension 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_dt4_team1_func_collector_name_resource
  name: 'extension_exceptionchangeextension'
  location: 'koreacentral'
  properties: {
    ruleDefinitions: {
      Name: 'extension_exceptionchangeextension'
      DisplayName: 'Abnormal rise in exception volume (preview)'
      Description: 'This detection rule automatically analyzes the exceptions thrown in your application, and can warn you about unusual patterns in your exception telemetry.'
      HelpUrl: 'https://github.com/Microsoft/ApplicationInsights-Home/blob/master/SmartDetection/abnormal-rise-in-exception-volume.md'
      IsHidden: false
      IsEnabledByDefault: true
      IsInPreview: true
      SupportsEmailNotifications: false
    }
    enabled: true
    sendEmailsToSubscriptionOwners: true
    customEmails: []
  }
}

resource components_dt4_team1_func_collector_name_extension_memoryleakextension 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_dt4_team1_func_collector_name_resource
  name: 'extension_memoryleakextension'
  location: 'koreacentral'
  properties: {
    ruleDefinitions: {
      Name: 'extension_memoryleakextension'
      DisplayName: 'Potential memory leak detected (preview)'
      Description: 'This detection rule automatically analyzes the memory consumption of each process in your application, and can warn you about potential memory leaks or increased memory consumption.'
      HelpUrl: 'https://github.com/Microsoft/ApplicationInsights-Home/tree/master/SmartDetection/memory-leak.md'
      IsHidden: false
      IsEnabledByDefault: true
      IsInPreview: true
      SupportsEmailNotifications: false
    }
    enabled: true
    sendEmailsToSubscriptionOwners: true
    customEmails: []
  }
}

resource components_dt4_team1_func_collector_name_extension_securityextensionspackage 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_dt4_team1_func_collector_name_resource
  name: 'extension_securityextensionspackage'
  location: 'koreacentral'
  properties: {
    ruleDefinitions: {
      Name: 'extension_securityextensionspackage'
      DisplayName: 'Potential security issue detected (preview)'
      Description: 'This detection rule automatically analyzes the telemetry generated by your application and detects potential security issues.'
      HelpUrl: 'https://github.com/Microsoft/ApplicationInsights-Home/blob/master/SmartDetection/application-security-detection-pack.md'
      IsHidden: false
      IsEnabledByDefault: true
      IsInPreview: true
      SupportsEmailNotifications: false
    }
    enabled: true
    sendEmailsToSubscriptionOwners: true
    customEmails: []
  }
}

resource components_dt4_team1_func_collector_name_extension_traceseveritydetector 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_dt4_team1_func_collector_name_resource
  name: 'extension_traceseveritydetector'
  location: 'koreacentral'
  properties: {
    ruleDefinitions: {
      Name: 'extension_traceseveritydetector'
      DisplayName: 'Degradation in trace severity ratio (preview)'
      Description: 'This detection rule automatically analyzes the trace logs emitted from your application, and can warn you about unusual patterns in the severity of your trace telemetry.'
      HelpUrl: 'https://github.com/Microsoft/ApplicationInsights-Home/blob/master/SmartDetection/degradation-in-trace-severity-ratio.md'
      IsHidden: false
      IsEnabledByDefault: true
      IsInPreview: true
      SupportsEmailNotifications: false
    }
    enabled: true
    sendEmailsToSubscriptionOwners: true
    customEmails: []
  }
}

resource components_dt4_team1_func_collector_name_longdependencyduration 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_dt4_team1_func_collector_name_resource
  name: 'longdependencyduration'
  location: 'koreacentral'
  properties: {
    ruleDefinitions: {
      Name: 'longdependencyduration'
      DisplayName: 'Long dependency duration'
      Description: 'Smart Detection rules notify you of performance anomaly issues.'
      HelpUrl: 'https://docs.microsoft.com/en-us/azure/application-insights/app-insights-proactive-performance-diagnostics'
      IsHidden: false
      IsEnabledByDefault: true
      IsInPreview: false
      SupportsEmailNotifications: true
    }
    enabled: true
    sendEmailsToSubscriptionOwners: true
    customEmails: []
  }
}

resource components_dt4_team1_func_collector_name_migrationToAlertRulesCompleted 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_dt4_team1_func_collector_name_resource
  name: 'migrationToAlertRulesCompleted'
  location: 'koreacentral'
  properties: {
    ruleDefinitions: {
      Name: 'migrationToAlertRulesCompleted'
      DisplayName: 'Migration To Alert Rules Completed'
      Description: 'A configuration that controls the migration state of Smart Detection to Smart Alerts'
      HelpUrl: 'https://docs.microsoft.com/en-us/azure/application-insights/app-insights-proactive-performance-diagnostics'
      IsHidden: true
      IsEnabledByDefault: false
      IsInPreview: true
      SupportsEmailNotifications: false
    }
    enabled: false
    sendEmailsToSubscriptionOwners: true
    customEmails: []
  }
}

resource components_dt4_team1_func_collector_name_slowpageloadtime 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_dt4_team1_func_collector_name_resource
  name: 'slowpageloadtime'
  location: 'koreacentral'
  properties: {
    ruleDefinitions: {
      Name: 'slowpageloadtime'
      DisplayName: 'Slow page load time'
      Description: 'Smart Detection rules notify you of performance anomaly issues.'
      HelpUrl: 'https://docs.microsoft.com/en-us/azure/application-insights/app-insights-proactive-performance-diagnostics'
      IsHidden: false
      IsEnabledByDefault: true
      IsInPreview: false
      SupportsEmailNotifications: true
    }
    enabled: true
    sendEmailsToSubscriptionOwners: true
    customEmails: []
  }
}

resource components_dt4_team1_func_collector_name_slowserverresponsetime 'microsoft.insights/components/ProactiveDetectionConfigs@2018-05-01-preview' = {
  parent: components_dt4_team1_func_collector_name_resource
  name: 'slowserverresponsetime'
  location: 'koreacentral'
  properties: {
    ruleDefinitions: {
      Name: 'slowserverresponsetime'
      DisplayName: 'Slow server response time'
      Description: 'Smart Detection rules notify you of performance anomaly issues.'
      HelpUrl: 'https://docs.microsoft.com/en-us/azure/application-insights/app-insights-proactive-performance-diagnostics'
      IsHidden: false
      IsEnabledByDefault: true
      IsInPreview: false
      SupportsEmailNotifications: true
    }
    enabled: true
    sendEmailsToSubscriptionOwners: true
    customEmails: []
  }
}

resource workflows_dt4_team1_alert_logicapps_name_resource 'Microsoft.Logic/workflows@2017-07-01' = {
  name: workflows_dt4_team1_alert_logicapps_name
  location: 'northcentralus'
  properties: {
    state: 'Enabled'
    definition: {
      metadata: {
        notes: {
          'C8E7F1F3-A5A7-4808-8815-E355B5239F22': {
            content: '웹후크 출처에 따른 분기\n\nCondition : \n\n- workspace_id의 유무에 따라 출처가 데이터브릭스인지 판단(느슨한 기준)\n\n- '
            color: '#FFFBCC'
            metadata: {
              position: {
                x: -200
                y: 200
              }
              width: 200
              height: 184
            }
          }
          'F0A0D58F-4F93-4388-A139-3F4803E2449F': {
            content: 'Databricks용 알림 분기\nevent_type으로 작업 시작 / 성공 / 실패 여부 분기'
            color: '#FFFBCC'
            metadata: {
              position: {
                x: -220
                y: 500
              }
              width: 200
              height: 84
            }
          }
        }
      }
      '$schema': 'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#'
      contentVersion: '1.0.0.0'
      parameters: {
        '$connections': {
          defaultValue: {}
          type: 'Object'
        }
      }
      triggers: {
        When_an_HTTP_request_is_received: {
          type: 'Request'
          kind: 'Http'
        }
      }
      actions: {
        '메시지_출처_분기': {
          actions: {
            '실패_여부_분기': {
              actions: {
                '채팅_또는_채널에서_메시지_게시': {
                  type: 'ApiConnection'
                  inputs: {
                    host: {
                      connection: {
                        name: '@parameters(\'$connections\')[\'teams-1\'][\'connectionId\']'
                      }
                    }
                    method: 'post'
                    body: {
                      recipient: {
                        groupId: 'd3a3c7bf-dcb4-4dcf-a4bb-b50b18b953df'
                        channelId: '19:I-nJwkHX6lGsGrsUHSSDh30emSkpFAHpZpNqGO_ugIM1@thread.tacv2'
                      }
                      messageBody: '<p class="editor-paragraph"><b><strong class="editor-text-bold" style="font-size: 20px;">🚨 [</strong></b><b><strong class="editor-text-bold" style="font-size: 20px;">System Alert</strong></b><b><strong class="editor-text-bold" style="font-size: 20px;">] Databricks 파이프라인 작업 실패 알림</strong></b></p><p class="editor-paragraph"><br>데이터 파이프라인 수행 중 오류가 발생하여 작업이 중단되었습니다. 상세 내용을 확인 후 조치해 주시기 바랍니다.</p><p class="editor-paragraph"><br>- 작업 이름 (Job Name): @{body(\'Databricks_메시지_파싱\')?[\'job\']?[\'name\']}<br>- 워크스페이스 ID (Workspace ID): @{body(\'Databricks_메시지_파싱\')?[\'workspace_id\']}<br>- 작업 ID (Job ID): @{body(\'Databricks_메시지_파싱\')?[\'job\']?[\'job_id\']}<br>- 실행 ID (Run ID): @{body(\'Databricks_메시지_파싱\')?[\'run\']?[\'run_id\']}</p>'
                    }
                    path: '/beta/teams/conversation/message/poster/@{encodeURIComponent(\'Flow bot\')}/location/@{encodeURIComponent(\'Channel\')}'
                  }
                }
              }
              runAfter: {
                'Databricks_메시지_파싱': [
                  'Succeeded'
                ]
              }
              else: {
                actions: {
                  '성공시작_여부_분기': {
                    actions: {
                      '채팅_또는_채널에서_메시지_게시_1': {
                        type: 'ApiConnection'
                        inputs: {
                          host: {
                            connection: {
                              name: '@parameters(\'$connections\')[\'teams-3\'][\'connectionId\']'
                            }
                          }
                          method: 'post'
                          body: {
                            recipient: {
                              groupId: 'd3a3c7bf-dcb4-4dcf-a4bb-b50b18b953df'
                              channelId: '19:I-nJwkHX6lGsGrsUHSSDh30emSkpFAHpZpNqGO_ugIM1@thread.tacv2'
                            }
                            messageBody: '<p class="editor-paragraph">✅<b><strong class="editor-text-bold" style="font-size: 20px;"> [System Alert] Databricks 파이프라인 작업 성공 알림</strong></b></p><br><p class="editor-paragraph">작업을 완료했습니다.</p><p class="editor-paragraph"><br>- 작업 이름 (Job Name): @{body(\'Databricks_메시지_파싱\')?[\'job\']?[\'name\']}<br>- 워크스페이스 ID (Workspace ID): @{body(\'Databricks_메시지_파싱\')?[\'workspace_id\']}<br>- 작업 ID (Job ID): @{body(\'Databricks_메시지_파싱\')?[\'job\']?[\'job_id\']}<br>- 실행 ID (Run ID): @{body(\'Databricks_메시지_파싱\')?[\'run\']?[\'run_id\']}</p>'
                          }
                          path: '/beta/teams/conversation/message/poster/Flow bot/location/@{encodeURIComponent(\'Channel\')}'
                        }
                      }
                    }
                    else: {
                      actions: {
                        '채팅_또는_채널에서_메시지_게시_2': {
                          type: 'ApiConnection'
                          inputs: {
                            host: {
                              connection: {
                                name: '@parameters(\'$connections\')[\'teams-3\'][\'connectionId\']'
                              }
                            }
                            method: 'post'
                            body: {
                              recipient: {
                                groupId: 'd3a3c7bf-dcb4-4dcf-a4bb-b50b18b953df'
                                channelId: '19:I-nJwkHX6lGsGrsUHSSDh30emSkpFAHpZpNqGO_ugIM1@thread.tacv2'
                              }
                              messageBody: '<p class="editor-paragraph"><b><strong class="editor-text-bold" style="font-size: 20px;">✈️ [System Alert] Databricks 파이프라인 작업 시작 알림</strong></b><br></p><br><p class="editor-paragraph">작업을 시작합니다.</p><br><p class="editor-paragraph">- 작업 이름 (Job Name): @{body(\'Databricks_메시지_파싱\')?[\'job\']?[\'name\']}<br>- 워크스페이스 ID (Workspace ID): @{body(\'Databricks_메시지_파싱\')?[\'workspace_id\']}<br>- 작업 ID (Job ID): @{body(\'Databricks_메시지_파싱\')?[\'job\']?[\'job_id\']}<br>- 실행 ID (Run ID): @{body(\'Databricks_메시지_파싱\')?[\'run\']?[\'run_id\']}</p>'
                            }
                            path: '/beta/teams/conversation/message/poster/Flow bot/location/@{encodeURIComponent(\'Channel\')}'
                          }
                        }
                      }
                    }
                    expression: {
                      and: [
                        {
                          equals: [
                            '@body(\'Databricks_메시지_파싱\')?[\'event_type\']'
                            'jobs.on_success'
                          ]
                        }
                      ]
                    }
                    type: 'If'
                  }
                }
              }
              expression: {
                and: [
                  {
                    equals: [
                      '@body(\'Databricks_메시지_파싱\')?[\'event_type\']'
                      'jobs.on_failure'
                    ]
                  }
                ]
              }
              type: 'If'
            }
            'Databricks_메시지_파싱': {
              type: 'ParseJson'
              inputs: {
                content: '@triggerBody()'
                schema: {
                  type: 'object'
                  properties: {
                    event_type: {
                      type: 'string'
                    }
                    workspace_id: {
                      type: 'integer'
                    }
                    run: {
                      type: 'object'
                      properties: {
                        run_id: {
                          type: 'integer'
                        }
                      }
                    }
                    job: {
                      type: 'object'
                      properties: {
                        job_id: {
                          type: 'integer'
                        }
                        name: {
                          type: 'string'
                        }
                      }
                    }
                  }
                }
              }
            }
          }
          runAfter: {}
          else: {
            actions: {
              'Function_메시지_파싱': {
                type: 'ParseJson'
                inputs: {
                  content: '@triggerBody()'
                  schema: {
                    type: 'object'
                    properties: {
                      data: {
                        type: 'object'
                        properties: {
                          essentials: {
                            type: 'object'
                            properties: {
                              alertRule: {
                                type: 'string'
                              }
                              severity: {
                                type: 'string'
                              }
                              monitorCondition: {
                                type: 'string'
                              }
                              firedDateTime: {
                                type: 'string'
                              }
                              investigationLink: {
                                type: 'string'
                              }
                              targetResourceGroup: {
                                type: 'string'
                              }
                              monitoringService: {
                                type: 'string'
                              }
                            }
                          }
                          alertContext: {
                            type: 'object'
                            properties: {
                              condition: {
                                type: 'object'
                                properties: {
                                  windowStartTime: {
                                    type: 'string'
                                  }
                                  windowEndTime: {
                                    type: 'string'
                                  }
                                  allOf: {
                                    type: 'array'
                                    items: {
                                      type: 'object'
                                      properties: {
                                        metricValue: {
                                          type: 'number'
                                        }
                                        dimensions: {
                                          type: 'array'
                                          items: {
                                            type: 'object'
                                            properties: {
                                              name: {
                                                type: 'string'
                                              }
                                              value: {
                                                type: 'string'
                                              }
                                            }
                                          }
                                        }
                                      }
                                    }
                                  }
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
              FilterFunctionName: {
                runAfter: {
                  'Function_메시지_파싱': [
                    'Succeeded'
                  ]
                }
                type: 'Query'
                inputs: {
                  from: '@body(\'Function_메시지_파싱\')?[\'data\']?[\'alertContext\']?[\'condition\']?[\'allOf\'][0]?[\'dimensions\']'
                  where: '@equals(item()?[\'name\'], \'functionName\')'
                }
              }
              FilterResultCode: {
                runAfter: {
                  FilterFunctionName: [
                    'Succeeded'
                  ]
                }
                type: 'Query'
                inputs: {
                  from: '@body(\'Function_메시지_파싱\')?[\'data\']?[\'alertContext\']?[\'condition\']?[\'allOf\'][0]?[\'dimensions\']'
                  where: '@equals(item()?[\'name\'], \'resultCode\')'
                }
              }
              Condition_1: {
                actions: {
                  '자신에게_메시지_게시': {
                    type: 'ApiConnection'
                    inputs: {
                      host: {
                        connection: {
                          name: '@parameters(\'$connections\')[\'teams-4\'][\'connectionId\']'
                        }
                      }
                      method: 'post'
                      body: {
                        body: {
                          content: '🚨 [System Alert] 수집 Function 성공\n\n데이터 수집에 성공하였습니다.\n\nFunction: @{first(body(\'FilterFunctionName\'))?[\'value\']}\n\n성공 시각: @{convertTimeZone(body(\'Function_메시지_파싱\')?[\'data\']?[\'essentials\']?[\'firedDateTime\'], \'UTC\', \'Korea Standard Time\', \'yyyy-MM-dd HH:mm:ss\')}'
                          contentType: 'text'
                        }
                      }
                      path: '/v1.0/chats/48:notes/messages'
                    }
                  }
                }
                runAfter: {
                  FilterResultCode: [
                    'Succeeded'
                  ]
                }
                else: {
                  actions: {}
                }
                expression: {
                  and: [
                    {
                      equals: [
                        'first(body(\'FilterResultCode\'))?[\'value\']'
                        200
                      ]
                    }
                  ]
                }
                type: 'If'
              }
            }
          }
          expression: {
            and: [
              {
                contains: [
                  '@triggerBody()'
                  'workspace_id'
                ]
              }
              {
                equals: [
                  ''
                  ''
                ]
              }
            ]
          }
          type: 'If'
        }
      }
      outputs: {}
    }
    parameters: {
      '$connections': {
        value: {
          'teams-1': {
            id: '/subscriptions/27db5ec6-d206-4028-b5e1-6004dca5eeef/providers/Microsoft.Web/locations/northcentralus/managedApis/teams'
            connectionId: connections_teams_name_resource.id
            connectionName: 'teams'
            connectionProperties: {}
          }
          'teams-3': {
            id: '/subscriptions/27db5ec6-d206-4028-b5e1-6004dca5eeef/providers/Microsoft.Web/locations/northcentralus/managedApis/teams'
            connectionId: connections_teams_name_resource.id
            connectionName: 'teams'
            connectionProperties: {}
          }
          'teams-4': {
            id: '/subscriptions/27db5ec6-d206-4028-b5e1-6004dca5eeef/providers/Microsoft.Web/locations/northcentralus/managedApis/teams'
            connectionId: connections_teams_name_resource.id
            connectionName: 'teams'
            connectionProperties: {}
          }
        }
      }
    }
  }
}

resource userAssignedIdentities_bioroute_id_8fa7_name_ccwhfhydm6y6o 'Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials@2025-05-31-preview' = {
  parent: userAssignedIdentities_bioroute_id_8fa7_name_resource
  name: 'ccwhfhydm6y6o'
  properties: {
    issuer: 'https://token.actions.githubusercontent.com'
    subject: 'repo:Risk-based-Routing-for-Disease-Control/Risk-based-Routing-for-Disease-Control:ref:refs/heads/WebUI'
    audiences: [
      'api://AzureADTokenExchange'
    ]
  }
}

resource storageAccounts_dt4team1blob_name_default 'Microsoft.Storage/storageAccounts/blobServices@2026-04-01' = {
  parent: storageAccounts_dt4team1blob_name_resource
  name: 'default'
  sku: {
    name: 'Standard_LRS'
    tier: 'Standard'
  }
  properties: {
    staticWebsite: {
      enabled: false
    }
    containerDeleteRetentionPolicy: {
      enabled: false
    }
    cors: {
      corsRules: []
    }
    deleteRetentionPolicy: {
      allowPermanentDelete: false
      enabled: false
    }
  }
}

resource Microsoft_Storage_storageAccounts_fileServices_storageAccounts_dt4team1blob_name_default 'Microsoft.Storage/storageAccounts/fileServices@2026-04-01' = {
  parent: storageAccounts_dt4team1blob_name_resource
  name: 'default'
  sku: {
    name: 'Standard_LRS'
    tier: 'Standard'
  }
  properties: {
    protocolSettings: {
      smb: {
        encryptionInTransit: {
          required: true
        }
      }
    }
    cors: {
      corsRules: []
    }
    shareDeleteRetentionPolicy: {
      enabled: true
      days: 7
    }
  }
}

resource Microsoft_Storage_storageAccounts_queueServices_storageAccounts_dt4team1blob_name_default 'Microsoft.Storage/storageAccounts/queueServices@2026-04-01' = {
  parent: storageAccounts_dt4team1blob_name_resource
  name: 'default'
  properties: {
    cors: {
      corsRules: []
    }
  }
}

resource Microsoft_Storage_storageAccounts_tableServices_storageAccounts_dt4team1blob_name_default 'Microsoft.Storage/storageAccounts/tableServices@2026-04-01' = {
  parent: storageAccounts_dt4team1blob_name_resource
  name: 'default'
  properties: {
    cors: {
      corsRules: []
    }
  }
}

resource sites_bioroute_name_resource 'Microsoft.Web/sites@2024-11-01' = {
  name: sites_bioroute_name
  location: 'Korea Central'
  kind: 'app,linux'
  properties: {
    enabled: true
    hostNameSslStates: [
      {
        name: '${sites_bioroute_name}-edagchfvcwfadfa3.koreacentral-01.azurewebsites.net'
        sslState: 'Disabled'
        hostType: 'Standard'
      }
      {
        name: '${sites_bioroute_name}-edagchfvcwfadfa3.scm.koreacentral-01.azurewebsites.net'
        sslState: 'Disabled'
        hostType: 'Repository'
      }
    ]
    serverFarmId: serverfarms_dt4_project2_team1_name_resource.id
    reserved: true
    isXenon: false
    hyperV: false
    dnsConfiguration: {}
    outboundVnetRouting: {
      allTraffic: false
      applicationTraffic: false
      contentShareTraffic: false
      imagePullTraffic: false
      backupRestoreTraffic: false
    }
    siteConfig: {
      numberOfWorkers: 1
      linuxFxVersion: 'PYTHON|3.11'
      acrUseManagedIdentityCreds: false
      alwaysOn: false
      http20Enabled: false
      functionAppScaleLimit: 0
      minimumElasticInstanceCount: 1
    }
    scmSiteAlsoStopped: false
    clientAffinityEnabled: false
    clientAffinityProxyEnabled: false
    clientCertEnabled: false
    clientCertMode: 'Required'
    hostNamesDisabled: false
    ipMode: 'IPv4'
    customDomainVerificationId: '520102906446FA8AD73B8CFA97C3FF8F5911B86B3D031F586F4B1F9C7A1868D5'
    containerSize: 0
    dailyMemoryTimeQuota: 0
    httpsOnly: true
    endToEndEncryptionEnabled: false
    redundancyMode: 'None'
    publicNetworkAccess: 'Enabled'
    storageAccountRequired: false
    keyVaultReferenceIdentity: 'SystemAssigned'
    autoGeneratedDomainNameLabelScope: 'TenantReuse'
  }
}

resource sites_bioroute_name_ftp 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2024-11-01' = {
  parent: sites_bioroute_name_resource
  name: 'ftp'
  location: 'Korea Central'
  properties: {
    allow: false
  }
}

resource sites_dt4_team1_func_collector_name_ftp 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2024-11-01' = {
  parent: sites_dt4_team1_func_collector_name_resource
  name: 'ftp'
  location: 'Korea Central'
  tags: {
    'hidden-link: /app-insights-resource-id': '/subscriptions/27db5ec6-d206-4028-b5e1-6004dca5eeef/resourceGroups/dt4_project2_team1/providers/microsoft.insights/components/dt4-team1-func-collector'
  }
  properties: {
    allow: false
  }
}

resource sites_bioroute_name_scm 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2024-11-01' = {
  parent: sites_bioroute_name_resource
  name: 'scm'
  location: 'Korea Central'
  properties: {
    allow: false
  }
}

resource sites_dt4_team1_func_collector_name_scm 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2024-11-01' = {
  parent: sites_dt4_team1_func_collector_name_resource
  name: 'scm'
  location: 'Korea Central'
  tags: {
    'hidden-link: /app-insights-resource-id': '/subscriptions/27db5ec6-d206-4028-b5e1-6004dca5eeef/resourceGroups/dt4_project2_team1/providers/microsoft.insights/components/dt4-team1-func-collector'
  }
  properties: {
    allow: false
  }
}

resource sites_bioroute_name_web 'Microsoft.Web/sites/config@2024-11-01' = {
  parent: sites_bioroute_name_resource
  name: 'web'
  location: 'Korea Central'
  properties: {
    numberOfWorkers: 1
    defaultDocuments: [
      'Default.htm'
      'Default.html'
      'Default.asp'
      'index.htm'
      'index.html'
      'iisstart.htm'
      'default.aspx'
      'index.php'
      'hostingstart.html'
    ]
    netFrameworkVersion: 'v4.0'
    linuxFxVersion: 'PYTHON|3.11'
    requestTracingEnabled: false
    remoteDebuggingEnabled: false
    httpLoggingEnabled: false
    acrUseManagedIdentityCreds: false
    logsDirectorySizeLimit: 35
    detailedErrorLoggingEnabled: false
    publishingUsername: 'REDACTED'
    scmType: 'GitHubAction'
    use32BitWorkerProcess: true
    webSocketsEnabled: false
    alwaysOn: false
    appCommandLine: 'bash startup.sh'
    managedPipelineMode: 'Integrated'
    virtualApplications: [
      {
        virtualPath: '/'
        physicalPath: 'site\\wwwroot'
        preloadEnabled: false
      }
    ]
    loadBalancing: 'LeastRequests'
    experiments: {
      rampUpRules: []
    }
    autoHealEnabled: false
    vnetRouteAllEnabled: false
    vnetPrivatePortsCount: 0
    publicNetworkAccess: 'Enabled'
    localMySqlEnabled: false
    ipSecurityRestrictions: [
      {
        ipAddress: 'Any'
        action: 'Allow'
        priority: 2147483647
        name: 'Allow all'
        description: 'Allow all access'
      }
    ]
    scmIpSecurityRestrictions: [
      {
        ipAddress: 'Any'
        action: 'Allow'
        priority: 2147483647
        name: 'Allow all'
        description: 'Allow all access'
      }
    ]
    scmIpSecurityRestrictionsUseMain: false
    http20Enabled: false
    minTlsVersion: '1.2'
    scmMinTlsVersion: '1.2'
    ftpsState: 'FtpsOnly'
    preWarmedInstanceCount: 0
    elasticWebAppScaleLimit: 0
    functionsRuntimeScaleMonitoringEnabled: false
    minimumElasticInstanceCount: 1
    azureStorageAccounts: {}
    http20ProxyFlag: 0
  }
}

resource sites_dt4_team1_func_collector_name_web 'Microsoft.Web/sites/config@2024-11-01' = {
  parent: sites_dt4_team1_func_collector_name_resource
  name: 'web'
  location: 'Korea Central'
  tags: {
    'hidden-link: /app-insights-resource-id': '/subscriptions/27db5ec6-d206-4028-b5e1-6004dca5eeef/resourceGroups/dt4_project2_team1/providers/microsoft.insights/components/dt4-team1-func-collector'
  }
  properties: {
    numberOfWorkers: 1
    defaultDocuments: [
      'Default.htm'
      'Default.html'
      'Default.asp'
      'index.htm'
      'index.html'
      'iisstart.htm'
      'default.aspx'
      'index.php'
    ]
    netFrameworkVersion: 'v4.0'
    requestTracingEnabled: false
    remoteDebuggingEnabled: false
    httpLoggingEnabled: false
    acrUseManagedIdentityCreds: false
    logsDirectorySizeLimit: 35
    detailedErrorLoggingEnabled: false
    publishingUsername: 'REDACTED'
    scmType: 'None'
    use32BitWorkerProcess: false
    webSocketsEnabled: false
    alwaysOn: false
    managedPipelineMode: 'Integrated'
    virtualApplications: [
      {
        virtualPath: '/'
        physicalPath: 'site\\wwwroot'
        preloadEnabled: false
      }
    ]
    loadBalancing: 'LeastRequests'
    experiments: {
      rampUpRules: []
    }
    autoHealEnabled: false
    vnetRouteAllEnabled: false
    vnetPrivatePortsCount: 0
    publicNetworkAccess: 'Enabled'
    cors: {
      allowedOrigins: [
        'https://portal.azure.com'
      ]
      supportCredentials: false
    }
    localMySqlEnabled: false
    ipSecurityRestrictions: [
      {
        ipAddress: 'Any'
        action: 'Allow'
        priority: 2147483647
        name: 'Allow all'
        description: 'Allow all access'
      }
    ]
    scmIpSecurityRestrictions: [
      {
        ipAddress: 'Any'
        action: 'Allow'
        priority: 2147483647
        name: 'Allow all'
        description: 'Allow all access'
      }
    ]
    scmIpSecurityRestrictionsUseMain: false
    http20Enabled: false
    minTlsVersion: '1.2'
    scmMinTlsVersion: '1.2'
    ftpsState: 'FtpsOnly'
    preWarmedInstanceCount: 0
    functionAppScaleLimit: 100
    functionsRuntimeScaleMonitoringEnabled: false
    minimumElasticInstanceCount: 0
    azureStorageAccounts: {}
    http20ProxyFlag: 0
  }
}

resource sites_bioroute_name_1397fab0_aef9_4dd1_8c34_3face9aca653 'Microsoft.Web/sites/deployments@2024-11-01' = {
  parent: sites_bioroute_name_resource
  name: '1397fab0-aef9-4dd1-8c34-3face9aca653'
  location: 'Korea Central'
  properties: {
    status: 4
    author_email: 'N/A'
    author: 'N/A'
    deployer: 'OneDeploy'
    message: 'OneDeploy'
    start_time: '2026-07-04T13:12:06.8238873Z'
    end_time: '2026-07-04T13:13:55.458297Z'
    active: false
  }
}

resource sites_bioroute_name_1f0fce47_6566_4ed1_ad16_a7a95da4c264 'Microsoft.Web/sites/deployments@2024-11-01' = {
  parent: sites_bioroute_name_resource
  name: '1f0fce47-6566-4ed1-ad16-a7a95da4c264'
  location: 'Korea Central'
  properties: {
    status: 4
    author_email: 'N/A'
    author: 'N/A'
    deployer: 'OneDeploy'
    message: 'OneDeploy'
    start_time: '2026-07-04T14:06:28.8347373Z'
    end_time: '2026-07-04T14:08:16.8516156Z'
    active: false
  }
}

resource sites_dt4_team1_func_collector_name_3b594378_a04f_4b8c_89c9_15e7ea809226 'Microsoft.Web/sites/deployments@2024-11-01' = {
  parent: sites_dt4_team1_func_collector_name_resource
  name: '3b594378-a04f-4b8c-89c9-15e7ea809226'
  location: 'Korea Central'
  properties: {
    status: 4
    deployer: 'ms-azuretools-vscode'
    start_time: '2026-07-02T05:35:32.3737134Z'
    end_time: '2026-07-02T05:36:40.4726706Z'
    active: false
  }
}

resource sites_bioroute_name_3cb8f786_e263_4e1a_8539_e5504f7b329d 'Microsoft.Web/sites/deployments@2024-11-01' = {
  parent: sites_bioroute_name_resource
  name: '3cb8f786-e263-4e1a-8539-e5504f7b329d'
  location: 'Korea Central'
  properties: {
    status: 4
    author_email: 'N/A'
    author: 'N/A'
    deployer: 'OneDeploy'
    message: 'OneDeploy'
    start_time: '2026-07-04T14:29:48.3956545Z'
    end_time: '2026-07-04T14:32:07.3877919Z'
    active: true
  }
}

resource sites_bioroute_name_51efa345_fc56_45bd_a7bf_afb09e9df62c 'Microsoft.Web/sites/deployments@2024-11-01' = {
  parent: sites_bioroute_name_resource
  name: '51efa345-fc56-45bd-a7bf-afb09e9df62c'
  location: 'Korea Central'
  properties: {
    status: 4
    author_email: 'N/A'
    author: 'N/A'
    deployer: 'OneDeploy'
    message: 'OneDeploy'
    start_time: '2026-07-04T07:45:51.6098521Z'
    end_time: '2026-07-04T07:47:41.3245189Z'
    active: false
  }
}

resource sites_bioroute_name_77ab2637_04ae_449f_8507_485ed6a42724 'Microsoft.Web/sites/deployments@2024-11-01' = {
  parent: sites_bioroute_name_resource
  name: '77ab2637-04ae-449f-8507-485ed6a42724'
  location: 'Korea Central'
  properties: {
    status: 4
    author_email: 'N/A'
    author: 'N/A'
    deployer: 'OneDeploy'
    message: 'OneDeploy'
    start_time: '2026-07-04T09:07:12.9446477Z'
    end_time: '2026-07-04T09:08:54.3672618Z'
    active: false
  }
}

resource sites_bioroute_name_95b1f627_6e38_42d0_bff7_3429c3cbf151 'Microsoft.Web/sites/deployments@2024-11-01' = {
  parent: sites_bioroute_name_resource
  name: '95b1f627-6e38-42d0-bff7-3429c3cbf151'
  location: 'Korea Central'
  properties: {
    status: 4
    author_email: 'N/A'
    author: 'N/A'
    deployer: 'OneDeploy'
    message: 'OneDeploy'
    start_time: '2026-07-04T14:25:44.9443093Z'
    end_time: '2026-07-04T14:27:33.8295361Z'
    active: false
  }
}

resource sites_bioroute_name_a722d5b1_d05d_42b9_9df2_de8981ee379e 'Microsoft.Web/sites/deployments@2024-11-01' = {
  parent: sites_bioroute_name_resource
  name: 'a722d5b1-d05d-42b9-9df2-de8981ee379e'
  location: 'Korea Central'
  properties: {
    status: 4
    author_email: 'N/A'
    author: 'N/A'
    deployer: 'OneDeploy'
    message: 'OneDeploy'
    start_time: '2026-07-03T09:30:56.1790633Z'
    end_time: '2026-07-03T09:34:02.4192182Z'
    active: false
  }
}

resource sites_bioroute_name_ba277ffc_636e_4651_9bb0_7bf5d90cc993 'Microsoft.Web/sites/deployments@2024-11-01' = {
  parent: sites_bioroute_name_resource
  name: 'ba277ffc-636e-4651-9bb0-7bf5d90cc993'
  location: 'Korea Central'
  properties: {
    status: 4
    author_email: 'N/A'
    author: 'N/A'
    deployer: 'OneDeploy'
    message: 'OneDeploy'
    start_time: '2026-07-03T09:20:26.2947442Z'
    end_time: '2026-07-03T09:22:06.130968Z'
    active: false
  }
}

resource sites_bioroute_name_bc063e4a_e82e_4417_b3db_acf43c8e34ba 'Microsoft.Web/sites/deployments@2024-11-01' = {
  parent: sites_bioroute_name_resource
  name: 'bc063e4a-e82e-4417-b3db-acf43c8e34ba'
  location: 'Korea Central'
  properties: {
    status: 4
    author_email: 'N/A'
    author: 'N/A'
    deployer: 'OneDeploy'
    message: 'OneDeploy'
    start_time: '2026-07-03T09:01:52.6583385Z'
    end_time: '2026-07-03T09:04:45.7657869Z'
    active: false
  }
}

resource sites_dt4_team1_func_collector_name_d7148b84_20d2_4164_a714_8081a12871f6 'Microsoft.Web/sites/deployments@2024-11-01' = {
  parent: sites_dt4_team1_func_collector_name_resource
  name: 'd7148b84-20d2-4164-a714-8081a12871f6'
  location: 'Korea Central'
  properties: {
    status: 4
    deployer: 'ms-azuretools-vscode'
    start_time: '2026-07-03T08:38:21.0270978Z'
    end_time: '2026-07-03T08:39:34.5569936Z'
    active: true
  }
}

resource sites_dt4_team1_func_collector_name_d871992d_42d1_4ee7_a0e7_7bdd4ef0b95a 'Microsoft.Web/sites/deployments@2024-11-01' = {
  parent: sites_dt4_team1_func_collector_name_resource
  name: 'd871992d-42d1-4ee7-a0e7-7bdd4ef0b95a'
  location: 'Korea Central'
  properties: {
    status: 4
    deployer: 'ms-azuretools-vscode'
    start_time: '2026-07-02T03:38:49.5896344Z'
    end_time: '2026-07-02T03:40:03.9929853Z'
    active: false
  }
}

resource sites_bioroute_name_eccfdfa5_20a1_4699_935d_2dd00d565d00 'Microsoft.Web/sites/deployments@2024-11-01' = {
  parent: sites_bioroute_name_resource
  name: 'eccfdfa5-20a1-4699-935d-2dd00d565d00'
  location: 'Korea Central'
  properties: {
    status: 4
    author_email: 'N/A'
    author: 'N/A'
    deployer: 'OneDeploy'
    message: 'OneDeploy'
    start_time: '2026-07-04T13:07:08.7924381Z'
    end_time: '2026-07-04T13:08:51.4298151Z'
    active: false
  }
}

resource sites_dt4_team1_func_collector_name_fn_compare_outbreaks 'Microsoft.Web/sites/functions@2024-11-01' = {
  parent: sites_dt4_team1_func_collector_name_resource
  name: 'fn_compare_outbreaks'
  location: 'Korea Central'
  properties: {
    script_href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/vfs/home/site/wwwroot/function_app.py'
    test_data_href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/vfs/tmp/FunctionsData/fn_compare_outbreaks.dat'
    href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/functions/fn_compare_outbreaks'
    config: {
      name: 'fn_compare_outbreaks'
      entryPoint: 'fn_compare_outbreaks'
      scriptFile: 'function_app.py'
      language: 'python'
      functionDirectory: '/home/site/wwwroot'
      bindings: [
        {
          direction: 'IN'
          type: 'httpTrigger'
          name: 'req'
          authLevel: 'FUNCTION'
          route: 'fn_compare_outbreaks'
        }
        {
          direction: 'OUT'
          type: 'http'
          name: '$return'
        }
      ]
    }
    invoke_url_template: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/api/fn_compare_outbreaks'
    language: 'python'
    isDisabled: false
  }
}

resource sites_dt4_team1_func_collector_name_fn_disinfection 'Microsoft.Web/sites/functions@2024-11-01' = {
  parent: sites_dt4_team1_func_collector_name_resource
  name: 'fn_disinfection'
  location: 'Korea Central'
  properties: {
    script_href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/vfs/home/site/wwwroot/function_app.py'
    test_data_href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/vfs/tmp/FunctionsData/fn_disinfection.dat'
    href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/functions/fn_disinfection'
    config: {
      name: 'fn_disinfection'
      entryPoint: 'fn_disinfection'
      scriptFile: 'function_app.py'
      language: 'python'
      functionDirectory: '/home/site/wwwroot'
      bindings: [
        {
          direction: 'IN'
          type: 'httpTrigger'
          name: 'req'
          authLevel: 'FUNCTION'
          route: 'fn_disinfection'
        }
        {
          direction: 'OUT'
          type: 'http'
          name: '$return'
        }
      ]
    }
    invoke_url_template: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/api/fn_disinfection'
    language: 'python'
    isDisabled: false
  }
}

resource sites_dt4_team1_func_collector_name_fn_kahis 'Microsoft.Web/sites/functions@2024-11-01' = {
  parent: sites_dt4_team1_func_collector_name_resource
  name: 'fn_kahis'
  location: 'Korea Central'
  properties: {
    script_href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/vfs/home/site/wwwroot/function_app.py'
    test_data_href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/vfs/tmp/FunctionsData/fn_kahis.dat'
    href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/functions/fn_kahis'
    config: {
      name: 'fn_kahis'
      entryPoint: 'fn_kahis'
      scriptFile: 'function_app.py'
      language: 'python'
      functionDirectory: '/home/site/wwwroot'
      bindings: [
        {
          direction: 'IN'
          type: 'httpTrigger'
          name: 'req'
          authLevel: 'FUNCTION'
          route: 'fn_kahis'
        }
        {
          direction: 'OUT'
          type: 'http'
          name: '$return'
        }
      ]
    }
    invoke_url_template: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/api/fn_kahis'
    language: 'python'
    isDisabled: false
  }
}

resource sites_dt4_team1_func_collector_name_fn_match_outbreaks 'Microsoft.Web/sites/functions@2024-11-01' = {
  parent: sites_dt4_team1_func_collector_name_resource
  name: 'fn_match_outbreaks'
  location: 'Korea Central'
  properties: {
    script_href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/vfs/home/site/wwwroot/function_app.py'
    test_data_href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/vfs/tmp/FunctionsData/fn_match_outbreaks.dat'
    href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/functions/fn_match_outbreaks'
    config: {
      name: 'fn_match_outbreaks'
      entryPoint: 'fn_match_outbreaks'
      scriptFile: 'function_app.py'
      language: 'python'
      functionDirectory: '/home/site/wwwroot'
      bindings: [
        {
          direction: 'IN'
          type: 'httpTrigger'
          name: 'req'
          authLevel: 'FUNCTION'
          route: 'fn_match_outbreaks'
        }
        {
          direction: 'OUT'
          type: 'http'
          name: '$return'
        }
      ]
    }
    invoke_url_template: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/api/fn_match_outbreaks'
    language: 'python'
    isDisabled: false
  }
}

resource sites_dt4_team1_func_collector_name_fn_migratory 'Microsoft.Web/sites/functions@2024-11-01' = {
  parent: sites_dt4_team1_func_collector_name_resource
  name: 'fn_migratory'
  location: 'Korea Central'
  properties: {
    script_href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/vfs/home/site/wwwroot/function_app.py'
    test_data_href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/vfs/tmp/FunctionsData/fn_migratory.dat'
    href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/functions/fn_migratory'
    config: {
      name: 'fn_migratory'
      entryPoint: 'fn_migratory'
      scriptFile: 'function_app.py'
      language: 'python'
      functionDirectory: '/home/site/wwwroot'
      bindings: [
        {
          direction: 'IN'
          type: 'httpTrigger'
          name: 'req'
          authLevel: 'FUNCTION'
          route: 'fn_migratory'
        }
        {
          direction: 'OUT'
          type: 'http'
          name: '$return'
        }
      ]
    }
    invoke_url_template: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/api/fn_migratory'
    language: 'python'
    isDisabled: false
  }
}

resource sites_dt4_team1_func_collector_name_fn_outbreak_logs 'Microsoft.Web/sites/functions@2024-11-01' = {
  parent: sites_dt4_team1_func_collector_name_resource
  name: 'fn_outbreak_logs'
  location: 'Korea Central'
  properties: {
    script_href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/vfs/home/site/wwwroot/function_app.py'
    test_data_href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/vfs/tmp/FunctionsData/fn_outbreak_logs.dat'
    href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/functions/fn_outbreak_logs'
    config: {
      name: 'fn_outbreak_logs'
      entryPoint: 'fn_outbreak_logs'
      scriptFile: 'function_app.py'
      language: 'python'
      functionDirectory: '/home/site/wwwroot'
      bindings: [
        {
          direction: 'IN'
          type: 'httpTrigger'
          name: 'req'
          authLevel: 'FUNCTION'
          route: 'fn_outbreak_logs'
        }
        {
          direction: 'OUT'
          type: 'http'
          name: '$return'
        }
      ]
    }
    invoke_url_template: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/api/fn_outbreak_logs'
    language: 'python'
    isDisabled: false
  }
}

resource sites_dt4_team1_func_collector_name_fn_outbreak_snapshot_listener 'Microsoft.Web/sites/functions@2024-11-01' = {
  parent: sites_dt4_team1_func_collector_name_resource
  name: 'fn_outbreak_snapshot_listener'
  location: 'Korea Central'
  properties: {
    script_href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/vfs/home/site/wwwroot/function_app.py'
    test_data_href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/vfs/tmp/FunctionsData/fn_outbreak_snapshot_listener.dat'
    href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/functions/fn_outbreak_snapshot_listener'
    config: {
      name: 'fn_outbreak_snapshot_listener'
      entryPoint: 'fn_outbreak_snapshot_listener'
      scriptFile: 'function_app.py'
      language: 'python'
      functionDirectory: '/home/site/wwwroot'
      bindings: [
        {
          direction: 'IN'
          type: 'blobTrigger'
          name: 'snapshot'
          path: 'raw/outbreak/snapshot/{name}'
          connection: 'BLOB_CONNECTION_STRING'
        }
      ]
    }
    language: 'python'
    isDisabled: false
  }
}

resource sites_dt4_team1_func_collector_name_fn_weather 'Microsoft.Web/sites/functions@2024-11-01' = {
  parent: sites_dt4_team1_func_collector_name_resource
  name: 'fn_weather'
  location: 'Korea Central'
  properties: {
    script_href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/vfs/home/site/wwwroot/function_app.py'
    test_data_href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/vfs/tmp/FunctionsData/fn_weather.dat'
    href: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/admin/functions/fn_weather'
    config: {
      name: 'fn_weather'
      entryPoint: 'fn_weather'
      scriptFile: 'function_app.py'
      language: 'python'
      functionDirectory: '/home/site/wwwroot'
      bindings: [
        {
          direction: 'IN'
          type: 'httpTrigger'
          name: 'req'
          authLevel: 'FUNCTION'
          route: 'fn_weather'
        }
        {
          direction: 'OUT'
          type: 'http'
          name: '$return'
        }
      ]
    }
    invoke_url_template: 'https://dt4-team1-func-collector-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net/api/fn_weather'
    language: 'python'
    isDisabled: false
  }
}

resource sites_bioroute_name_sites_bioroute_name_edagchfvcwfadfa3_koreacentral_01_azurewebsites_net 'Microsoft.Web/sites/hostNameBindings@2024-11-01' = {
  parent: sites_bioroute_name_resource
  name: '${sites_bioroute_name}-edagchfvcwfadfa3.koreacentral-01.azurewebsites.net'
  location: 'Korea Central'
  properties: {
    siteName: 'bioroute'
    hostNameType: 'Verified'
  }
}

resource sites_dt4_team1_func_collector_name_sites_dt4_team1_func_collector_name_d8ehhja4chfabzbq_koreacentral_01_azurewebsites_net 'Microsoft.Web/sites/hostNameBindings@2024-11-01' = {
  parent: sites_dt4_team1_func_collector_name_resource
  name: '${sites_dt4_team1_func_collector_name}-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net'
  location: 'Korea Central'
  properties: {
    siteName: 'dt4-team1-func-collector'
    hostNameType: 'Verified'
  }
}

resource scheduledqueryrules_collection_fail_name_resource 'microsoft.insights/scheduledqueryrules@2026-03-01' = {
  name: scheduledqueryrules_collection_fail_name
  location: 'koreacentral'
  kind: 'LogAlert'
  properties: {
    displayName: scheduledqueryrules_collection_fail_name
    severity: 3
    enabled: true
    evaluationFrequency: 'PT1M'
    scopes: [
      components_dt4_team1_func_collector_name_resource.id
    ]
    targetResourceTypes: [
      'microsoft.insights/components'
    ]
    windowSize: 'PT1M'
    criteria: {
      allOf: [
        {
          query: 'requests\n| where resultCode != 200\n| extend functionName = coalesce(\n    tostring(customDimensions["FunctionName"]),\n    tostring(customDimensions["functionName"]),\n    tostring(operation_Name)\n)\n| summarize failures=count() by functionName, resultCode, bin(timestamp, 1m)\n| order by timestamp desc\n'
          timeAggregation: 'Count'
          dimensions: [
            {
              name: 'functionName'
              operator: 'Include'
              values: [
                '*'
              ]
            }
            {
              name: 'resultCode'
              operator: 'Include'
              values: [
                '*'
              ]
            }
          ]
          operator: 'GreaterThan'
          threshold: json('0')
          failingPeriods: {
            numberOfEvaluationPeriods: 1
            minFailingPeriodsToAlert: 1
          }
        }
      ]
    }
    autoMitigate: false
    actions: {
      actionGroups: [
        actionGroups_collector_name_resource.id
      ]
      customProperties: {}
      actionProperties: {}
    }
  }
}

resource scheduledqueryrules_collection_failure_name_resource 'microsoft.insights/scheduledqueryrules@2026-03-01' = {
  name: scheduledqueryrules_collection_failure_name
  location: 'koreacentral'
  kind: 'LogAlert'
  properties: {
    displayName: scheduledqueryrules_collection_failure_name
    severity: 3
    enabled: true
    evaluationFrequency: 'PT5M'
    scopes: [
      components_dt4_team1_func_collector_name_resource.id
    ]
    targetResourceTypes: [
      'microsoft.insights/components'
    ]
    windowSize: 'PT5M'
    criteria: {
      allOf: [
        {
          query: 'requests\n| where resultCode == 200\n| extend functionName = coalesce(\n    tostring(customDimensions["FunctionName"]),\n    tostring(customDimensions["functionName"]),\n    tostring(operation_Name)\n)\n| summarize failures=count() by functionName, resultCode, bin(timestamp, 1m)\n| order by timestamp desc\n'
          timeAggregation: 'Count'
          dimensions: [
            {
              name: 'functionName'
              operator: 'Include'
              values: [
                '*'
              ]
            }
          ]
          operator: 'GreaterThan'
          threshold: json('0')
          failingPeriods: {
            numberOfEvaluationPeriods: 1
            minFailingPeriodsToAlert: 1
          }
        }
      ]
    }
    autoMitigate: false
    actions: {
      actionGroups: [
        actionGroups_collector_name_resource.id
      ]
      customProperties: {}
      actionProperties: {}
    }
  }
}

resource storageAccounts_dt4team1blob_name_default_app_package_dt4_team1_func_collector_926202b 'Microsoft.Storage/storageAccounts/blobServices/containers@2026-04-01' = {
  parent: storageAccounts_dt4team1blob_name_default
  name: 'app-package-dt4-team1-func-collector-926202b'
  properties: {
    immutableStorageWithVersioning: {
      enabled: false
    }
    defaultEncryptionScope: '$account-encryption-key'
    denyEncryptionScopeOverride: false
    publicAccess: 'None'
  }
  dependsOn: [
    storageAccounts_dt4team1blob_name_resource
  ]
}

resource storageAccounts_dt4team1blob_name_default_archive 'Microsoft.Storage/storageAccounts/blobServices/containers@2026-04-01' = {
  parent: storageAccounts_dt4team1blob_name_default
  name: 'archive'
  properties: {
    immutableStorageWithVersioning: {
      enabled: false
    }
    defaultEncryptionScope: '$account-encryption-key'
    denyEncryptionScopeOverride: false
    publicAccess: 'None'
  }
  dependsOn: [
    storageAccounts_dt4team1blob_name_resource
  ]
}

resource storageAccounts_dt4team1blob_name_default_azure_webjobs_hosts 'Microsoft.Storage/storageAccounts/blobServices/containers@2026-04-01' = {
  parent: storageAccounts_dt4team1blob_name_default
  name: 'azure-webjobs-hosts'
  properties: {
    immutableStorageWithVersioning: {
      enabled: false
    }
    defaultEncryptionScope: '$account-encryption-key'
    denyEncryptionScopeOverride: false
    publicAccess: 'None'
  }
  dependsOn: [
    storageAccounts_dt4team1blob_name_resource
  ]
}

resource storageAccounts_dt4team1blob_name_default_azure_webjobs_secrets 'Microsoft.Storage/storageAccounts/blobServices/containers@2026-04-01' = {
  parent: storageAccounts_dt4team1blob_name_default
  name: 'azure-webjobs-secrets'
  properties: {
    immutableStorageWithVersioning: {
      enabled: false
    }
    defaultEncryptionScope: '$account-encryption-key'
    denyEncryptionScopeOverride: false
    publicAccess: 'None'
  }
  dependsOn: [
    storageAccounts_dt4team1blob_name_resource
  ]
}

resource storageAccounts_dt4team1blob_name_default_model_artifacts 'Microsoft.Storage/storageAccounts/blobServices/containers@2026-04-01' = {
  parent: storageAccounts_dt4team1blob_name_default
  name: 'model-artifacts'
  properties: {
    immutableStorageWithVersioning: {
      enabled: false
    }
    defaultEncryptionScope: '$account-encryption-key'
    denyEncryptionScopeOverride: false
    publicAccess: 'None'
  }
  dependsOn: [
    storageAccounts_dt4team1blob_name_resource
  ]
}

resource storageAccounts_dt4team1blob_name_default_raw 'Microsoft.Storage/storageAccounts/blobServices/containers@2026-04-01' = {
  parent: storageAccounts_dt4team1blob_name_default
  name: 'raw'
  properties: {
    immutableStorageWithVersioning: {
      enabled: false
    }
    defaultEncryptionScope: '$account-encryption-key'
    denyEncryptionScopeOverride: false
    publicAccess: 'None'
  }
  dependsOn: [
    storageAccounts_dt4team1blob_name_resource
  ]
}

resource sites_dt4_team1_func_collector_name_resource 'Microsoft.Web/sites@2024-11-01' = {
  name: sites_dt4_team1_func_collector_name
  location: 'Korea Central'
  tags: {
    'hidden-link: /app-insights-resource-id': '/subscriptions/27db5ec6-d206-4028-b5e1-6004dca5eeef/resourceGroups/dt4_project2_team1/providers/microsoft.insights/components/dt4-team1-func-collector'
  }
  kind: 'functionapp,linux'
  properties: {
    enabled: true
    hostNameSslStates: [
      {
        name: '${sites_dt4_team1_func_collector_name}-d8ehhja4chfabzbq.koreacentral-01.azurewebsites.net'
        sslState: 'Disabled'
        hostType: 'Standard'
      }
      {
        name: '${sites_dt4_team1_func_collector_name}-d8ehhja4chfabzbq.scm.koreacentral-01.azurewebsites.net'
        sslState: 'Disabled'
        hostType: 'Repository'
      }
    ]
    serverFarmId: serverfarms_ASP_dt4project2team1_a9bb_name_resource.id
    reserved: true
    isXenon: false
    hyperV: false
    dnsConfiguration: {}
    outboundVnetRouting: {
      allTraffic: false
      applicationTraffic: false
      contentShareTraffic: false
      imagePullTraffic: false
      backupRestoreTraffic: false
    }
    siteConfig: {
      numberOfWorkers: 1
      acrUseManagedIdentityCreds: false
      alwaysOn: false
      http20Enabled: false
      functionAppScaleLimit: 100
      minimumElasticInstanceCount: 0
    }
    functionAppConfig: {
      deployment: {
        storage: {
          type: 'blobContainer'
          value: 'https://${storageAccounts_dt4team1blob_name}.blob.core.windows.net/app-package-${sites_dt4_team1_func_collector_name}-926202b'
          authentication: {
            type: 'StorageAccountConnectionString'
            storageAccountConnectionStringName: 'DEPLOYMENT_STORAGE_CONNECTION_STRING'
          }
        }
      }
      runtime: {
        name: 'python'
        version: '3.11'
      }
      scaleAndConcurrency: {
        maximumInstanceCount: 100
        instanceMemoryMB: 2048
      }
    }
    scmSiteAlsoStopped: false
    clientAffinityEnabled: false
    clientAffinityProxyEnabled: false
    clientCertEnabled: false
    clientCertMode: 'Required'
    hostNamesDisabled: false
    ipMode: 'IPv4'
    customDomainVerificationId: '520102906446FA8AD73B8CFA97C3FF8F5911B86B3D031F586F4B1F9C7A1868D5'
    containerSize: 1536
    dailyMemoryTimeQuota: 0
    httpsOnly: true
    endToEndEncryptionEnabled: false
    redundancyMode: 'None'
    publicNetworkAccess: 'Enabled'
    storageAccountRequired: false
    keyVaultReferenceIdentity: 'SystemAssigned'
    autoGeneratedDomainNameLabelScope: 'TenantReuse'
  }
  dependsOn: [
    storageAccounts_dt4team1blob_name_resource
  ]
}
