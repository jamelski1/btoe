# Example Predictions — Model A (model_a_text_only)

Test set: 896 samples

For each actual-duration bucket, this report shows:
- **3 best predictions** (smallest relative error)
- **3 worst predictions** (largest relative error)

---

## Actual bucket: **< 1 day** (86 samples)

*Median absolute error: 2.9d, median relative error: 2406%*

### Best 3 predictions (most accurate)

**kubernetes/kubernetes #136091** — Standard numeric format validation (int32, int64, float, double) is not enforced in CRDs

- Actual: **5.7h** (5.7h, bucket: < 1 day)
- Predicted: **21.8h** (21.8h, bucket: 1 day)
- Error: 16.1h (283% off)
- Files changed: 66

> ### What happened?
CRDs that use standard numeric formats for both integer and number types do not actually enforce these constraints during validation. 
This is a follow up issue of https://github.com/kubernetes/kubernetes/issues/133880
### What did you expect to happen?
Reject invalid integer/number following the defined formats.
### How can we reproduce it (as minimally and precisely as possibl...

**kubernetes/kubernetes #27785** — Panic in DNS Zone Creation: interface conversion: interfaces.ManagedZone is *internal.ManagedZone,  not internal.ManagedZone

- Actual: **6.3h** (6.3h, bucket: < 1 day)
- Predicted: **1.7d** (41.1h, bucket: 1-3 days)
- Error: 1.5d (555% off)
- Files changed: 8

> See https://github.com/kubernetes/kubernetes/pull/27695#issuecomment-227488419
Fix PR incoming shortly.
cc: @mml FYI.

**microsoft/vscode #270394** — .interactive-session styles should not be in chatViewWelcome.css

- Actual: **6.6h** (6.6h, bucket: < 1 day)
- Predicted: **1.9d** (45.3h, bucket: 1-3 days)
- Error: 1.6d (582% off)
- Files changed: 2

> I just noticed this while looking at quick chat- we now have these styles for `.interactive-session` in the welcome views css file https://github.com/microsoft/vscode/blob/3ec367371fdb761eaf951bfeeb9b68b61272d21c/src/vs/workbench/contrib/chat/browser/media/chatViewWelcome.css#L18-L21
But we also have styles for the same selector in chat.css https://github.com/microsoft/vscode/blob/3ec367371fdb761e...

### Worst 3 predictions (least accurate)

**microsoft/vscode #243115** — Selecting `file` from context picker with mouse is a no-op

- Actual: **1.7h** (1.7h, bucket: < 1 day)
- Predicted: **8.2d** (196.9h, bucket: 1-4 weeks)
- Error: 8.1d (11628% off)
- Files changed: 3

> Click this with a mouse:
<img width="1124" alt="Image" src="https://github.com/user-attachments/assets/44b71a95-db3a-4e33-bd21-c1f3a25bc14f" />
This closes quick pick right away making it seem like a no-op
//cc @isidorn

**microsoft/vscode #282527** — Agent sessions: make sidebar toggle visible even in chats

- Actual: **2.2h** (2.2h, bucket: < 1 day)
- Predicted: **9.6d** (229.4h, bucket: 1-4 weeks)
- Error: 9.5d (10267% off)
- Files changed: 5

> When you are in a chat, we show a title:
<img width="571" height="440" alt="Image" src="https://github.com/user-attachments/assets/f415fbd4-f9f6-4264-a197-cce8bea5205f" />
In here the top right should show the sidebar toggle.
//cc @rebornix

**kubernetes/kubernetes #84783** — cpumanager: cpu manager state checkpoint file validate failed after node crash or kubelet down

- Actual: **1.3h** (1.3h, bucket: < 1 day)
- Predicted: **5.4d** (130.5h, bucket: 3-7 days)
- Error: 5.4d (9997% off)
- Files changed: 12

> <!-- Please use this template while reporting a bug and provide as much info as possible. Not doing so may result in your bug not being addressed in a timely manner. Thanks!
If the matter is security related, please disclose it privately via https://kubernetes.io/security/
-->

**What happened**:
Currently, static policy in cpumanager validate state checkpoint file when kubelet starts if cpu bindi...

---

## Actual bucket: **1 day** (90 samples)

*Median absolute error: 3.4d, median relative error: 512%*

### Best 3 predictions (most accurate)

**kubernetes/kubernetes #135001** — failing kubelet skew jobs with kubeadm (kinder)

- Actual: **21.5h** (21.5h, bucket: 1 day)
- Predicted: **1.1d** (26.8h, bucket: 1-3 days)
- Error: 5.3h (25% off)
- Files changed: 2

> ### Which jobs are failing?
https://testgrid.k8s.io/sig-cluster-lifecycle-kubeadm#kubeadm-kinder-kubelet-1-33-on-latest
https://testgrid.k8s.io/sig-cluster-lifecycle-kubeadm#kubeadm-kinder-kubelet-1-32-on-latest

### Which tests are failing?
Kubernetes e2e suite.[It] [sig-node] Pods Extended (pod generation) Pod Generation issue 500 podspec updates and verify generation and observedGeneration even...

**microsoft/vscode #243228** — MCP: Install via protocol activation

- Actual: **16.9h** (16.9h, bucket: 1 day)
- Predicted: **21.9h** (21.9h, bucket: 1 day)
- Error: 5.1h (30% off)
- Files changed: 5

> We've had some asks from registries to support protocol activation as a way to install MCP servers (i.e. via a link.) Let's support this.
Tentatively assigning to this month but it's not as high a priority item.

**microsoft/vscode #248317** — Settings auto save reset the scroll and selected feature

- Actual: **23.9h** (23.9h, bucket: 1 day)
- Predicted: **1.5d** (36.9h, bucket: 1-3 days)
- Error: 13.0h (55% off)
- Files changed: 1

> <!-- ⚠️⚠️ Do Not Delete This! bug_report_template ⚠️⚠️ -->
<!-- Please read our Rules of Conduct: https://opensource.microsoft.com/codeofconduct/ -->
<!-- 🕮 Read our guide about submitting issues: https://github.com/microsoft/vscode/wiki/Submitting-Bugs-and-Suggestions -->
<!-- 🔎 Search existing issues to avoid creating duplicates. -->
<!-- 🧪 Test using the latest Insiders build to see if your iss...

### Worst 3 predictions (least accurate)

**microsoft/vscode #301672** — Sessions: progress bar when session loads goes through the previous content

- Actual: **10.7h** (10.7h, bucket: 1 day)
- Predicted: **2.1w** (351.1h, bucket: 1-4 weeks)
- Error: 2.0w (3196% off)
- Files changed: 1

> Often seeing a progress bar appearing when opening a session that travels through the previous content. It seems weirdly aligned.

**microsoft/vscode #243372** — Tree sitter loses coloring when moving lines up and down

- Actual: **8.2h** (8.2h, bucket: 1 day)
- Predicted: **10.1d** (242.7h, bucket: 1-4 weeks)
- Error: 9.8d (2860% off)
- Files changed: 1

> File: https://github.com/microsoft/vscode/blob/d7d36053045528f020a40ce519b162673b9ed5a9/src/vs/workbench/contrib/terminal/browser/xterm/xtermTerminal.ts#L242
![Image](https://github.com/user-attachments/assets/afd45ef5-a1a0-4001-ad9b-7d78aed2314e)

**kubernetes/kubernetes #3640** — Round robin load balancer can overwhelm first pod behind service

- Actual: **10.4h** (10.4h, bucket: 1 day)
- Predicted: **12.3d** (296.1h, bucket: 1-4 weeks)
- Error: 11.9d (2745% off)
- Files changed: 4

> This is particularly easy to do with a new cluster.
Create a service `S` and deploy `N` pods behind it. Start up `M` pods which create a persistent connection to service `S`.
Because the round robin load balancer always starts at the 0th endpoint, and the endpoint list is consistent cluster-wide, you will see that you now have `M` connections to Pod 1, and 0 connections to all other pods 2 through...

---

## Actual bucket: **1-3 days** (157 samples)

*Median absolute error: 3.0d, median relative error: 177%*

### Best 3 predictions (most accurate)

**kubernetes/kubernetes #136473** — Extend DRA performance tests to cover implicit resources

- Actual: **1.3d** (32.3h, bucket: 1-3 days)
- Predicted: **1.4d** (33.5h, bucket: 1-3 days)
- Error: 1.2h (4% off)
- Files changed: 3

> [Current performance tests](https://github.com/kubernetes/kubernetes/blob/master/test/integration/scheduler_perf/dra/extendedresource/extendedresource_test.go) cover only explicit extended resources. It would be nice to extend them to cover also implicit resources. This would allow to measure and compare testing results for both types of resources.
/sig scheduling

**microsoft/vscode #247649** — Quick pick padding is inconsistent

- Actual: **2.9d** (69.7h, bucket: 1-3 days)
- Predicted: **3.0d** (72.9h, bucket: 3-7 days)
- Error: 3.2h (5% off)
- Files changed: 1

> <img width="347" alt="Image" src="https://github.com/user-attachments/assets/7622df49-59fd-4c7b-ac66-aaf9bf0fed88" />
- Top padding is larger than left padding
- Input border doesn't align horizontally with the selected item background - I don't see why it wouldn't

**kubernetes/kubernetes #5278** — Kind wildcarding/discovery in kubectl

- Actual: **1.8d** (42.7h, bucket: 1-3 days)
- Predicted: **1.9d** (44.7h, bucket: 1-3 days)
- Error: 2.1h (5% off)
- Files changed: 7

> Forked from #3233.
I think the last proposal was to support:
```
kubectl describe all
kubectl describe all foo
```
where "all" implies all known kinds.
@brendandburns @smarterclayton

### Worst 3 predictions (least accurate)

**kubernetes/kubernetes #73264** — --cpu-cfs-quota-period should not have effect if feature gate CPUCFSQuotaPeriod is not enabled

- Actual: **1.2d** (29.7h, bucket: 1-3 days)
- Predicted: **3.4w** (578.6h, bucket: 1-4 weeks)
- Error: 3.3w (1848% off)
- Files changed: 2

> <!-- Please use this template while reporting a bug and provide as much info as possible. Not doing so may result in your bug not being addressed in a timely manner. Thanks!-->

**What happened**:
When run kubelet with "--cpu-cfs-quota-period 1000ms"  and without --feature-gates=CustomCPUCFSQuotaPeriod=true, kubelet would set cgroup cpu.cfs_period_us to 1000000, but make calculation based on a def...

**microsoft/vscode #268390** — Secondary side bar shouldnt open by default in vscode.dev

- Actual: **1.7d** (41.2h, bucket: 1-3 days)
- Predicted: **3.6w** (609.7h, bucket: 1-4 weeks)
- Error: 3.4w (1379% off)
- Files changed: 1

> When we switched to show the secondary side bar with the walkthrough or in a new workspace, this is also getting applied in vscode.dev. We shouldn't open the secondary side bar in these scenarios as Copilot is not supported
<img width="2540" height="1382" alt="Image" src="https://github.com/user-attachments/assets/57c03b29-9abd-4ffa-b7ae-5472750e80db" />
Thanks @kieferrm for pointing this out!

**kubernetes/kubernetes #135963** — [Flake] test/integration/servicecidr: TestServiceAllocation fails with "range is full"

- Actual: **2.0d** (48.2h, bucket: 1-3 days)
- Predicted: **3.0w** (507.5h, bucket: 1-4 weeks)
- Error: 2.7w (953% off)
- Files changed: 2

> ### Which jobs are flaking?
ci-kubernetes-integration-master
### Which tests are flaking?
k8s.io/kubernetes/test/integration/servicecidr TestServiceAllocation/IP_allocator_only
### Since when has it been flaking?
Observed on Dec 28, 2025
### Testgrid link
https://testgrid.k8s.io/sig-release-master-blocking#integration-master
### Reason for failure (if possible)
The test fails with an IP exhaustion...

---

## Actual bucket: **3-7 days** (133 samples)

*Median absolute error: 2.0d, median relative error: 43%*

### Best 3 predictions (most accurate)

**microsoft/vscode #235819** — Switching code editor tabs slow in workspace with many tests (~150,000)

- Actual: **5.9d** (140.7h, bucket: 3-7 days)
- Predicted: **6.0d** (143.0h, bucket: 3-7 days)
- Error: 2.3h (2% off)
- Files changed: 2

> <!-- ⚠️⚠️ Do Not Delete This! bug_report_template ⚠️⚠️ -->
<!-- Please read our Rules of Conduct: https://opensource.microsoft.com/codeofconduct/ -->
<!-- 🕮 Read our guide about submitting issues: https://github.com/microsoft/vscode/wiki/Submitting-Bugs-and-Suggestions -->
<!-- 🔎 Search existing issues to avoid creating duplicates. -->
<!-- 🧪 Test using the latest Insiders build to see if your iss...

**kubernetes/kubernetes #136350** — Image build is failing - post-kubernetes-push-e2e-node-perf-npb-is-test-images

- Actual: **4.7d** (111.9h, bucket: 3-7 days)
- Predicted: **4.7d** (113.9h, bucket: 3-7 days)
- Error: 2.0h (2% off)
- Files changed: 5

> Please see logs in:
https://storage.googleapis.com/kubernetes-ci-logs/logs/post-kubernetes-push-e2e-node-perf-npb-is-test-images/2011957383982485504/build-log.txt
Log snippet:
```
#6 0.460 W: The repository 'http://security.debian.org/debian-security stretch/updates Release' does not have a Release file.
#6 0.460 W: The repository 'http://deb.debian.org/debian stretch Release' does not have a Rele...

**microsoft/vscode #240307** — MSAL Authentication: throws error around decrypting data - Error Code 2148073483

- Actual: **5.8d** (139.9h, bucket: 3-7 days)
- Predicted: **6.0d** (144.8h, bucket: 3-7 days)
- Error: 4.9h (4% off)
- Files changed: 2

> # Edit from maintainer
Hi, I got a response from someone who has given me a potential workaround for this DPAPI issue.
* Delete the directory: `%userprofile%\AppData\Local\Microsoft\IdentityCache`
* Try signing in with `msal` again
---
# Original issue filed
During the sign in to Azure process with the new msal authentication and extension `ms-azuretools.vscode-azureresourcegroups` Version 0.10.4,...

### Worst 3 predictions (least accurate)

**microsoft/vscode #244403** — Notebook snapshot not restored when reloading VS Code

- Actual: **3.3d** (79.1h, bucket: 3-7 days)
- Predicted: **12.2d** (293.2h, bucket: 1-4 weeks)
- Error: 8.9d (271% off)
- Files changed: 1

> <!-- ⚠️⚠️ Do Not Delete This! bug_report_template ⚠️⚠️ -->
<!-- Please read our Rules of Conduct: https://opensource.microsoft.com/codeofconduct/ -->
<!-- 🕮 Read our guide about submitting issues: https://github.com/microsoft/vscode/wiki/Submitting-Bugs-and-Suggestions -->
<!-- 🔎 Search existing issues to avoid creating duplicates. -->
<!-- 🧪 Test using the latest Insiders build to see if your iss...

**microsoft/vscode #248686** — Move away and remove duplicated utilities functions

- Actual: **3.7d** (89.5h, bucket: 3-7 days)
- Predicted: **13.6d** (327.1h, bucket: 1-4 weeks)
- Error: 9.9d (265% off)
- Files changed: 10

> https://github.com/microsoft/vscode/pull/248685 deprecates some utils that duplicate existing function. Their usages should be adopted/fixed and ultimately the duplicates should be removed

**kubernetes/kubernetes #18606** — Reconcile testing docs

- Actual: **3.2d** (76.1h, bucket: 3-7 days)
- Predicted: **11.2d** (269.2h, bucket: 1-4 weeks)
- Error: 8.0d (254% off)
- Files changed: 2

> https://github.com/kubernetes/kubernetes/pull/14112 introduced [docs/devel/e2e-tests.md](https://github.com/kubernetes/kubernetes/blob/master/docs/devel/e2e-tests.md), but that document isn't correct, and contradicts the information in [docs/devel/development.md](https://github.com/kubernetes/kubernetes/blob/master/docs/devel/development.md).  These two docs should be reconciled.

---

## Actual bucket: **1-4 weeks** (263 samples)

*Median absolute error: 9.2d, median relative error: 65%*

### Best 3 predictions (most accurate)

**kubernetes/kubernetes #26435** — Node e2e does not return error from copying test artifacts

- Actual: **8.3d** (198.6h, bucket: 1-4 weeks)
- Predicted: **8.3d** (200.2h, bucket: 1-4 weeks)
- Error: 1.6h (1% off)
- Files changed: 1

**microsoft/vscode #284011** — Flip defaults for chat.restoreLastPanelSession

- Actual: **7.9d** (188.5h, bucket: 1-4 weeks)
- Predicted: **7.8d** (186.3h, bucket: 1-4 weeks)
- Error: 2.2h (1% off)
- Files changed: 1

> Default should be `false`.
Just ExP control does not get all users. So the defaults should change.
If you are up for it - consider as a candidate (I am fine if we do it in Dec/Jan milestone).

**kubernetes/kubernetes #135247** — [Failing Test] [sig-node] ImageVolume should succeed with pod and pull policy of Always [MinimumKubeletVersion:1.35]

- Actual: **4.2w** (698.7h, bucket: 1-4 weeks)
- Predicted: **4.1w** (688.3h, bucket: 1-4 weeks)
- Error: 10.4h (1% off)
- Files changed: 1

> ### Which jobs are failing?
* sig-release-master-blocking
* gce-cos-master-default
### Which tests are failing?
* [Kubernetes e2e suite.[It] [sig-node] ImageVolume should succeed with pod and pull policy of Always [MinimumKubeletVersion:1.35]](https://prow.k8s.io/view/gs/kubernetes-ci-logs/logs/ci-kubernetes-e2e-gci-gce/1988078996033638400)
### Since when has it been failing?
* First failure: Sun,...

### Worst 3 predictions (least accurate)

**kubernetes/kubernetes #135825** — Kubelet SyncTerminatedPod times out after 30s due to race with cleanupOrphanedPodCgroups

- Actual: **7.7d** (185.2h, bucket: 1-4 weeks)
- Predicted: **3.4w** (577.9h, bucket: 1-4 weeks)
- Error: 2.3w (212% off)
- Files changed: 34

> ### What happened?
In this [OpenShift CI run](https://prow.ci.openshift.org/view/gs/test-platform-results/logs/periodic-ci-openshift-multiarch-master-nightly-4.21-ocp-e2e-ovn-remote-s2s-libvirt-ppc64le/1999572809340162048), the upstream `[sig-node] Lifecycle sleep action zero value when create a pod with lifecycle hook using sleep action with a duration of zero seconds prestop hook using sleep act...

**microsoft/vscode #244637** — confusing default configuration value

- Actual: **8.8d** (210.7h, bucket: 1-4 weeks)
- Predicted: **2.9w** (483.1h, bucket: 1-4 weeks)
- Error: 11.4d (129% off)
- Files changed: 5

> Testing https://github.com/microsoft/vscode/issues/244525
When user types "mcp" in `settings.json`, the next default block is automatically added to the config:
```json
"mcp": {
        "inputs": [],
        "servers": {
            "mcp-server-time": {
                "command": "python",
                "args": [
                    "-m",
                    "mcp_server_time",...

**kubernetes/kubernetes #135621** — DATA RACE garbage collector: blockingDependents

- Actual: **8.0d** (192.0h, bucket: 1-4 weeks)
- Predicted: **2.3w** (380.7h, bucket: 1-4 weeks)
- Error: 7.9d (98% off)
- Files changed: 7

> ### What happened?
kube-controller-manager compiled with -race and tested with various E2E tests in a kind cluster [led to](https://prow.k8s.io/view/gs/kubernetes-ci-logs/pr-logs/pull/133844/pull-kubernetes-e2e-kind-alpha-beta-features-race/1996896534980988928):

#### kube-system/kube-controller-manager-kind-control-plane/kube-controller-manager
  
      Read at 0x00c004c37cf8 by goroutine 2258:...

---

## Actual bucket: **> 4 weeks** (167 samples)

*Median absolute error: 6.0w, median relative error: 86%*

### Best 3 predictions (most accurate)

**microsoft/vscode #244752** — `chat.mcp.enabled` doesn't affect API MCP server

- Actual: **4.7w** (788.4h, bucket: > 4 weeks)
- Predicted: **4.5w** (750.8h, bucket: > 4 weeks)
- Error: 1.6d (5% off)
- Files changed: 1

> * have an extension that contributes an MCP server config
* disable `chat.mcp.enabled`
* the MCP server is still there

**microsoft/vscode #214424** — Just restart EH automatically on extension update?

- Actual: **4.8w** (799.4h, bucket: > 4 weeks)
- Predicted: **3.0w** (512.0h, bucket: 1-4 weeks)
- Error: 12.0d (36% off)
- Files changed: 5

> I love the new feature that extension updates do not require the whole window reload. 
But right now it still requires an action from me to click on "Restart Extensions".
Can you remind me why don't we just restart the EH automatically on extension update? Are we afraid that we might break some other extension?
Can we do some detection to see if it is "safe" to restart automatically? Or can we do...

**microsoft/vscode #277174** — Terminal tabs view shows when there's only a single terminal

- Actual: **4.9w** (815.3h, bucket: > 4 weeks)
- Predicted: **2.8w** (468.9h, bucket: 1-4 weeks)
- Error: 2.1w (42% off)
- Files changed: 1

> <img width="905" height="283" alt="Image" src="https://github.com/user-attachments/assets/584b47ef-e0bc-474f-a594-2851d50ce4e5" />
Before, it only showed when there was more than one 
cc @Tyriar

### Worst 3 predictions (least accurate)

**microsoft/vscode #280050** — List: focus outline flicker when clicking into element without prior selection

- Actual: **9.6w** (1618.4h, bucket: > 4 weeks)
- Predicted: **20.7h** (20.7h, bucket: 1 day)
- Error: 9.5w (99% off)
- Files changed: 1

> I always found it annoying that a click into any list is first briefly flashing the outline and then removes it:
![Image](https://github.com/user-attachments/assets/89834a18-2b42-4237-8a44-47fc468f8cc3)
The rule that triggers this is:
https://github.com/microsoft/vscode/blob/4fe2ba4f68694888da7625e030c0661c4caad8a1/src/vs/workbench/browser/media/style.css#L267
Ideally if a click results in an elem...

**microsoft/vscode #241809** — Make paused indication stronger and clickable

- Actual: **7.4w** (1237.5h, bucket: > 4 weeks)
- Predicted: **21.7h** (21.7h, bucket: 1 day)
- Error: 7.2w (98% off)
- Files changed: 3

> Testing #241788
* make an agent request
* press pause
* the chat output shows a resumed indication but that's very easy to miss
I'd suggest to render this as button so that this stands out more and that I can actually press it to resume the request
<img width="476" alt="Screenshot 2025-02-25 at 08 45 50" src="https://github.com/user-attachments/assets/c1a8d1de-dabb-4521-96ed-71acd4a2a9f6" />

**facebook/react #30627** — [Compiler]: Using `for` loop for array of strings

- Actual: **10.8w** (1816.6h, bucket: > 4 weeks)
- Predicted: **1.4d** (34.8h, bucket: 1-3 days)
- Error: 10.6w (98% off)
- Files changed: 1

> ### What kind of issue is this?
- [ ] React Compiler core (the JS output is incorrect, or your app works incorrectly after optimization)
- [X] babel-plugin-react-compiler (build issue installing or using the Babel plugin)
- [ ] eslint-plugin-react-compiler (build issue installing or using the eslint plugin)
- [ ] react-compiler-healthcheck (build issue installing or using the healthcheck script)
#...

---
