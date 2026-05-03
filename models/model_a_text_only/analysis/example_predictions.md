# Example Predictions — Model A (model_a_text_only)

Test set: 865 samples

For each actual-duration bucket, this report shows:
- **3 best predictions** (smallest relative error)
- **3 worst predictions** (largest relative error)

---

## Actual bucket: **< 1 day** (72 samples)

*Median absolute error: 3.3d, median relative error: 2522%*

### Best 3 predictions (most accurate)

**microsoft/vscode #255787** — Workspace chat history should format file references better

- Actual: **7.9h** (7.9h, bucket: < 1 day)
- Predicted: **1.3d** (31.6h, bucket: 1-3 days)
- Error: 23.8h (302% off)
- Files changed: 1

> <img width="740" height="282" alt="Image" src="https://github.com/user-attachments/assets/fb8f6cd6-d111-4305-99f4-f6bb3ba07583" />

**microsoft/vscode #254880** — Undoing with a `Try again` action in the history doesn't make it dissapear

- Actual: **7.7h** (7.7h, bucket: < 1 day)
- Predicted: **1.6d** (39.5h, bucket: 1-3 days)
- Error: 1.3d (414% off)
- Files changed: 1

> At some point the agent failed to edit further
<img width="404" height="623" alt="Image" src="https://github.com/user-attachments/assets/0da3b2ad-2f26-48ee-aee2-0ba2ae979464" />
If I clicked Undo a few times, that error message staying in the chat:
<img width="553" height="498" alt="Image" src="https://github.com/user-attachments/assets/cb8fc15c-982c-44bb-935c-f102d8893c85" />

**microsoft/vscode #301997** — Chat image carousel doesn't always show title

- Actual: **3.0h** (3.0h, bucket: < 1 day)
- Predicted: **16.5h** (16.5h, bucket: 1 day)
- Error: 13.5h (445% off)
- Files changed: 2

> Testing #301610
Opened the image carousel from a chat, but it doesn't always have a title in the top left. I couldn't figure out how to reproduce this though.
<img width="1392" height="1294" alt="Image" src="https://github.com/user-attachments/assets/98309d72-cdc4-4aae-a1ea-22a9373ce9be" />
<img width="1393" height="1322" alt="Image" src="https://github.com/user-attachments/assets/06d12172-e671-4e...

### Worst 3 predictions (least accurate)

**microsoft/vscode #253363** — Opening secondary sidebar in new workspaces should skip web

- Actual: **2.0h** (2.0h, bucket: < 1 day)
- Predicted: **5.3d** (126.8h, bucket: 3-7 days)
- Error: 5.2d (6346% off)
- Files changed: 3

> fyi @isidorn a result of the experiment
<img width="418" alt="Image" src="https://github.com/user-attachments/assets/4bd3891d-42ac-4e97-80d1-7919d6d78a95" />
In vscode.dev/github.dev the secondary sidebar is empty.

**kubernetes/kubernetes #136527** — Job validation error message is misleading when updating .status.startTime

- Actual: **2.4h** (2.4h, bucket: < 1 day)
- Predicted: **6.2d** (147.8h, bucket: 3-7 days)
- Error: 6.1d (6094% off)
- Files changed: 3

> ### What happened?
I encountered a confusing validation error while trying to update the `.status.startTime` of an existing  
Job.
The error message received was:
```bash
Job.batch "job-c4nbt" is invalid: status.startTime: Required value: startTime cannot be removed for unsuspended job
```
However, I am not trying to remove the `startTime`, but rather update it. I checked the code and found that t...

**facebook/react #9102** — [Fiber] Check for requestAnimationFrame throws when react-dom is required on the server

- Actual: **3.5h** (3.5h, bucket: < 1 day)
- Predicted: **9.0d** (216.5h, bucket: 1-4 weeks)
- Error: 8.9d (6057% off)
- Files changed: 3

> **Do you want to request a *feature* or report a *bug*?**
Bug-ish
**What is the current behavior?**
When doing server-side rendering with React, requiring `react-dom` (which transitively requires `ReactDOMFrameScheduling.js`) throws an exception because rAF is not defined.
```
Invariant Violation: React depends on requestAnimationFrame. Make sure that you load a polyfill in older browsers.
    at...

---

## Actual bucket: **1 day** (91 samples)

*Median absolute error: 3.6d, median relative error: 578%*

### Best 3 predictions (most accurate)

**microsoft/vscode #247672** — Chat: Add consistent icon order across modes

- Actual: **18.2h** (18.2h, bucket: 1 day)
- Predicted: **23.1h** (23.1h, bucket: 1 day)
- Error: 4.9h (27% off)
- Files changed: 1

> <!-- ⚠️⚠️ Do Not Delete This! feature_request_template ⚠️⚠️ -->
<!-- Please read our Rules of Conduct: https://opensource.microsoft.com/codeofconduct/ -->
<!-- Please search existing issues to avoid creating duplicates. -->
While testing https://github.com/microsoft/vscode/issues/247399, I noticed that there's an inconsistent order of icons when switching between modes.
Namely, the voice chat icon...

**kubernetes/kubernetes #135894** — job integration: TestUpdateJobPodResources "field is immutable" flake

- Actual: **21.1h** (21.1h, bucket: 1 day)
- Predicted: **1.6d** (38.4h, bucket: 1-3 days)
- Error: 17.3h (82% off)
- Files changed: 1

> ### Which jobs are flaking?
ci-kubernetes-integration-master and similar jobs for other platforms.
https://storage.googleapis.com/k8s-triage/index.html?text=field%20is%20immutable&test=k8s.io%2Fkubernetes%2Ftest%2Fintegration

### Which tests are flaking?
`TestUpdateJobPodResources/suspended_job,_feature_gate_enabled,_update_resources` in test/integration/job.

### Since when has it been flaking?...

**facebook/react #1049** — jsx-compiler.html shouldn't show Live/Compiled switcher

- Actual: **22.7h** (22.7h, bucket: 1 day)
- Predicted: **1.8d** (44.4h, bucket: 1-3 days)
- Error: 21.7h (96% off)
- Files changed: 2

> http://facebook.github.io/react/jsx-compiler.html
@chenglou

### Worst 3 predictions (least accurate)

**microsoft/vscode #264515** — Double click in empty Chat Sessions list should add new session

- Actual: **10.2h** (10.2h, bucket: 1 day)
- Predicted: **13.1d** (315.3h, bucket: 1-4 weeks)
- Error: 12.7d (2980% off)
- Files changed: 2

> Double click in empty Explorer area creates a new empty file (same effect as +)
Same pattern should be followed for all views in the Chat Sessions view container. E.g. clicking on an empty space in Claude Code should just create a new claude code session.
fyi @jo-oikawa @roblourens

**kubernetes/kubernetes #21777** — e2e script refactor broke ubernetes-lite e2e tests

- Actual: **13.3h** (13.3h, bucket: 1 day)
- Predicted: **2.2w** (364.5h, bucket: 1-4 weeks)
- Error: 2.1w (2643% off)
- Files changed: 1

> #21524 broke ubernetes-lite e2e tests.  PR to fix incoming.
Specifically:
https://github.com/kubernetes/kubernetes/blob/ac644e03bd6acb322beb66e0e51c2dba1051dfcd/hack/jenkins/job-configs/kubernetes-e2e.yaml#L159
setting KUBE_GCE_ZONE to an empty string causes it to be defaulted to (currently) "us-central1-b" rather than the zone in which the master components reside, leading to the following error:...

**kubernetes/kubernetes #27657** — GCE Multizone: Cannot create volumes in non-master zones

- Actual: **23.3h** (23.3h, bucket: 1 day)
- Predicted: **3.4w** (571.1h, bucket: 1-4 weeks)
- Error: 3.3w (2355% off)
- Files changed: 9

> Due to #27656, users are unable to create volumes in non-master zones.  The volume cannot be found, and so effectively only one zone is usable for persistent storage (or, in the case of HA master, none of them are).
Fix coming in the next hour or so...

---

## Actual bucket: **1-3 days** (150 samples)

*Median absolute error: 3.3d, median relative error: 176%*

### Best 3 predictions (most accurate)

**kubernetes/kubernetes #370** — Unable to start example app before enabling the cloud storage API

- Actual: **1.3d** (32.1h, bucket: 1-3 days)
- Predicted: **1.3d** (31.8h, bucket: 1-3 days)
- Error: 21 min (1% off)
- Files changed: 1

> Before enabling the cloud storage API, I'm unable to launch the test cluster. dev-build-and-up.sh appears to run successfully, but hangs at the end as the machines have not been properly configured. 
From /var/log/startupscript.log on the kubernetes-master:
AccessDeniedException: 403 Access Not Configured. Please go to the Google Developers Console (https://cloud.google.com/console#/project) for y...

**microsoft/vscode #247486** — Transfer chat session only works on new workspace

- Actual: **3.0d** (70.8h, bucket: 1-3 days)
- Predicted: **2.9d** (70.0h, bucket: 1-3 days)
- Error: 50 min (1% off)
- Files changed: 1

> - From a workspace with files in it, ask Copilot Chat to create a new project
- Go through the new workspace flow- it asks you to open an empty folder
- Pick an empty folder that has never been opened in vscode before
- New workspace flow works, continues setting up project 👍 
- But, if you pick an empty folder that you have used before, chat view is broken and empty
When switching to use the `Cha...

**facebook/react #988** — support form novalidate attribute

- Actual: **2.5d** (61.0h, bucket: 1-3 days)
- Predicted: **2.5d** (59.8h, bucket: 1-3 days)
- Error: 1.2h (2% off)
- Files changed: 1

> Using v0.8, the `novalidate` attribute on a `form` component gets stripped. Could we add it to the whitelisted attributes?
More info about the attribute here:
http://www.w3.org/TR/html5/forms.html#attr-fs-novalidate

### Worst 3 predictions (least accurate)

**microsoft/vscode #297689** — 'Open Chat Customizations' button is too much

- Actual: **1.4d** (32.5h, bucket: 1-3 days)
- Predicted: **2.5w** (427.2h, bucket: 1-4 weeks)
- Error: 2.3w (1216% off)
- Files changed: 13

> Whenever instructions/skill/agent file open in an editor, the button 'Open Chat Customizations` shows up.
<img width="931" height="539" alt="Image" src="https://github.com/user-attachments/assets/e7f5dcd5-595c-43b8-bc9d-b9a4656925fb" />
I think its too much and should be removed
- It's not an action that I would typically invoke when editing in a prompt file
- It looks lost

**kubernetes/kubernetes #135822** — TestReplaceEvents is flaky

- Actual: **1.1d** (25.6h, bucket: 1-3 days)
- Predicted: **12.8d** (306.4h, bucket: 1-4 weeks)
- Error: 11.7d (1095% off)
- Files changed: 1

> ### Which jobs are flaking?
TestReplaceEvents in client-go https://github.com/kubernetes/kubernetes/blame/bb52ae5e24a4eb118460e8feadee86b9f41b4244/staging/src/k8s.io/client-go/tools/cache/controller_test.go#L901 is flaking and failed in the smoke tests run as part of kubernetes/publishing-bot
### Which tests are flaking?
TestReplaceEvents/Delete_all_objects
Ref: https://github.com/kubernetes/kuber...

**kubernetes/kubernetes #34491** — vSphere cloud provider: re-use session for vCenter logins

- Actual: **1.1d** (27.5h, bucket: 1-3 days)
- Predicted: **13.1d** (313.9h, bucket: 1-4 weeks)
- Error: 11.9d (1040% off)
- Files changed: 2

> **Kubernetes version**:
1.3+
**Environment**:
- **Cloud provider or hardware configuration**: vSphere
vSphere cloud provider creates will create a new login session each and every time the plugin is invoked.  This creates a substantial login/logoffs attempts in vCenter which can impact performance and stability.  The session should be re-used if possible instead of creating a new one each time.

---

## Actual bucket: **3-7 days** (137 samples)

*Median absolute error: 2.8d, median relative error: 61%*

### Best 3 predictions (most accurate)

**kubernetes/kubernetes #136031** — [Failing-test] Kubelet panic in NodeDeclareFeatures code

- Actual: **5.8d** (140.1h, bucket: 3-7 days)
- Predicted: **5.9d** (141.7h, bucket: 3-7 days)
- Error: 1.7h (1% off)
- Files changed: 2

> ### Which jobs are failing?
alpha jobs
### Which tests are failing?
Entire job.

### Since when has it been failing?
Test grid for some reason doesn't go very far back.
### Testgrid link
https://testgrid.k8s.io/sig-node-containerd#ci-node-e2e-containerd-alpha-features
### Reason for failure (if possible)
```
I0105 07:36:00.527576    2667 kubelet.go:2611] "SyncLoop DELETE" source="api" pods=["mirro...

**kubernetes/kubernetes #134789** — (DRA) Requests field not set for config FromClass in ResourceClaim.status.allocation.devices.config

- Actual: **4.5d** (107.6h, bucket: 3-7 days)
- Predicted: **4.4d** (106.2h, bucket: 3-7 days)
- Error: 1.5h (1% off)
- Files changed: 4

> ### What happened?
When creating a ResourceClaim with 2 requests with 2 different device class that have a config, the config reported in the allocation devices status is not mentioning from which request the config is coming from. So the DRA-Drivers cannot identify the configuration belonging to the request it is supposed to handle.
```yaml
apiVersion: resource.k8s.io/v1
kind: ResourceClaim
metad...

**kubernetes/kubernetes #137687** — beta-feature enabled clusters are broken in master

- Actual: **5.2d** (123.6h, bucket: 3-7 days)
- Predicted: **5.3d** (126.2h, bucket: 3-7 days)
- Error: 2.6h (2% off)
- Files changed: 7

> ### Which jobs are failing?
ci-kubernetes-e2e-kind-beta-enabled 
### Which tests are failing?
breforesuite ... cluster is unhealthy
### Since when has it been failing?
march 12th
diff is https://github.com/kubernetes/kubernetes/compare/f7f694e5e...4e2bbc78b
### Testgrid link
https://testgrid.k8s.io/sig-release-master-informing#kind-master-beta-enabled
### Reason for failure (if possible)
times out...

### Worst 3 predictions (least accurate)

**kubernetes/kubernetes #135621** — DATA RACE garbage collector: blockingDependents

- Actual: **5.9d** (142.0h, bucket: 3-7 days)
- Predicted: **4.4w** (738.2h, bucket: > 4 weeks)
- Error: 3.5w (420% off)
- Files changed: 7

> ### What happened?
kube-controller-manager compiled with -race and tested with various E2E tests in a kind cluster [led to](https://prow.k8s.io/view/gs/kubernetes-ci-logs/pr-logs/pull/133844/pull-kubernetes-e2e-kind-alpha-beta-features-race/1996896534980988928):

#### kube-system/kube-controller-manager-kind-control-plane/kube-controller-manager
  
      Read at 0x00c004c37cf8 by goroutine 2258:...

**microsoft/vscode #245707** — Error starting github: CodeExpectedError: Variable 'github_token'

- Actual: **3.2d** (77.5h, bucket: 3-7 days)
- Predicted: **13.3d** (320.1h, bucket: 1-4 weeks)
- Error: 10.1d (313% off)
- Files changed: 1

> Error starting github: CodeExpectedError: Variable 'github_token' must be defined in an 'inputs' section of the debug or task configuration.
cc @digitarald 
Here is my config:
```
{
    "@azure.argTenant": "",
    "mcp": {
        "servers": {
            "github": {
                "command": "docker",
                "args": [
                    "run",
                    "-i",...

**microsoft/vscode #302993** — Sessions: The session filter displays two `Local` session types

- Actual: **3.1d** (74.0h, bucket: 3-7 days)
- Predicted: **11.8d** (282.4h, bucket: 1-4 weeks)
- Error: 8.7d (282% off)
- Files changed: 1

> If you click the filter icon in the sessions list, you'll see two `Local` options. The top one appears to be the `Local` sessions in VS Code, and the second one appears to be "Copilot CLI". That said, we should probably hide the former and rename the later? That way we have three options: Copilot CLI, Claude, and Cloud? That would match the terminology and VS Code and be more direct with what thes...

---

## Actual bucket: **1-4 weeks** (239 samples)

*Median absolute error: 10.0d, median relative error: 60%*

### Best 3 predictions (most accurate)

**microsoft/vscode #245646** — Chat - inline chat view zone bottom gap

- Actual: **9.1d** (217.7h, bucket: 1-4 weeks)
- Predicted: **9.0d** (216.7h, bucket: 1-4 weeks)
- Error: 58 min (0% off)
- Files changed: 1

> <img width="1017" alt="Image" src="https://github.com/user-attachments/assets/7ec42329-10e3-4404-ab8d-fe6152bf202e" />

**kubernetes/kubernetes #135616** — kubectl apply with --dry-run=client - docs confusing/inaccurate

- Actual: **8.6d** (205.4h, bucket: 1-4 weeks)
- Predicted: **8.7d** (208.7h, bucket: 1-4 weeks)
- Error: 3.3h (2% off)
- Files changed: 3

> Hi,
> --dry-run='none':
>         Must be "none", "server", or "client". **If client strategy, only print the object that would be sent, without sending it**. If server strategy, submit server-side request without persisting the resource.
The output (without -o yaml) does not "print the object that would be sent" - it just gives a one-liner e.g. the manifest has been configured or unchanged
The ou...

**microsoft/vscode #302003** — Image Carousel: Allow zoom

- Actual: **2.6w** (443.8h, bucket: 1-4 weeks)
- Predicted: **2.6w** (432.7h, bucket: 1-4 weeks)
- Error: 11.1h (3% off)
- Files changed: 3

> Testing #301610
Allow zooming in/out in the image carousel just like in the normal image viewer

### Worst 3 predictions (least accurate)

**microsoft/vscode #282527** — Agent sessions: make sidebar toggle visible even in chats

- Actual: **7.4d** (178.6h, bucket: 1-4 weeks)
- Predicted: **2.7w** (453.6h, bucket: 1-4 weeks)
- Error: 11.5d (154% off)
- Files changed: 5

> When you are in a chat, we show a title:
<img width="571" height="440" alt="Image" src="https://github.com/user-attachments/assets/f415fbd4-f9f6-4264-a197-cce8bea5205f" />
In here the top right should show the sidebar toggle.
//cc @rebornix

**kubernetes/kubernetes #135929** — globalmount path may be residual while pod creation-deletion

- Actual: **8.0d** (192.8h, bucket: 1-4 weeks)
- Predicted: **2.8w** (464.9h, bucket: 1-4 weeks)
- Error: 11.3d (141% off)
- Files changed: 3

> ### What happened?
1. created a pod A
2. pod A starting `mountDevice` , but at this time, the csi-plugin pod was upgrading, kubelet received `rpc error: code = Unavailable error reading from server: EOF`, marked the volume device  `uncertain`, actually the globalmount was mounted.
https://github.com/kubernetes/kubernetes/blob/15673d04e30c711a7bb0f0efe6abf4baead1463b/pkg/volume/util/operationexecut...

**kubernetes/kubernetes #130554** — Duplicate keys in MatchLabelKeys of PodSpec should be explicitly validated

- Actual: **7.4d** (176.9h, bucket: 1-4 weeks)
- Predicted: **2.4w** (406.8h, bucket: 1-4 weeks)
- Error: 9.6d (130% off)
- Files changed: 8

> #### Summary
If `MatchLabelKeys` of `PodSpec` contains duplicate keys, the validation should fail with an explicit error.
#### Details
If `MatchLabelKeys` of `PodSpec` contains duplicate keys, validation will fail as follows.
`sample-affinity.yaml`
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sample-affinity
  labels:
    app: sample-affinity
spec:
  containers:
  - image: nginx
    name: ng...

---

## Actual bucket: **> 4 weeks** (176 samples)

*Median absolute error: 5.2w, median relative error: 84%*

### Best 3 predictions (most accurate)

**microsoft/vscode #272616** — `Ctrl+R` shows folders, workspaces, and files mixed up together

- Actual: **4.4w** (747.0h, bucket: > 4 weeks)
- Predicted: **3.9w** (652.3h, bucket: 1-4 weeks)
- Error: 3.9d (13% off)
- Files changed: 1

> <!-- ⚠️⚠️ Do Not Delete This! bug_report_template ⚠️⚠️ -->
<!-- Please read our Rules of Conduct: https://opensource.microsoft.com/codeofconduct/ -->
<!-- 🕮 Read our guide about submitting issues: https://github.com/microsoft/vscode/wiki/Submitting-Bugs-and-Suggestions -->
<!-- 🔎 Search existing issues to avoid creating duplicates. -->
<!-- 🧪 Test using the latest Insiders build to see if your iss...

**microsoft/vscode #244752** — `chat.mcp.enabled` doesn't affect API MCP server

- Actual: **7.7w** (1292.4h, bucket: > 4 weeks)
- Predicted: **5.2w** (872.3h, bucket: > 4 weeks)
- Error: 2.5w (33% off)
- Files changed: 1

> * have an extension that contributes an MCP server config
* disable `chat.mcp.enabled`
* the MCP server is still there

**kubernetes/kubernetes #9675** — What storage driver (& kernel & OS) should AWS use?

- Actual: **4.8w** (807.0h, bucket: > 4 weeks)
- Predicted: **3.0w** (503.0h, bucket: 1-4 weeks)
- Error: 12.7d (38% off)
- Files changed: 10

> I have struggled to find a filesystem/kernel for AWS that really works well.
- GCE uses wheezy with a custom kernel and aufs, but aufs seems like a dead-end: it isn't in the kernel and looks like it never will be AFAICT.  Getting GCE's kernel onto AWS would likely be work, both one-off and ongoing (?).
- overlayfs seems like the future of aufs, but is only in newer kernels
- if we're going to use...

### Worst 3 predictions (least accurate)

**facebook/react #606** — `testDoc.addEventListener("scroll", callback, true)` crashes iOS Safari

- Actual: **10.5w** (1756.4h, bucket: > 4 weeks)
- Predicted: **1.5d** (36.1h, bucket: 1-3 days)
- Error: 10.2w (98% off)
- Files changed: 2

> ``` js
document.implementation.createHTMLDocument('test doc').addEventListener("scroll", function(){}, true)
```

**microsoft/vscode #298659** — Hiding other items from on-selection widget leaves a vertical bar

- Actual: **12.0w** (2013.7h, bucket: > 4 weeks)
- Predicted: **2.6d** (63.5h, bucket: 1-3 days)
- Error: 11.6w (97% off)
- Files changed: 7

> repro: 
1. select code in editor to get the new widget
<img width="486" height="186" alt="Image" src="https://github.com/user-attachments/assets/285bf061-764e-4b8d-9566-2b202c9540ec" />
2. hide two items on the left -- :bug: vertical bar left over
<img width="432" height="184" alt="Image" src="https://github.com/user-attachments/assets/b6015a7f-0d28-42de-8ea0-8ac7eeaa1458" />
Version: 1.110.0-insi...

**microsoft/vscode #225476** — Settings sync ruined my UI state

- Actual: **8.7w** (1467.3h, bucket: > 4 weeks)
- Predicted: **2.1d** (51.6h, bucket: 1-3 days)
- Error: 8.4w (96% off)
- Files changed: 2

> * have insiders with settings sync enabled
* add exploration build to the sync
* select replace local when prompted so that exploration because just like insiders
* 🐛 over time insiders UI state gets ruined, e.g the side bar is populated with views I have carefully hidden and rearranged

---
