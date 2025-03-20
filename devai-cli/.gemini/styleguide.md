# Company Kubernetes configuration best practices

1. Resource Management for Pods and Containers: Ensure the resource requests like memory and cpu are set for containers configuration.
Check that is not over or under provisioned for DEV and PROD environments.

### Company Specific Resource Requests Configuration for DEV env ###
resources:
    requests:
        cpu: 200m
        memory: 256Mi
        ephemeral-storage: 0.5Gi
    limits:
        cpu: 500m
        memory: 512Mi
        ephemeral-storage: 0.5Gi

### Company Specific Resource Requests Configuration for PROD env ###
resources:
    requests:
        cpu: 500m
        memory: 1Gi
        ephemeral-storage: 0.5Gi
    limits:
        cpu: 1000m
        memory: 2Gi
        ephemeral-storage: 1Gi