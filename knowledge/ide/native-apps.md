# Defining Native Applications

A **Native Application** is described by an application profile — a YAML document with `applicationProfile` at its root — that defines the workload (container, VM, or binary), its runtime environment, and the requirements that govern where and how it runs.

---

## Profile Structure
Every application profile follows this layout:

```yaml
applicationProfile:
  metadata:
    # application identity and annotations
  specs:
    # runtime, resources, network, constraints, qos
  status:
    # runtime state, updated dynamically
```

| Field | Type | Required | Description |
|---|---|---|---|
| `applicationProfile.metadata` | object | ✅ | Application metadata — see `metadata` |
| `applicationProfile.specs` | object | ✅ | Application requirements — see the `specs` sections below |
| `applicationProfile.status` | object | ❌ | Runtime state, updated dynamically — see `status` |

---

## Field Reference
Below we provide all ***mandatory*** (✅) and ***optional*** (❌) fields that are registered in the Hyper-AI platform.

### `metadata` — Application Metadata

| Field | Type | Required | Example | Description |
|---|---|---|---|---|
| `type` | string, `native` | ✅ | `"native"` | Application profile type: integration, native, or device. |
| `schemaVersion` | string | ✅ | `"1.1.0"` latest | App profile schema version using semantic versioning (e.g., 1.0.0). |
| `name` | string | ✅ | `"hello-world-webserver"` | Globally unique application name for identification. |
| `version` | string | ✅ | `"1.0.0"` | Internal version identifier for the application instance. |
| `description` | string | ❌ | `"Nginx web server for HyperAI platform assessment."` | A short description of what the application does. |
| `owner` | string | ✅ | `"UoA-Team"` | Person or organization responsible for this application. |
| `lifecyclePhase` | string, enum: `development` `testing` `production` | ✅ | `"development"` | Lifecycle stage: development, testing, or production. |
| `createdAt` | string (RFC 3339) | ❌ | `"2026-06-04T12:00:00Z"` | Creation timestamp in RFC 3339 format (UTC). |
| `updatedAt` | string (RFC 3339) | ❌ | `"2026-06-04T12:30:00Z"` | Last modification timestamp in RFC 3339 format (UTC). |
| `annotations.intent` | string | ❌ | `"platform-demo"` | Purpose of the application |
| `annotations.domain` | string | ❌ | `"education"` | Classification of application (e.g., AI, Automotive, robotics) |
| `annotations.language` | string | ❌ | `"Python 3.10"` | Programming language used by the application |
| `annotations.dependencies` | list | ❌ | `["fastapi", "uvicorn"]` | Required software libraries (e.g., ML frameworks) |

---

### `specs.runtime` — Runtime Requirements

| Field | Type | Required | Example | Description |
|---|---|---|---|---|
| `executionType` | string, enum: `container` `vm` | ✅ | `"container"` | Type of execution platform (e.g., container, vm, native, android) |
| `entryPoint` | string | ✅ | `"uvicorn"` | Path to the main script or command executed at container startup |
| `args` | list | ✅ | `["main:app", "--port", "8000"]` | Arguments passed to the entry point command |
| `baseOS.name` | string | ✅ | `"python"` | Name of base OS (e.g., ubuntu) |
| `baseOS.version` | string | ✅ | `"3.10-slim"` | Version of the base OS (e.g., 20.04) |
| `containerImage.uri` | string | ✅ | `"registry.example.com/org/app"` | OCI-compliant container image URI |
| `containerImage.tag` | string | ✅ | `"latest"` | Optional image tag (containers) |
| `hypervisor` | string, enum: `qemu` `kvm` `xen` `vmware` | ❌ | `"kvm"` | Hypervisor/manager (qemu, kvm, xen, vmware) |
| `acceleratorRuntime[].name` | string | ❌ | `"cuda"` | Name of the runtime environment for accelerators |
| `acceleratorRuntime[].version` | string | ❌ | `"12.2"` | Version of the accelerator runtime |

---

### `specs.resources` — Resource Requirements

| Field | Type | Required | Example | Description |
|---|---|---|---|---|
| `cpu` | string (>0, millicores) | ✅ | `"2000m"` | Number of CPU cores required (e.g., '1000m' for 1 core). |
| `memory` | string (`Mi` `Gi` `Ti`) | ✅ | `"10Gi"` | Memory requirement. |
| `storage` | string (`Mi` `Gi` `Ti`) | ✅ | `"1Gi"` | Storage requirement (if needed). |
| `gpu` | integer (≥0) | ❌ | `1` | Required GPUs. |
| `tpu` | integer (≥0) | ❌ | `0` | Required TPUs. |
| `accelerators` | integer (≥0) | ❌ | `0` | List of FPGAs, ASICs |

---

### `specs.network` — Network Requirements

| Field | Type | Required | Example | Description |
|---|---|---|---|---|
| `ports[].port` | integer | ✅ | `8000` | port number |
| `ports[].protocol` | string | ✅ | `"TCP"` | protocol used by this port |
| `ports[].publicExposure` | boolean | ❌ | `true` | Whether the port is publicly exposed |
| `protocols` | list | ❌ | `["HTTP"]` | Application-level protocols used by the application (e.g., HTTP, gRPC) |
| `networkBandwidthMin` | string (`Mbps` `Gbps`) | ❌ | `"100Mbps"` | Minimum network bandwidth. |

---

### `specs.constraints` — Scheduling Constraints

| Field | Type | Required | Example | Description |
|---|---|---|---|---|
| `supportedArchitectures` | list | ✅ | `["x86_64"]` | Compatible CPU/GPU architectures. |
| `trustScore` | string (1–5) | ❌ | `"4.5"` | Reliability and security score. |
| `geoLocationRequirement` | string | ❌ | `"Europe-only"` | Location restrictions. |
| `isHighlyAvailable` | boolean | ❌ | `false` | Specifies if deployment requires redundancy. |
| `faultTolerance` | string | ❌ | `"restart"` | Resiliency strategy (e.g., restart policy). |
| `securityLevel` | string (1–3) | ❌ | `"high"` | Security classification (e.g., 3: high, 2: medium, 1: low). |
| `dataClassification` | string | ❌ | `"private"` | Data sensitivity |

---

### `specs.qos` — Quality of Service

| Field | Type | Required | Example | Description |
|---|---|---|---|---|
| `latencyToleranceMax` | string (ms) | ❌ | `"150ms"` | Maximum tolerable latency. |
| `energyCost` | string (kWh) | ❌ | `"0.5kWh"` | Estimated energy consumption per hour. |
| `monetaryCost` | string (currency) | ❌ | `"0.05"` | Deployment cost per hour. |
| `resilience` | string | ❌ | `"restart"` | Tolerance and failure mechanism (e.g., restart) |
| `availability` | string (%) | ❌ | `"99.0%"` | Uptime SLA target |
| `startupTime` | string (secs) | ❌ | `"10s"` | Time to become operational |

> **Note:** `resilience`: Redundant to faultTolerance, will be removed in the next schema version.

---

### `status` — Runtime Status (Dynamic)

Unlike the fields above, `status` is not set in the profile — it reflects the runtime state of the application and is updated dynamically.

| Field | Type | Required | Example | Description |
|---|---|---|---|---|
| `isOnline` | boolean | ✅ | `true` | Whether the application is currently active |
| `lastHeartBeat` | string (RFC 3339) | ✅ | `"2026-06-04T12:30:00Z"` | Last time the app sent a status signal |
| `runtimeState` | string | ✅ | `"running"` | Current runtime status of app (e.g., running, failed) |
| `isStateless` | boolean | ❌ | `false` | Indicates if the application maintains state. |
| `resourceUsage.cpu` | string | ✅ | `"2000m"` | CPU usage (e.g., 2000m) |
| `resourceUsage.memory` | string | ✅ | `"512Mi"` | RAM usage |
| `resourceUsage.storage` | string | ✅ | `"1Gi"` | Storage consumed |
| `resourceUsage.gpu` | integer (≥0) | ❌ | `0` | Number of GPUs consumed |
| `resourceUsage.tpu` | integer (≥0) | ❌ | `0` | Number of TPUs consumed |
| `resourceUsage.accelerators` | integer (≥0) | ❌ | `0` | Number of FPGAs, ASICs used |

---

## Examples

See Cookbook & Examples for minimal native app examples.
