# Example Predictions — Model C (model_c_combined)

Test set: 896 samples

For each actual-duration bucket, this report shows:
- **3 best predictions** (smallest relative error)
- **3 worst predictions** (largest relative error)

---

## Actual bucket: **< 1 day** (86 samples)

*Median absolute error: 3.2d, median relative error: 2417%*

### Best 3 predictions (most accurate)

**kubernetes/kubernetes #136091** — Standard numeric format validation (int32, int64, float, double) is not enforced in CRDs

- Actual: **5.7h** (5.7h, bucket: < 1 day)
- Predicted: **9.2h** (9.2h, bucket: 1 day)
- Error: 3.5h (61% off)
- Files changed: 66

> ### What happened?
CRDs that use standard numeric formats for both integer and number types do not actually enforce these constraints during validation. 
This is a follow up issue of https://github.com/kubernetes/kubernetes/issues/133880
### What did you expect to happen?
Reject invalid integer/number following the defined formats.
### How can we reproduce it (as minimally and precisely as possibl...

**facebook/react #7430** — `HTMLDOMPropertyConfig` contains non-standard `icon` property

- Actual: **7.9h** (7.9h, bucket: < 1 day)
- Predicted: **1.6d** (38.9h, bucket: 1-3 days)
- Error: 1.3d (395% off)
- Files changed: 1

> **Do you want to request a _feature_ or report a _bug_?**
Report a bug.
**What is the current behavior?**
The `HTMLDOMPropertyConfig` object [includes an `icon` property](https://github.com/facebook/react/blob/cccef3c68310df3bd611df2a7b98a530645c67c0/src/renderers/dom/shared/HTMLDOMPropertyConfig.js#L85) in a section title `Standard Properties`, but `icon` isn’t an attribute supported by any stand...

**microsoft/vscode #302132** — Sessions: telemetry should distinguish between the apps

- Actual: **4.8h** (4.8h, bucket: < 1 day)
- Predicted: **1.0d** (24.5h, bucket: 1-3 days)
- Error: 19.7h (408% off)
- Files changed: 6

> Maybe a property on the base telemetry props would be good.

### Worst 3 predictions (least accurate)

**microsoft/vscode #283174** — "Search with AI" option shows even if you have "Disable AI Features" enabled

- Actual: **1.2h** (1.2h, bucket: < 1 day)
- Predicted: **8.1d** (193.7h, bucket: 1-4 weeks)
- Error: 8.0d (15730% off)
- Files changed: 1

> <!-- ⚠️⚠️ Do Not Delete This! bug_report_template ⚠️⚠️ -->
<!-- Please read our Rules of Conduct: https://opensource.microsoft.com/codeofconduct/ -->
<!-- 🕮 Read our guide about submitting issues: https://github.com/microsoft/vscode/wiki/Submitting-Bugs-and-Suggestions -->
<!-- 🔎 Search existing issues to avoid creating duplicates. -->
<!-- 🧪 Test using the latest Insiders build to see if your iss...

**microsoft/vscode #254880** — Undoing with a `Try again` action in the history doesn't make it dissapear

- Actual: **1.5h** (1.5h, bucket: < 1 day)
- Predicted: **8.7d** (208.3h, bucket: 1-4 weeks)
- Error: 8.6d (14172% off)
- Files changed: 1

> At some point the agent failed to edit further
<img width="404" height="623" alt="Image" src="https://github.com/user-attachments/assets/0da3b2ad-2f26-48ee-aee2-0ba2ae979464" />
If I clicked Undo a few times, that error message staying in the chat:
<img width="553" height="498" alt="Image" src="https://github.com/user-attachments/assets/cb8fc15c-982c-44bb-935c-f102d8893c85" />

**microsoft/vscode #282527** — Agent sessions: make sidebar toggle visible even in chats

- Actual: **2.2h** (2.2h, bucket: < 1 day)
- Predicted: **10.9d** (262.7h, bucket: 1-4 weeks)
- Error: 10.9d (11770% off)
- Files changed: 5

> When you are in a chat, we show a title:
<img width="571" height="440" alt="Image" src="https://github.com/user-attachments/assets/f415fbd4-f9f6-4264-a197-cce8bea5205f" />
In here the top right should show the sidebar toggle.
//cc @rebornix

---

## Actual bucket: **1 day** (90 samples)

*Median absolute error: 3.2d, median relative error: 524%*

### Best 3 predictions (most accurate)

**kubernetes/kubernetes #2681** — Kubelet stats don't work with latest version of cadvisor (0.6.2)

- Actual: **23.9h** (23.9h, bucket: 1 day)
- Predicted: **1.1d** (27.3h, bucket: 1-3 days)
- Error: 3.4h (14% off)
- Files changed: 10

> Detailed at https://github.com/openshift/origin/issues/458.
With cadvisor 0.6.2 request to kubelet at `/stats/<POD_ID>/<CONTAINER_ID>` doesn't work as it proxies call to cadvisor `/containers/docker/<DOCKER_ID>` The `/containers` prefix no longer works.
Solution is to upgrade `github.com/google/cadvisor/client` & `github.com/google/cadvisor/info` dependencies & update `cadvisorInterface`with `Dock...

**kubernetes/kubernetes #135001** — failing kubelet skew jobs with kubeadm (kinder)

- Actual: **21.5h** (21.5h, bucket: 1 day)
- Predicted: **1.3d** (30.1h, bucket: 1-3 days)
- Error: 8.7h (40% off)
- Files changed: 2

> ### Which jobs are failing?
https://testgrid.k8s.io/sig-cluster-lifecycle-kubeadm#kubeadm-kinder-kubelet-1-33-on-latest
https://testgrid.k8s.io/sig-cluster-lifecycle-kubeadm#kubeadm-kinder-kubelet-1-32-on-latest

### Which tests are failing?
Kubernetes e2e suite.[It] [sig-node] Pods Extended (pod generation) Pod Generation issue 500 podspec updates and verify generation and observedGeneration even...

**microsoft/vscode #248550** — `sourceFileMap` does not work with `${config:` settings on v1.100

- Actual: **19.0h** (19.0h, bucket: 1 day)
- Predicted: **1.2d** (28.6h, bucket: 1-3 days)
- Error: 9.5h (50% off)
- Files changed: 2

> <!-- ⚠️⚠️ Do Not Delete This! bug_report_template ⚠️⚠️ -->
<!-- Please read our Rules of Conduct: https://opensource.microsoft.com/codeofconduct/ -->
<!-- 🕮 Read our guide about submitting issues: https://github.com/microsoft/vscode/wiki/Submitting-Bugs-and-Suggestions -->
<!-- 🔎 Search existing issues to avoid creating duplicates. -->
<!-- 🧪 Test using the latest Insiders build to see if your iss...

### Worst 3 predictions (least accurate)

**facebook/react #28968** — Update react GitHub page CNAME record

- Actual: **8.9h** (8.9h, bucket: 1 day)
- Predicted: **12.9d** (309.9h, bucket: 1-4 weeks)
- Error: 12.5d (3372% off)
- Files changed: 1

> React GitHub page (https://facebook.github.io/react) (`gh-pages` branch) currently pointing to [reactjs.org](https://reactjs.org) and then it redirects to https://react.dev/.
So many redirects, can we update the content of `CNAME` file with `react.dev`, if it ok to do, then I am very happy to do the same and I'll contribution in real open source project.

**kubernetes/kubernetes #3640** — Round robin load balancer can overwhelm first pod behind service

- Actual: **10.4h** (10.4h, bucket: 1 day)
- Predicted: **2.1w** (351.4h, bucket: 1-4 weeks)
- Error: 2.0w (3277% off)
- Files changed: 4

> This is particularly easy to do with a new cluster.
Create a service `S` and deploy `N` pods behind it. Start up `M` pods which create a persistent connection to service `S`.
Because the round robin load balancer always starts at the 0th endpoint, and the endpoint list is consistent cluster-wide, you will see that you now have `M` connections to Pod 1, and 0 connections to all other pods 2 through...

**kubernetes/kubernetes #134961** — ResourceClaim strategy test miss the unexpected error check

- Actual: **10.9h** (10.9h, bucket: 1 day)
- Predicted: **12.5d** (300.1h, bucket: 1-4 weeks)
- Error: 12.1d (2664% off)
- Files changed: 2

> ### What happened?
According to the comment https://github.com/kubernetes/kubernetes/pull/134615#discussion_r2475964555 by @mortent, the assertion in `pkg/registry/resource/resourceclaimtemplate/strategy_test.go` doesn't catch situations where Validate unexpectedly returns errors.
Since tc.expectValidationError is an empty string in this situation, it will pass. It should check that if tc.expectVa...

---

## Actual bucket: **1-3 days** (157 samples)

*Median absolute error: 3.0d, median relative error: 156%*

### Best 3 predictions (most accurate)

**kubernetes/kubernetes #137617** — DRA scheduler plugin cannot fulfill gang scheduling with shared ResourceClaims

- Actual: **2.0d** (49.0h, bucket: 1-3 days)
- Predicted: **2.0d** (49.0h, bucket: 1-3 days)
- Error: 2 min (0% off)
- Files changed: 12

> ### What happened?
When two Pods are created in a gang where both Pods share the same ResourceClaim, the scheduler falls into an endless loop trying to schedule the Pods and never succeeds.
```
Events:
  Type     Reason            Age                          From               Message
  ----     ------            ----                         ----               -------
  Warning  FailedScheduling...

**microsoft/vscode #285255** — Remove or move `src/vs/loader.js`

- Actual: **2.2d** (52.8h, bucket: 1-3 days)
- Predicted: **2.1d** (50.6h, bucket: 1-3 days)
- Error: 2.2h (4% off)
- Files changed: 5

> Given https://github.com/microsoft/vscode-dev/issues/1245#issuecomment-3675865128, I am moving ahead to remove the ESM-AMD bridge support for web in https://github.com/microsoft/vscode/pull/285230. This means web no longer has a dependency on `src/vs/loader.js` and thus can be removed or moved.
However, it looks like there are still certain uses (searching for `loader.js` in `vscode`):
- the edito...

**kubernetes/kubernetes #3852** — Automatically restart etcd

- Actual: **2.2d** (52.6h, bucket: 1-3 days)
- Predicted: **2.0d** (47.5h, bucket: 1-3 days)
- Error: 5.1h (10% off)
- Files changed: 2

> We don't currently automatically restart etcd.  We should.

### Worst 3 predictions (least accurate)

**facebook/react #6879** — React.createElement(type, { key: undefined }) is handled incorrectly

- Actual: **1.0d** (24.6h, bucket: 1-3 days)
- Predicted: **13.5d** (325.1h, bucket: 1-4 weeks)
- Error: 12.5d (1219% off)
- Files changed: 3

> I believe #5744 introduced a behavioral difference between development and production versions of React. We released it as a part of 15.0, and this difference still exists.
The production behavior hasn’t changed. However the development behavior diverged after this change.
``` js
var el = React.createElement('div', { key: undefined })
document.body.innerHTML = (typeof el.key) + ' ' + el.key
```
Wh...

**kubernetes/kubernetes #126468** — kube-proxy: initialization check race leads to stale UDP conntrack

- Actual: **1.0d** (24.9h, bucket: 1-3 days)
- Predicted: **11.3d** (272.2h, bucket: 1-4 weeks)
- Error: 10.3d (995% off)
- Files changed: 1

> ### What happened?
AKS had a customer report repeated issues in their clusters where:
1. kube-proxy would redeploy (e.g. due to AKS deploying a new kube-proxy image with CVE fixes)
2. Envoy c-ares DNS client would send repeated DNS queries to the kube-dns service VIP from the same src IP address, creating a UDP conntrack entry to the svc VIP and keeping it alive. For example, with kube-dns svc VIP...

**kubernetes/kubernetes #73264** — --cpu-cfs-quota-period should not have effect if feature gate CPUCFSQuotaPeriod is not enabled

- Actual: **1.2d** (29.7h, bucket: 1-3 days)
- Predicted: **11.8d** (282.0h, bucket: 1-4 weeks)
- Error: 10.5d (850% off)
- Files changed: 2

> <!-- Please use this template while reporting a bug and provide as much info as possible. Not doing so may result in your bug not being addressed in a timely manner. Thanks!-->

**What happened**:
When run kubelet with "--cpu-cfs-quota-period 1000ms"  and without --feature-gates=CustomCPUCFSQuotaPeriod=true, kubelet would set cgroup cpu.cfs_period_us to 1000000, but make calculation based on a def...

---

## Actual bucket: **3-7 days** (133 samples)

*Median absolute error: 1.8d, median relative error: 41%*

### Best 3 predictions (most accurate)

**kubernetes/kubernetes #26138** — [k8s.io] Kubectl client [k8s.io] Kubectl rolling-update should support rolling-update to same image [Conformance] {Kubernetes e2e suite}

- Actual: **6.2d** (148.2h, bucket: 3-7 days)
- Predicted: **6.2d** (149.0h, bucket: 3-7 days)
- Error: 50 min (1% off)
- Files changed: 2

> https://console.cloud.google.com/storage/kubernetes-jenkins/logs/kubernetes-e2e-gke/7634/
Failed: [k8s.io] Kubectl client [k8s.io] Kubectl rolling-update should support rolling-update to same image [Conformance] {Kubernetes e2e suite}
```
/go/src/k8s.io/kubernetes/_output/dockerized/go/src/k8s.io/kubernetes/test/e2e/kubectl.go:911
Expected error:
    <*errors.errorString | 0xc820684350>: {...

**kubernetes/kubernetes #1776** — Update demo e2e has unbound variable

- Actual: **4.7d** (112.4h, bucket: 3-7 days)
- Predicted: **4.7d** (113.1h, bucket: 3-7 days)
- Error: 44 min (1% off)
- Files changed: 5

> Saw this in Jenkins:
```
./hack/../cluster/gce/../../hack/e2e-suite/update.sh: line 30: pod_id_list[@]: unbound variable
```

**kubernetes/kubernetes #33375** — Extend `local-up-cluster.sh` to be able to start with the secured port 

- Actual: **3.3d** (78.2h, bucket: 3-7 days)
- Predicted: **3.2d** (77.4h, bucket: 3-7 days)
- Error: 49 min (1% off)
- Files changed: 3

> Followup to https://github.com/kubernetes/kubernetes/pull/31491
Extend `local-up-cluster.sh` to be able to start with the secured port available using https://github.com/kubernetes/kubernetes/pull/31491 and an option to close the insecured port so that its easy to start determining which permissions the controllers need.
The controller manager should try to make use of the secured port hidden behi...

### Worst 3 predictions (least accurate)

**kubernetes/kubernetes #18606** — Reconcile testing docs

- Actual: **3.2d** (76.1h, bucket: 3-7 days)
- Predicted: **10.5d** (252.9h, bucket: 1-4 weeks)
- Error: 7.4d (233% off)
- Files changed: 2

> https://github.com/kubernetes/kubernetes/pull/14112 introduced [docs/devel/e2e-tests.md](https://github.com/kubernetes/kubernetes/blob/master/docs/devel/e2e-tests.md), but that document isn't correct, and contradicts the information in [docs/devel/development.md](https://github.com/kubernetes/kubernetes/blob/master/docs/devel/development.md).  These two docs should be reconciled.

**microsoft/vscode #244403** — Notebook snapshot not restored when reloading VS Code

- Actual: **3.3d** (79.1h, bucket: 3-7 days)
- Predicted: **10.9d** (262.1h, bucket: 1-4 weeks)
- Error: 7.6d (231% off)
- Files changed: 1

> <!-- ⚠️⚠️ Do Not Delete This! bug_report_template ⚠️⚠️ -->
<!-- Please read our Rules of Conduct: https://opensource.microsoft.com/codeofconduct/ -->
<!-- 🕮 Read our guide about submitting issues: https://github.com/microsoft/vscode/wiki/Submitting-Bugs-and-Suggestions -->
<!-- 🔎 Search existing issues to avoid creating duplicates. -->
<!-- 🧪 Test using the latest Insiders build to see if your iss...

**kubernetes/kubernetes #136307** — Graduate job_controller metrics to BETA

- Actual: **6.9d** (165.8h, bucket: 3-7 days)
- Predicted: **3.1w** (519.8h, bucket: 1-4 weeks)
- Error: 2.1w (213% off)
- Files changed: 3

> Parent issue: https://github.com/kubernetes/kubernetes/issues/136107
- path: pkg/controller/job/metrics/metrics.go
    - [x] job_controller_pod_failures_handled_by_failure_policy_total
    - [x] job_controller_terminated_pods_tracking_finalizer_total

---

## Actual bucket: **1-4 weeks** (263 samples)

*Median absolute error: 8.3d, median relative error: 61%*

### Best 3 predictions (most accurate)

**kubernetes/kubernetes #26435** — Node e2e does not return error from copying test artifacts

- Actual: **8.3d** (198.6h, bucket: 1-4 weeks)
- Predicted: **8.3d** (199.0h, bucket: 1-4 weeks)
- Error: 24 min (0% off)
- Files changed: 1

**kubernetes/kubernetes #11471** — HA for kube-dns

- Actual: **12.3d** (295.2h, bucket: 1-4 weeks)
- Predicted: **12.1d** (289.3h, bucket: 1-4 weeks)
- Error: 6.0h (2% off)
- Files changed: 1

> I recently ran into an issue on my cluster because kube-dns unexpectedly went down.
The only error I saw was "2015/07/08 23:18:23 etcdhttp: unexpected error: etcdserver: request timed out"
I'm guessing etcd went down and recovered on its own. However, during this time, I was unable to launch any topologies at all on my cluster which leads me to thinking about some way to make the system more resil...

**kubernetes/kubernetes #135039** — [Failing Test] [sig-cluster-lifecycle] kinder.test.workflow: task-09-e2e-after

- Actual: **11.5d** (275.3h, bucket: 1-4 weeks)
- Predicted: **11.2d** (268.7h, bucket: 1-4 weeks)
- Error: 6.7h (2% off)
- Files changed: 1

> ### Which jobs are failing?
* sig-release-master-informing
* kubeadm-kinder-upgrade-1-34-latest
### Which tests are failing?
* [task-09-e2e-after](https://prow.k8s.io/view/gs/kubernetes-ci-logs/logs/ci-kubernetes-e2e-kubeadm-kinder-upgrade-1-34-latest/1984871857492332544)
### Since when has it been failing?
* First failure: Sat, 18 Oct 2025 07:35:03 UTC
* Latest failure: Sun, 02 Nov 2025 06:36:18...

### Worst 3 predictions (least accurate)

**kubernetes/kubernetes #26526** — Update API Reference script

- Actual: **7.7d** (185.2h, bucket: 1-4 weeks)
- Predicted: **2.7w** (456.0h, bucket: 1-4 weeks)
- Error: 11.3d (146% off)
- Files changed: 1

> Hi, 
there is a minor bug in the [hack/update-api-reference-docs.sh](https://github.com/kubernetes/kubernetes/blob/master/hack/update-api-reference-docs.sh) script or at least some inconsistency. When I run the update script white spaces are ignores with the `-w`option [see line 98](https://github.com/kubernetes/kubernetes/blob/master/hack/update-api-reference-docs.sh#L98) but in the [verify scrip...

**facebook/react #4069** — Stop building react-source gem

- Actual: **2.9w** (479.7h, bucket: 1-4 weeks)
- Predicted: **16.6h** (16.6h, bucket: 1 day)
- Error: 2.8w (97% off)
- Files changed: 5

> I'm not sure how much value there really is in this. react-rails already stopped using it and just builds the files in itself.
cc @rmosolgo

**microsoft/vscode #275061** — Inline chat: need 2 undo to remove a change

- Actual: **9.3d** (224.2h, bucket: 1-4 weeks)
- Predicted: **2.6w** (440.6h, bucket: 1-4 weeks)
- Error: 9.0d (97% off)
- Files changed: 1

> Testing #274768
If you accept an inline chat change, I need 2x undo to remove it again.

---

## Actual bucket: **> 4 weeks** (167 samples)

*Median absolute error: 6.0w, median relative error: 86%*

### Best 3 predictions (most accurate)

**kubernetes/kubernetes #136094** — [Failing Test] cri-proxy [sig node] image volume digest error handling should expect error log for image volume with empty Image.Image

- Actual: **4.8w** (807.0h, bucket: > 4 weeks)
- Predicted: **4.4w** (736.6h, bucket: > 4 weeks)
- Error: 2.9d (9% off)
- Files changed: 1

> ### Which jobs are failing?
https://prow.k8s.io/view/gs/kubernetes-ci-logs/logs/ci-kubernetes-node-e2e-cri-proxy-serial/2001550251227353088
### Which tests are failing?
E2eNode Suite: [It] [sig-node] [Feature:CriProxy] [Serial] Image volume digest error handling [Feature:CriProxy] [FeatureGate:ImageVolumeWithDigest] [Alpha] [Feature:OffByDefault] should expect error log for image volume with empty...

**kubernetes/kubernetes #134737** — failing test[sig-node] Override hostname of Pod [FeatureGate:HostnameOverride] [Beta] a pod with only hostnameOverride field will have hostnameOverride as hostname

- Actual: **4.4w** (742.6h, bucket: > 4 weeks)
- Predicted: **2.6w** (432.7h, bucket: 1-4 weeks)
- Error: 12.9d (42% off)
- Files changed: 2

> https://prow.k8s.io/view/gs/kubernetes-ci-logs/logs/ci-kubernetes-e2e-kind-ipv6/1980349256950616064
https://github.com/kubernetes/kubernetes/compare/183e01c6f...e4fcafba6
https://testgrid.k8s.io/sig-release-master-blocking#kind-ipv6-master
/kind failing-test
/sig node

**microsoft/vscode #287819** — Better Shebang Language Detection (Deno, Bun, etc)

- Actual: **6.0w** (1008.3h, bucket: > 4 weeks)
- Predicted: **3.4w** (570.7h, bucket: 1-4 weeks)
- Error: 2.6w (43% off)
- Files changed: 2

> Along the same lines as #182613, it would be nice if the shebang language detection worked a bit better... especially with /usr/bin/env (-S) where the language/executable after env or env -S is supported, or can determine the type of file, but not a direct match.
ex: `#!/usr/bin/env -S deno -A` or similar should be treated as typescript.
Runtimes really matter, and it would be nice if more were di...

### Worst 3 predictions (least accurate)

**microsoft/vscode #241809** — Make paused indication stronger and clickable

- Actual: **7.4w** (1237.5h, bucket: > 4 weeks)
- Predicted: **12.9h** (12.9h, bucket: 1 day)
- Error: 7.3w (99% off)
- Files changed: 3

> Testing #241788
* make an agent request
* press pause
* the chat output shows a resumed indication but that's very easy to miss
I'd suggest to render this as button so that this stands out more and that I can actually press it to resume the request
<img width="476" alt="Screenshot 2025-02-25 at 08 45 50" src="https://github.com/user-attachments/assets/c1a8d1de-dabb-4521-96ed-71acd4a2a9f6" />

**kubernetes/kubernetes #136910** — Some crashed or OOMKilled containers fail to restart in v1.35

- Actual: **12.5w** (2099.0h, bucket: > 4 weeks)
- Predicted: **1.9d** (46.5h, bucket: 1-3 days)
- Error: 12.2w (98% off)
- Files changed: 3

> ### What happened?
After upgrading Kubernetes from v1.34.2 to v1.35.0, we observed a scenario where a pod with multiple containers does not restart a crashed application container, leaving the pod in an Error state indefinitely.
This behavior was not observed on v1.34.2. Reverting the kubelet back to v1.34.2 causes the issue to disappear.
**Observed Behavior:**
The main container terminates but ne...

**kubernetes/kubernetes #133847** — kubelet_volume_stats_* metrics not available in 1.34

- Actual: **6.3w** (1060.5h, bucket: > 4 weeks)
- Predicted: **1.1d** (25.9h, bucket: 1-3 days)
- Error: 6.2w (98% off)
- Files changed: 5

> ### What happened?
When using Kubernetes version 1.34 `kubelet_volume_stats_*` metrics such as `kubelet_volume_stats_available_bytes` are no longer present in `kubectl get --raw "/api/v1/nodes/$NODE/proxy/metrics"`.
I know that they are in Alpha state and Alpha metrics do not come with any guarantees, but since they are still [documented](https://kubernetes.io/docs/reference/instrumentation/metric...

---
