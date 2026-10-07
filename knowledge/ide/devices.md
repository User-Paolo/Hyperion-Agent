# Defining Device Node Applications

An **Application** is a Kubernetes [custom resource](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/) that describes a deployable workload:

- an **Android** APK
- a **Docker image**
- an **ESP32 firmware** binary

along with the device it should run on and the constraints that govern its deployment.

---

## Manifest Structure
Every Application manifest follows the standard Kubernetes resource layout:

```yaml
apiVersion: hyper.ai/v1
kind: Application
metadata:
  name: my-app
  annotations:
    intent: "Computer vision capture"
spec:
  # the application definition
status:
  # read-only, set by the platform
```

| Field | Type | Required | Description |
|---|---|---|---|
| `apiVersion` | string | ✅ | `hyper.ai/v1` |
| `kind` | string | ✅ | `Application` |
| `metadata` | object | ✅ | Application metadata — see `metadata` |
| `spec` | object | ✅ | Application Definition — see `spec` |
| `status` | object | ❌ | Set by the platform — see `status` |

---

## Field Reference
Below we provide all ***mandatory*** (✅) and ***optional*** (❌) fields that are registered in the Hyper-AI platform. The user can also provide additional fields and attributes, which will be forwarded and be accessible by their application.

### `metadata` — Application Metadata

| Field | Type | Required | Example |
|---|---|---|---|
| `name` | string | ✅ | `"vision-capture-android"` |
| `annotations` | map[string]string | ❌ | `intent: "Computer vision capture"` |

---

### `spec` — Application Definition
The attributes below are not required. Specifically it is possible to select a Device Node from the IDE UI, and this will fill the `device_name` attribute. Regarding the `device_uuid`, **you should not alter or set it**.

| Field | Type | Required | Example |
|---|---|---|---|
| `device_name` | string | ❌ | `"edge-device-01"` — if omitted, the scheduler selects the best available device |
| `device_uuid` | string | ❌ | `"40637429-b8ed-4817-b7fd-f32bc6834d9b"` — set automatically by the platform |

---

### `spec.app` — Application Identity

| Field | Type | Required | Example |
|---|---|---|---|
| `type` | string, enum: `device` | ✅ | `device` |
| `schemaVersion` | string | ✅ | `"1.0.0"` |
| `name` | string | ✅ | `"vision-capture"` |
| `version` | string | ✅ | `"2.3.0"` |
| `owner` | string | ✅ | `"Edge Vision Team"` |
| `lifecyclePhase` | string, enum: `development` `testing` `production` | ✅ | `"production"` |
| `description` | string | ❌ | `"Captures frames and emits detections."` |
| `parentApp.name` | string | ❌ | `"parent-app"` |
| `parentApp.uid` | string | ❌ | `"abc-123"` |

---

### `spec.workload` — Workload Definition

The `workload.kind` field determines which parameter block must be provided: exactly one of `androidApk`, `dockerImage`, or `esp32Binary`, matching the selected kind. Each block has its own set of fields, described below.

| Field | Type | Required | Example |
|---|---|---|---|
| `kind` | string, enum: `AndroidApk` `DockerImage` `esp32Binary` | ✅ | `"DockerImage"` |

#### AndroidApk

| Field | Type | Required | Example |
|---|---|---|---|
| `androidApk.apkUrl` | string (URI) | ✅ | `"https://example.com/app.apk"` |
| `androidApk.packageName` | string | ✅ | `"com.example.myapp"` |
| `androidApk.sha256` | string | ❌ | `"a3f5c..."` |
| `androidApk.installMode` | string, enum: `install` `update` | ❌ | `"update"` |
| `androidApk.launch.activity` | string | ❌ | `"com.example.myapp/.MainActivity"` |
| `androidApk.launch.action` | string | ❌ | `"android.intent.action.MAIN"` |
| `androidApk.launch.category` | string | ❌ | `"android.intent.category.LAUNCHER"` |

#### DockerImage

| Field | Type | Required | Example |
|---|---|---|---|
| `dockerImage.image` | string | ✅ | `"nginx:latest"` |
| `dockerImage.imagePullPolicy` | string, enum: `Always` `IfNotPresent` `Never` | ❌ | `"IfNotPresent"` |
| `dockerImage.imagePullSecretRef` | string | ❌ | `"registry-credentials"` |

#### esp32Binary

| Field | Type | Required | Example |
|---|---|---|---|
| `esp32Binary.binaryUrl` | string (URI) | ✅ | `"https://example.com/firmware.bin"` |
| `esp32Binary.chip` | string, enum: `esp32` `esp32s2` `esp32s3` `esp32c3` `esp32c6` `esp32h2` | ✅ | `"esp32s3"` |
| `esp32Binary.flash.method` | string, enum: `serial` `ota` | ✅ | `"ota"` |
| `esp32Binary.sha256` | string | ❌ | `"b2f4a..."` |
| `esp32Binary.flash.port` | string | ❌ | `"/dev/ttyUSB0"` |
| `esp32Binary.flash.baudRate` | integer (≥1200) | ❌ | `115200` |
| `esp32Binary.flash.offset` | string (hex) | ❌ | `"0x10000"` |
| `esp32Binary.flash.partition` | string | ❌ | `"app0"` |
| `esp32Binary.flash.eraseFlash` | boolean | ❌ | `true` |

---

### `spec.exec` — Execution Parameters
These attributes can be used to pass environmental variables inside the application deployed.

| Field | Type | Required | Example |
|---|---|---|---|
| `parameters` | map[string]string | ❌ | `STREAM_URL: "rtsp://10.0.0.5/live"` |
| `command` | array of strings | ❌ | `["/app/start", "--verbose"]` |
| `env` | map[string]string | ❌ | `LOG_LEVEL: "info"` |
| `workingDir` | string | ❌ | `"/app"` |

---

### `spec.resources` — Resource Requirements
These are additional attributes for required describing resources. They are important and taken into consideration, in case **the user does not opt for a specific Device Node during submission from the IDE**s (they are used for scheduling the application to the appropriate Device Node).

| Field | Type | Required | Example |
|---|---|---|---|
| `cpu.value` | number | ❌ | `250` |
| `cpu.unit` | string, enum: `cores` `millicores` | ❌ | `"millicores"` |
| `memory.value` | number | ❌ | `256` |
| `memory.unit` | string, enum: `MiB` `GiB` etc. | ❌ | `"MiB"` |
| `storage.value` | number | ❌ | `1` |
| `storage.unit` | string, enum: `GiB` etc. | ❌ | `"GiB"` |
| `gpu` | integer (≥0) | ❌ | `1` |
| `tpu` | integer (≥0) | ❌ | `0` |
| `accelerators` | array of strings | ❌ | `["cuda", "tensorrt"]` |

---

### `spec.network` — Network Requirements

| Field | Type | Required | Example |
|---|---|---|---|
| `ports[].port` | integer (1–65535) | ✅ | `8080` |
| `ports[].protocol` | string | ✅ | `"HTTP"` |
| `networkBandwidthMin.value` | number | ✅ | `10` |
| `networkBandwidthMin.unit` | string, enum: `bps` `Kbps` `Mbps` `Gbps` | ✅ | `"Mbps"` |

---

### `spec.qos` — Quality of Service

| Field | Type | Required | Example |
|---|---|---|---|
| `latencyToleranceMax.value` | number | ✅ | `150` |
| `latencyToleranceMax.unit` | string, enum: `ms` `s` | ✅ | `"ms"` |
| `energyCost.value` | number | ✅ | `5` |
| `energyCost.unit` | string, enum: `mW` `W` | ✅ | `"W"` |
| `monetaryCost.value` | number | ✅ | `0.05` |
| `monetaryCost.currency` | string | ✅ | `"USD"` |
| `monetaryCost.per` | string, enum: `second` `minute` `hour` `day` | ✅ | `"hour"` |
| `resilience` | string | ✅ | `"auto-restart"` |
| `availability.value` | number (0–1) | ✅ | `0.95` |
| `availability.unit` | string, enum: `fraction` | ✅ | `"fraction"` |
| `startupTime.value` | number | ✅ | `3` |
| `startupTime.unit` | string, enum: `ms` `s` | ✅ | `"s"` |

---

### `spec.constraints` — Scheduling Constraints

| Field | Type | Required | Example |
|---|---|---|---|
| `schedulingPriority` | integer | ✅ | `5` |
| `supportedArchitectures` | array of strings | ✅ | `["arm64-v8a", "amd64"]` |
| `geoLocationRequirement` | string | ✅ | `"LocalZone"` |
| `isHighlyAvailable` | boolean | ✅ | `false` |
| `faultTolerance` | string | ✅ | `"graceful-degradation"` |
| `dataClassification` | string | ✅ | `"private"` |
| `trustScore` | number (≥0) | ❌ | `90.0` |
| `batteryLevelMin` | integer (0–100) | ❌ | `20` |
| `securityLevel` | string | ❌ | `"high"` |

---

### `spec.sensors` — Sensor Requirements

| Field | Type | Required | Example |
|---|---|---|---|
| `sensorType` | string | ✅ | `"temperature"` |
| `isActive` | boolean | ✅ | `true` |
| `taskStatus` | string, enum: `IDLE` `RUNNING` `SCHEDULED` | ✅ | `"IDLE"` |
| `sensorIDs` | array of strings | ❌ | `["sensor-001"]` |
| `platformInfo` | string | ❌ | `"i2c-bus-1"` |

---

### `spec.runtime` — Runtime Requirements

| Field | Type | Required | Example |
|---|---|---|---|
| `baseOS.name` | string | ❌ | `"Ubuntu"` |
| `baseOS.version` | string | ❌ | `"22.04"` |
| `acceleratorRuntime[].name` | string | ❌ | `"cuda"` |
| `hypervisor` | string | ❌ | `"kvm"` |

---

### `spec` — Miscellaneous

| Field | Type | Required | Example |
|---|---|---|---|
| `logs_url` | string (URI) | ❌ | `"https://logs.example.com/my-app"` |
| `metrics_url` | string (URI) | ❌ | `"https://metrics.example.com/my-app"` |
| `config` | free-form object | ❌ | see Custom Configuration Fields |

---

### `status` — Deployment Status (Read-only)

Unlike the `spec` fields above, `status` is not set by the user. The platform updates `status.phase` automatically as the application progresses through its lifecycle:

| Phase | Meaning |
|---|---|
| `pending` | Deployment requested, waiting for device ACK |
| `scheduled` | Device selected, workload being sent |
| `deployed` | Device acknowledged successful deployment |
| `failed` | Deployment failed or timed out |
| `removed` | Application was deleted and device acknowledged removal |

---

## Custom Configuration Fields

> **Note:** The `spec.config` field accepts any key-value structure, allowing you to pass arbitrary configuration to your application without modifying the schema. This is useful for application-specific settings that don't fit into the standard fields.

Examples:

```yaml
spec:
  config:
    mqtt_broker: "mqtt://edge-broker:1883"
    sampling_rate: "100ms"
    model_path: "/models/person-v3.onnx"
    debug: "true"
```

```yaml
spec:
  config:
    camera_index: "0"
    resolution: "1920x1080"
    output_topic: "detections/camera-0"
```

---

## Examples

See Cookbook & Examples for minimal device app examples.
