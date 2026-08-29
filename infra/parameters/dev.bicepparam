using '../main.bicep'

param acrName = 'acrcrookednumbersdev'
param logAnalyticsName = 'log-crooked-numbers-dev'
param containerAppsEnvironmentName = 'cae-crooked-numbers-dev'
param jobName = 'job-statcast-ingest-dev'
param jobIdentityName = 'id-statcast-ingest-dev'
param storageAccountName = 'crookednumbers'
param blobContainerName = 'baseball-data'
param imageName = 'crooked-numbers-statcast-ingestion:dev'
param cronExpression = '0 12 * * *'
param cpu = '0.5'
param memory = '1Gi'
param replicaTimeout = 1800
param replicaRetryLimit = 1
param statcastLookbackDays = 3
