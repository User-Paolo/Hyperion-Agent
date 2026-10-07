# Cookbook & Examples

Recipes and examples for building complex workflows including native and device applications.

## Native Applications

The examples below are native Applications — workloads defined through an application profile. All available attributes are explained in the Native Apps reference.

### Hello World Web Server — nginx

A workflow that deploys an nginx server. The user expresses their preferences through specific constraints and QoS requirements.

```yaml
applicationProfile:
  metadata:
    type: "native"
    schemaVersion: "1.1.0"
    name: "hello-world-webserver"
    version: "1.0.0"
    description: "Nginx web server for HyperAI platform assessment."
    owner: "UoA-Team"
    lifecyclePhase: "development"
    annotations:
      intent: "platform-demo"
      domain: "education"
      language: "Python 3.10"
      dependencies: ["fastapi", "uvicorn"]

  specs:
    runtime:
      executionType: "container"
      entryPoint: "uvicorn"
      args: ["main:app", "--host", "0.0.0.0", "--port", "8000"]
      baseOS:
        name: "python"
        version: "3.10-slim"
      containerImage:
        uri: "nginx"
        tag: "latest"

    resources:
      cpu: "2000m"
      memory: "10Gi"
      storage: "1Gi"

    network:
      ports:
        - port: 8000
          protocol: "TCP"
          publicExposure: true
      protocols: ["HTTP"]

    constraints:
      supportedArchitectures: ["x86_64", "arm64"]
      securityLevel: "high"
      dataClassification: "private"
      isHighlyAvailable: false

    qos:
      startupTime: "10s"
      availability: "99.0%"
```

## Device Applications

The examples below are device Applications — workloads deployed to Device Nodes across the edge. All available attributes are explained in the Device Apps reference.

### Hello World — Docker

A minimal Docker application built on the [hello-world](https://hub.docker.com/_/hello-world) image. `device_name` is intentionally omitted — the platform scheduler automatically selects the best available device with Docker support.

```yaml
apiVersion: hyper.ai/v1
kind: Application
metadata:
  name: hello-world
  annotations:
    intent: "Hello World test"
    domain: "edge-testing"
spec:
  app:
    type: device
    schemaVersion: "1.0.0"
    name: "hello-world"
    version: "1.0.0"
    description: "Hello World Docker image for basic connectivity testing."
    owner: "HyperAI Team"
    lifecyclePhase: "testing"
  workload:
    kind: DockerImage
    dockerImage:
      image: "hello-world"
      imagePullPolicy: "IfNotPresent"
  exec:
    parameters:
      MODE: "test"
  network:
    ports:
      - port: 80
        protocol: "HTTP"
    networkBandwidthMin: { value: 1, unit: "Mbps" }
  qos:
    latencyToleranceMax: { value: 500, unit: "ms" }
    energyCost: { value: 1, unit: "W" }
    monetaryCost: { value: 0.01, currency: "USD", per: "hour" }
    resilience: "auto-restart"
    availability: { value: 0.90, unit: "fraction" }
    startupTime: { value: 5, unit: "s" }
  constraints:
    schedulingPriority: 1
    supportedArchitectures: ["amd64", "arm64"]
    geoLocationRequirement: "LocalZone"
    isHighlyAvailable: false
    faultTolerance: "graceful-degradation"
    dataClassification: "internal"
```

### Hello World — Android APK

An Android APK application that install a simple Hello World apk. Demonstrates Android workload configuration including APK URL, package name, launch intent, and execution parameters. Targets a specific device by name.

```yaml
apiVersion: hyper.ai/v1
kind: Application
metadata:
  name: hello-world-android
  annotations:
    intent: "Hello World Android test"
    domain: "edge-testing"
spec:
  device_name: device-sdk-gphone64-arm64-3a646c203ef4e9df
  app:
    type: device
    schemaVersion: "1.0.0"
    name: "hello-world-android"
    version: "1.0.0"
    description: "Test APK deployment to Android device via HyperAI Open Connectors."
    owner: "HyperAI Team"
    lifecyclePhase: "testing"
  workload:
    kind: AndroidApk
    androidApk:
      apkUrl: "https://gitlab.eclipse.org/eclipse-research-labs/hyper-ai-project/open-connectors/-/raw/master/android/test-target-debug.apk"
      packageName: "com.example.testtarget"
      installMode: "install"
  network:
    ports:
      - port: 80
        protocol: "HTTP"
    networkBandwidthMin: { value: 1, unit: "Mbps" }
  qos:
    latencyToleranceMax: { value: 500, unit: "ms" }
    energyCost: { value: 1, unit: "W" }
    monetaryCost: { value: 0.01, currency: "USD", per: "hour" }
    resilience: "auto-restart"
    availability: { value: 0.90, unit: "fraction" }
    startupTime: { value: 5, unit: "s" }
  constraints:
    schedulingPriority: 1
    supportedArchitectures: ["arm64-v8a"]
    geoLocationRequirement: "LocalZone"
    isHighlyAvailable: false
    faultTolerance: "graceful-degradation"
    dataClassification: "internal"
```

> **Note:** Replace `<your-device-name>` with the name of a registered Android DeviceNode.
