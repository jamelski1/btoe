# Example Predictions — Model C (model_c_combined)

Test set: 865 samples

For each actual-duration bucket, this report shows:
- **3 best predictions** (smallest relative error)
- **3 worst predictions** (largest relative error)

---

## Actual bucket: **< 1 day** (72 samples)

*Median absolute error: 2.8d, median relative error: 2149%*

### Best 3 predictions (most accurate)

**microsoft/vscode #301997** — Chat image carousel doesn't always show title

- Actual: **3.0h** (3.0h, bucket: < 1 day)
- Predicted: **9.2h** (9.2h, bucket: 1 day)
- Error: 6.1h (203% off)
- Files changed: 2

> Testing #301610
Opened the image carousel from a chat, but it doesn't always have a title in the top left. I couldn't figure out how to reproduce this though.
<img width="1392" height="1294" alt="Image" src="https://github.com/user-attachments/assets/98309d72-cdc4-4aae-a1ea-22a9373ce9be" />
<img width="1393" height="1322" alt="Image" src="https://github.com/user-attachments/assets/06d12172-e671-4e...

**microsoft/vscode #250415** — mcpr quick access as wrong title

- Actual: **7.2h** (7.2h, bucket: < 1 day)
- Predicted: **1.3d** (31.1h, bucket: 1-3 days)
- Error: 23.9h (331% off)
- Files changed: 1

> Testing #250353
* open F1 and type `?`
* the `mcpr` entry has a title saying "Add Server"
<img width="762" alt="Image" src="https://github.com/user-attachments/assets/70e263f7-02d8-4936-b4bb-190dd30c04f7" />

**microsoft/vscode #254880** — Undoing with a `Try again` action in the history doesn't make it dissapear

- Actual: **7.7h** (7.7h, bucket: < 1 day)
- Predicted: **1.4d** (33.9h, bucket: 1-3 days)
- Error: 1.1d (341% off)
- Files changed: 1

> At some point the agent failed to edit further
<img width="404" height="623" alt="Image" src="https://github.com/user-attachments/assets/0da3b2ad-2f26-48ee-aee2-0ba2ae979464" />
If I clicked Undo a few times, that error message staying in the chat:
<img width="553" height="498" alt="Image" src="https://github.com/user-attachments/assets/cb8fc15c-982c-44bb-935c-f102d8893c85" />

### Worst 3 predictions (least accurate)

**kubernetes/kubernetes #10803** — Unclean container garbage collection

- Actual: **1.9h** (1.9h, bucket: < 1 day)
- Predicted: **7.8d** (186.1h, bucket: 1-4 weeks)
- Error: 7.7d (9479% off)
- Files changed: 1

> I'm conducting PoC about distributed build using Kubernetes.
Jenkins master distribute jenkins slave pods through Kubernetes API Server.
When build is done, jenkins slave pod is also deleted by kubernetes API Server.
But, kubernetes didn't delete container. (Pod is deleted well)
After searching, I found kubelet’s containerGC option.
So, I adjusted below options to kubelet.
--minimum-container-ttl-...

**facebook/react #6797** — Move instrumentation from isomorphic to renderers/shared

- Actual: **2.8h** (2.8h, bucket: < 1 day)
- Predicted: **9.7d** (232.6h, bucket: 1-4 weeks)
- Error: 9.6d (8155% off)
- Files changed: 13

> Per @sebmarkbage, we want `isomorphic` folder to only contain the code necessary to author React components. It should not have dependencies on `ReactInstrumentation`, `ReactDebugTool`, and `devtools/*` friends, which themselves should be moved to `renderers/shared/`.
The only caller we to `ReactInstrumentation` we have right now in that folder is [`onSetState()`](https://github.com/facebook/react...

**microsoft/vscode #246095** — Leaked disposable in `KeybindingsEditor.createHeader`

- Actual: **1.3h** (1.3h, bucket: < 1 day)
- Predicted: **4.3d** (103.3h, bucket: 3-7 days)
- Error: 4.2d (7816% off)
- Files changed: 1

> ```
[71755:0409/135558.118655:INFO:CONSOLE(23)] "[LEAKED DISPOSABLE] Error: CREATED via:
    at GCBasedDisposableTracker.trackDisposable (vscode-file://vscode-app/Users/bpasero/Development/Microsoft/vscode/out/vs/base/common/lifecycle.js:27:23)
    at trackDisposable (vscode-file://vscode-app/Users/bpasero/Development/Microsoft/vscode/out/vs/base/common/lifecycle.js:198:24)
    at new Disposable (...

---

## Actual bucket: **1 day** (91 samples)

*Median absolute error: 3.4d, median relative error: 559%*

### Best 3 predictions (most accurate)

**microsoft/vscode #247672** — Chat: Add consistent icon order across modes

- Actual: **18.2h** (18.2h, bucket: 1 day)
- Predicted: **20.0h** (20.0h, bucket: 1 day)
- Error: 1.8h (10% off)
- Files changed: 1

> <!-- ⚠️⚠️ Do Not Delete This! feature_request_template ⚠️⚠️ -->
<!-- Please read our Rules of Conduct: https://opensource.microsoft.com/codeofconduct/ -->
<!-- Please search existing issues to avoid creating duplicates. -->
While testing https://github.com/microsoft/vscode/issues/247399, I noticed that there's an inconsistent order of icons when switching between modes.
Namely, the voice chat icon...

**microsoft/vscode #250424** — Commands in warning hover are heavily truncated

- Actual: **23.4h** (23.4h, bucket: 1 day)
- Predicted: **1.3d** (30.1h, bucket: 1-3 days)
- Error: 6.7h (29% off)
- Files changed: 1

> Testing #249660
<img width="537" alt="Image" src="https://github.com/user-attachments/assets/606ee26f-31bf-4980-9e5f-0ce593ba0ef5" />

**microsoft/vscode #260160** — Terminal suggest: git cherry-pick flags aren't supported

- Actual: **12.8h** (12.8h, bucket: 1 day)
- Predicted: **1.0d** (24.0h, bucket: 1-3 days)
- Error: 11.3h (88% off)
- Files changed: 5

> <img width="798" height="84" alt="Image" src="https://github.com/user-attachments/assets/8a67a59b-3600-4e3a-a652-323c6e22e38b" />

### Worst 3 predictions (least accurate)

**microsoft/vscode #259872** — Investigate issues with `subst` workaround

- Actual: **13.4h** (13.4h, bucket: 1 day)
- Predicted: **3.6w** (607.1h, bucket: 1-4 weeks)
- Error: 3.5w (4423% off)
- Files changed: 2

> If you start VS Code from subst drive, then VS Code will show wrong content for root of that drive:
<img width="1366" height="720" alt="image" src="https://github.com/user-attachments/assets/6715a25d-dfb5-47c2-9bbb-d87df5bd55c5" />
<img width="1366" height="720" alt="image" src="https://github.com/user-attachments/assets/226a0b9b-a897-493d-9059-614c43a3c253" />
As you can see, instead of showing c...

**microsoft/vscode #264515** — Double click in empty Chat Sessions list should add new session

- Actual: **10.2h** (10.2h, bucket: 1 day)
- Predicted: **13.7d** (328.6h, bucket: 1-4 weeks)
- Error: 13.3d (3110% off)
- Files changed: 2

> Double click in empty Explorer area creates a new empty file (same effect as +)
Same pattern should be followed for all views in the Chat Sessions view container. E.g. clicking on an empty space in Claude Code should just create a new claude code session.
fyi @jo-oikawa @roblourens

**kubernetes/kubernetes #130719** — Replace all deprecated sets.String with sets.Set from directories managed by in sig/node

- Actual: **8.5h** (8.5h, bucket: 1 day)
- Predicted: **11.0d** (264.5h, bucket: 1-4 weeks)
- Error: 10.7d (2996% off)
- Files changed: 2

> In this PR https://github.com/kubernetes/kubernetes/pull/112377, sets.Set is newly implemented, and sets.String got marked as deprecated.
In the files managed by sig/node, there are some `sets.String`. This issue aimas to replace all sets.String with sets.Set in the sig/node area.
ref: https://github.com/kubernetes/kubernetes/issues/113709
/kind cleanup
/sig node
- [x] pkg/controller/nodelifecycle...

---

## Actual bucket: **1-3 days** (150 samples)

*Median absolute error: 2.8d, median relative error: 168%*

### Best 3 predictions (most accurate)

**facebook/react #5054** — Incorrect react-dom package on bower?

- Actual: **1.4d** (34.7h, bucket: 1-3 days)
- Predicted: **1.5d** (34.8h, bucket: 1-3 days)
- Error: 5 min (0% off)
- Files changed: 3

> I tried doing the following to pick up react-dom: `bower install react-dom#0.14.0-rc1 --save`
However, it said that the only version available was `0.1.0`
Poking around on Github yielded a repo called [react-dom](https://github.com/EtienneLem/react-dom) that appears to be linked to Bower. I'm guessing this isn't the right library; what's the dependency installation story going to look like with Bo...

**kubernetes/kubernetes #137074** — Update HPA e2e DynamicResourceConsumer to use current APIs

- Actual: **2.7d** (64.4h, bucket: 1-3 days)
- Predicted: **2.7d** (65.3h, bucket: 1-3 days)
- Error: 50 min (1% off)
- Files changed: 3

> In the HPA e2e tests, the NewDynamicResourceConsumer utility function is responsible for creating several Kubernetes objects. However, these objects are currently created using deprecated/legacy API versions:
https://github.com/kubernetes/kubernetes/blob/2fb84cfed3e0da83eec85dcc97d14db9b06915c9/test/e2e/framework/autoscaling/autoscaling_utils.go#L90-L98
We should update this implementation to use...

**microsoft/vscode #245718** — array string replacements as source no longer works in launch.json

- Actual: **2.9d** (69.6h, bucket: 1-3 days)
- Predicted: **3.0d** (71.8h, bucket: 1-3 days)
- Error: 2.2h (3% off)
- Files changed: 2

> Type: <b>Bug</b>
In settings json, declare an array setting
```json
{
    "buildPaths": [
        "C:\\pathone",
        "C:\\pathtwo",
        "C:\\paththree"
    ]
}
```
Then in launch.json, declare 
```json
        "options": {
                "env": {
                    "BUILD_EXE": "${config:buildPaths}"
                }
            }
```
Instead of an array of paths being set to BUILD_EXE,...

### Worst 3 predictions (least accurate)

**microsoft/vscode #297689** — 'Open Chat Customizations' button is too much

- Actual: **1.4d** (32.5h, bucket: 1-3 days)
- Predicted: **3.2w** (542.8h, bucket: 1-4 weeks)
- Error: 3.0w (1573% off)
- Files changed: 13

> Whenever instructions/skill/agent file open in an editor, the button 'Open Chat Customizations` shows up.
<img width="931" height="539" alt="Image" src="https://github.com/user-attachments/assets/e7f5dcd5-595c-43b8-bc9d-b9a4656925fb" />
I think its too much and should be removed
- It's not an action that I would typically invoke when editing in a prompt file
- It looks lost

**kubernetes/kubernetes #136347** — Post merge PR is failing: post-kubernetes-push-e2e-node-perf-tf-wide-deep-test-images

- Actual: **1.4d** (34.2h, bucket: 1-3 days)
- Predicted: **2.6w** (429.4h, bucket: 1-4 weeks)
- Error: 2.4w (1155% off)
- Files changed: 2

> Hoisting comment from @mkumatag in https://github.com/kubernetes/kubernetes/pull/134822#issuecomment-3449397895
the CI job is *STILL* failing https://storage.googleapis.com/kubernetes-ci-logs/logs/post-kubernetes-push-e2e-node-perf-tf-wide-deep-test-images/2011957382287986688/build-log.txt (cc @humblec - context - https://github.com/kubernetes/kubernetes/pull/134822)
Post merge PR is failing:
```...

**kubernetes/kubernetes #134167** — MAP duplicate env parse error

- Actual: **1.1d** (26.6h, bucket: 1-3 days)
- Predicted: **13.6d** (325.7h, bucket: 1-4 weeks)
- Error: 12.5d (1124% off)
- Files changed: 2

> ### What happened?
The following pod gets rejected by MAP in kubernetes 1.33
```
apiVersion: v1
kind: Pod
metadata:
  name: hello-world
spec:
  containers:
  - name: hello-world-container
    image: nginx:latest
    ports:
    - containerPort: 80
    env:
    - name: test
      value: a
    - name: test
      value: b
```
The pods "hello-world" is invalid: : policy 'seccomp-profile-default' with b...

---

## Actual bucket: **3-7 days** (137 samples)

*Median absolute error: 2.7d, median relative error: 52%*

### Best 3 predictions (most accurate)

**microsoft/vscode #286098** — Agent sessions - back button in the title feedback

- Actual: **6.2d** (149.9h, bucket: 3-7 days)
- Predicted: **6.3d** (151.3h, bucket: 3-7 days)
- Error: 1.4h (1% off)
- Files changed: 3

> Testing #285958
Back button makes sense when the session is opened in the panel:
<img width="428" height="179" alt="Image" src="https://github.com/user-attachments/assets/d20ab27b-d7a1-4f66-bc2d-8e8b113585f7" />
When a session is opened to the side, it just clears the side area so it does not make much sense there:
<img width="684" height="171" alt="Image" src="https://github.com/user-attachments/...

**kubernetes/kubernetes #136628** — Let DRA drivers specify the order in which devices are considered during scheduling

- Actual: **4.6d** (109.6h, bucket: 3-7 days)
- Predicted: **4.6d** (110.7h, bucket: 3-7 days)
- Error: 1.1h (1% off)
- Files changed: 10

> ### What would you like to be added?
Currently the order in which the DRA allocator considers devices during scheduling is non-deterministic. Since the DRA allocator uses a first-fit algorithm, the order in which devices are considered can impact both the time required to schedule pods and which devices are selected.
We want to let DRA drivers specify the order in which the allocator will consider...

**microsoft/vscode #254893** — Terminal Persistence detach/attach should support basic reconnection

- Actual: **4.2d** (100.7h, bucket: 3-7 days)
- Predicted: **4.3d** (102.1h, bucket: 3-7 days)
- Error: 1.4h (1% off)
- Files changed: 1

> https://dev.azure.com/monacotools/Monaco/_build/results?buildId=348219&view=logs&j=45e2b0b5-0069-506f-d663-629b6db3a5d5&t=7cde2c7d-5236-5b41-5514-673b49f2139d&l=178
```
1) VSCode Smoke Tests (Electron)
       Terminal
         Terminal Persistence
           detach/attach
             should support basic reconnection:
     Error: Timeout: get elements '.tabs-list .monaco-list-row' after 20 second...

### Worst 3 predictions (least accurate)

**kubernetes/kubernetes #135621** — DATA RACE garbage collector: blockingDependents

- Actual: **5.9d** (142.0h, bucket: 3-7 days)
- Predicted: **5.4w** (910.3h, bucket: > 4 weeks)
- Error: 4.6w (541% off)
- Files changed: 7

> ### What happened?
kube-controller-manager compiled with -race and tested with various E2E tests in a kind cluster [led to](https://prow.k8s.io/view/gs/kubernetes-ci-logs/pr-logs/pull/133844/pull-kubernetes-e2e-kind-alpha-beta-features-race/1996896534980988928):

#### kube-system/kube-controller-manager-kind-control-plane/kube-controller-manager
  
      Read at 0x00c004c37cf8 by goroutine 2258:...

**microsoft/vscode #302993** — Sessions: The session filter displays two `Local` session types

- Actual: **3.1d** (74.0h, bucket: 3-7 days)
- Predicted: **2.1w** (353.8h, bucket: 1-4 weeks)
- Error: 11.7d (378% off)
- Files changed: 1

> If you click the filter icon in the sessions list, you'll see two `Local` options. The top one appears to be the `Local` sessions in VS Code, and the second one appears to be "Copilot CLI". That said, we should probably hide the former and rename the later? That way we have three options: Copilot CLI, Claude, and Cloud? That would match the terminology and VS Code and be more direct with what thes...

**microsoft/vscode #244570** — `observableInternal`: Cannot read properties of null (reading 'push')

- Actual: **3.9d** (94.1h, bucket: 3-7 days)
- Predicted: **2.3w** (379.8h, bucket: 1-4 weeks)
- Error: 11.9d (304% off)
- Files changed: 1

> Cannot read properties of null (reading 'push'): TypeError: Cannot read properties of null (reading 'push')
at [vs/base/common/observableInternal/base.ts:407:27](https://github.com/microsoft/vscode/blob/b47e1fee9e4034b5a569d54f7765e4133bd3f7ed/src/vs/base/common/observableInternal/base.ts#L407)
at [vs/base/common/observableInternal/base.ts:489:7](https://github.com/microsoft/vscode/blob/b47e1fee9e...

---

## Actual bucket: **1-4 weeks** (239 samples)

*Median absolute error: 9.4d, median relative error: 61%*

### Best 3 predictions (most accurate)

**facebook/react #2880** — Cannot load example

- Actual: **7.7d** (185.9h, bucket: 1-4 weeks)
- Predicted: **7.8d** (186.3h, bucket: 1-4 weeks)
- Error: 26 min (0% off)
- Files changed: 1

> When I run the index.html in examples jquery-mobile in the chromium browser, I get:
 Uncaught TypeError: Cannot read property '__reactAutoBindMap' of undefinedreact.js:5776 Constructorapp.js:182 (anonymous function)

**kubernetes/kubernetes #135145** — ValidatingAdmissionPolicies that use a CRD with a property of type=object and additionalProperties=true in matchConstraints crash kube-controller-manager

- Actual: **14.0d** (334.9h, bucket: 1-4 weeks)
- Predicted: **14.0d** (335.7h, bucket: 1-4 weeks)
- Error: 49 min (0% off)
- Files changed: 3

> ### What happened?
A CRD that includes an object property defined as `type: object` and `additionalProperties: true` is used in a `ValidatingAdmissionPolicy` in the `matchConstraints` field.
As soon as the `ValidatingAdmissionPolicy` is created, the `validatingadmissionpolicystatus` controller in `kube-controller-manager` does type-checking on the resource specified in the `matchConstraints` field...

**kubernetes/kubernetes #24089** — kubectl validation fails when creating a non-v1 object in a v1 list

- Actual: **8.9d** (213.4h, bucket: 1-4 weeks)
- Predicted: **9.3d** (222.1h, bucket: 1-4 weeks)
- Error: 8.8h (4% off)
- Files changed: 7

> In other words, you can't create/replace/delete/apply deployments with kubectl if they're in a list.
Works as expected:
``` console
$ cat nginx-rc.yaml
apiVersion: v1
kind: List
items:
  - apiVersion: v1
    kind: ReplicationController
    metadata:
      name: nginx
    spec:
      replicas: 1
      template:
        metadata:
          labels:
            name: nginx
        spec:
          cont...

### Worst 3 predictions (least accurate)

**kubernetes/kubernetes #135929** — globalmount path may be residual while pod creation-deletion

- Actual: **8.0d** (192.8h, bucket: 1-4 weeks)
- Predicted: **4.0w** (671.3h, bucket: 1-4 weeks)
- Error: 2.8w (248% off)
- Files changed: 3

> ### What happened?
1. created a pod A
2. pod A starting `mountDevice` , but at this time, the csi-plugin pod was upgrading, kubelet received `rpc error: code = Unavailable error reading from server: EOF`, marked the volume device  `uncertain`, actually the globalmount was mounted.
https://github.com/kubernetes/kubernetes/blob/15673d04e30c711a7bb0f0efe6abf4baead1463b/pkg/volume/util/operationexecut...

**microsoft/vscode #282527** — Agent sessions: make sidebar toggle visible even in chats

- Actual: **7.4d** (178.6h, bucket: 1-4 weeks)
- Predicted: **3.7w** (615.3h, bucket: 1-4 weeks)
- Error: 2.6w (244% off)
- Files changed: 5

> When you are in a chat, we show a title:
<img width="571" height="440" alt="Image" src="https://github.com/user-attachments/assets/f415fbd4-f9f6-4264-a197-cce8bea5205f" />
In here the top right should show the sidebar toggle.
//cc @rebornix

**microsoft/vscode #278199** — Issue running subagent tool

- Actual: **9.8d** (235.4h, bucket: 1-4 weeks)
- Predicted: **3.8w** (635.7h, bucket: 1-4 weeks)
- Error: 2.4w (170% off)
- Files changed: 1

> - Copilot Chat Extension Version: 0.33.1
- VS Code Version: 1.106.1
- OS Version: Windows 11 / WSL Ubuntu
- Feature (e.g. agent/edit/ask mode): agent
- Selected model (e.g. GPT 4.1, Claude 3.7 Sonnet): Claude Sonnet 4.5
- Logs: -
The #runSubagent tool randomly stops working in VS Code Chat. I understand that it is an experimental feature and that it is subject to errors, but I am passing on what i...

---

## Actual bucket: **> 4 weeks** (176 samples)

*Median absolute error: 5.2w, median relative error: 85%*

### Best 3 predictions (most accurate)

**microsoft/vscode #244752** — `chat.mcp.enabled` doesn't affect API MCP server

- Actual: **7.7w** (1292.4h, bucket: > 4 weeks)
- Predicted: **7.8w** (1315.8h, bucket: > 4 weeks)
- Error: 23.3h (2% off)
- Files changed: 1

> * have an extension that contributes an MCP server config
* disable `chat.mcp.enabled`
* the MCP server is still there

**kubernetes/kubernetes #135963** — [Flake] test/integration/servicecidr: TestServiceAllocation fails with "range is full"

- Actual: **5.0w** (836.5h, bucket: > 4 weeks)
- Predicted: **4.8w** (805.2h, bucket: > 4 weeks)
- Error: 1.3d (4% off)
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

**kubernetes/kubernetes #9675** — What storage driver (& kernel & OS) should AWS use?

- Actual: **4.8w** (807.0h, bucket: > 4 weeks)
- Predicted: **4.3w** (725.0h, bucket: > 4 weeks)
- Error: 3.4d (10% off)
- Files changed: 10

> I have struggled to find a filesystem/kernel for AWS that really works well.
- GCE uses wheezy with a custom kernel and aufs, but aufs seems like a dead-end: it isn't in the kernel and looks like it never will be AFAICT.  Getting GCE's kernel onto AWS would likely be work, both one-off and ongoing (?).
- overlayfs seems like the future of aufs, but is only in newer kernels
- if we're going to use...

### Worst 3 predictions (least accurate)

**kubernetes/kubernetes #137269** — Investigate cleaning up cross-group publishing of Options types in openapi v3

- Actual: **5.2w** (865.4h, bucket: > 4 weeks)
- Predicted: **14.5h** (14.5h, bucket: 1 day)
- Error: 5.1w (98% off)
- Files changed: 36

> While reviewing https://github.com/kubernetes/kubernetes/pull/137028/files, I noticed that any addition of any group/version results in changes to the openapi v3 published for all other group versions.
This happens because we cross-register generic metav1 types like DeleteOptions and WatchEvent into all API group/versions, and then publish all registered group/versions for those types into openapi...

**microsoft/vscode #298659** — Hiding other items from on-selection widget leaves a vertical bar

- Actual: **12.0w** (2013.7h, bucket: > 4 weeks)
- Predicted: **1.4d** (34.1h, bucket: 1-3 days)
- Error: 11.8w (98% off)
- Files changed: 7

> repro: 
1. select code in editor to get the new widget
<img width="486" height="186" alt="Image" src="https://github.com/user-attachments/assets/285bf061-764e-4b8d-9566-2b202c9540ec" />
2. hide two items on the left -- :bug: vertical bar left over
<img width="432" height="184" alt="Image" src="https://github.com/user-attachments/assets/b6015a7f-0d28-42de-8ea0-8ac7eeaa1458" />
Version: 1.110.0-insi...

**microsoft/vscode #281643** — Agent sessions: special rendering of PRs and worktrees

- Actual: **12.4w** (2075.1h, bucket: > 4 weeks)
- Predicted: **1.7d** (41.5h, bucket: 1-3 days)
- Error: 12.1w (98% off)
- Files changed: 6

> <!-- ⚠️⚠️ Do Not Delete This! feature_request_template ⚠️⚠️ -->
<!-- Please read our Rules of Conduct: https://opensource.microsoft.com/codeofconduct/ -->
<!-- Please search existing issues to avoid creating duplicates. -->
<!-- Describe the feature you'd like. -->
Ref https://github.com/microsoft/vscode-internalbacklog/issues/6388
I thought PR links were previously clickable - is that no longer t...

---
