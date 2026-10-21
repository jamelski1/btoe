# Example Predictions — Model C (model_c_combined)

Test set: 865 samples

For each actual-duration bucket, this report shows:
- **3 best predictions** (smallest relative error)
- **3 worst predictions** (largest relative error)

---

## Actual bucket: **< 1 day** (72 samples)

*Median absolute error: 2.8d, median relative error: 2149%*

### Best 3 predictions (most accurate)

**microsoft/vscode #245136** — An aria alert should indicate which chat model has been toggled to

- Actual: **3.0h** (3.0h, bucket: < 1 day)
- Predicted: **9.2h** (9.2h, bucket: 1 day)
- Error: 6.1h (203% off)
- Files changed: 1

> 1. Using a screen reader, use `ctrlCmd+alt+.` in the chat input to toggle between chat models
2. 🐛 there's no announcement indicating which mode has been entered

**microsoft/vscode #250415** — mcpr quick access as wrong title

- Actual: **7.2h** (7.2h, bucket: < 1 day)
- Predicted: **1.3d** (31.1h, bucket: 1-3 days)
- Error: 23.9h (331% off)
- Files changed: 1

> Testing #250353
* open F1 and type `?`
* the `mcpr` entry has a title saying "Add Server"
<img width="762" alt="Image" src="https://github.com/user-attachments/assets/70e263f7-02d8-4936-b4bb-190dd30c04f7" />

**microsoft/vscode #249492** — VS Code Speech shows modal dialog after cancelling

- Actual: **7.7h** (7.7h, bucket: < 1 day)
- Predicted: **1.4d** (33.9h, bucket: 1-3 days)
- Error: 1.1d (341% off)
- Files changed: 1

> 1. Without speech installed, click the microphone button in the chat input
2. Hit esc on the modal dialog to install the speech extension
3. :bug: another modal appears:
<img width="305" alt="Image" src="https://github.com/user-attachments/assets/3bf2c22c-487f-4f13-89b3-01246495d808" />

### Worst 3 predictions (least accurate)

**facebook/react #28924** — Changelog for 18.3 is missing

- Actual: **1.9h** (1.9h, bucket: < 1 day)
- Predicted: **7.8d** (186.1h, bucket: 1-4 weeks)
- Error: 7.7d (9479% off)
- Files changed: 1

> <!--
  Please provide a clear and concise description of what the bug is. Include
  screenshots if needed. Please test using the latest version of the relevant
  React packages to make sure your issue has not already been fixed.
-->
React version: 18.3
## Steps To Reproduce
1. Check the Releases section on this repo, the `CHANGELOG.md` file, or click on "Release notes" at the end of the second not...

**facebook/react #1120** — warning code shows up in min build

- Actual: **2.8h** (2.8h, bucket: < 1 day)
- Predicted: **9.7d** (232.6h, bucket: 1-4 weeks)
- Error: 9.6d (8155% off)
- Files changed: 4

> See http://fb.me/react-0.9.0-rc1.min.js and search for `"Invalid`. We should either (a) change warning's implementation to warn only in `__DEV__` and strip it in the build step or (b) change the callers to check `__DEV__`.
@cpojer?

**microsoft/vscode #239939** — Terminal: Split action is missing

- Actual: **1.3h** (1.3h, bucket: < 1 day)
- Predicted: **4.3d** (103.3h, bucket: 3-7 days)
- Error: 4.2d (7816% off)
- Files changed: 1

> I no longer see the split terminal icon :thinking_face: even though right clicking the actions tells me it should be visible
![Image](https://github.com/user-attachments/assets/13727b7b-c45f-4fb3-b224-38826ab6f45f)
![Image](https://github.com/user-attachments/assets/b789d121-ba52-499e-9d07-9ec6699bc08e)

---

## Actual bucket: **1 day** (91 samples)

*Median absolute error: 3.4d, median relative error: 559%*

### Best 3 predictions (most accurate)

**microsoft/vscode #242583** — Treesitter makes window stop responding when chat emits codeblocks

- Actual: **18.2h** (18.2h, bucket: 1 day)
- Predicted: **20.0h** (20.0h, bucket: 1 day)
- Error: 1.8h (10% off)
- Files changed: 3

> - Enable `editor.experimental.preferTreeSitter.typescript`
- Ask Copilot Chat "give a typescript example"
- Window stops responding for a bit

**microsoft/vscode #239481** — Comment is getting added randomly when pressing enter on a line where a URI is defined

- Actual: **23.4h** (23.4h, bucket: 1 day)
- Predicted: **1.3d** (30.1h, bucket: 1-3 days)
- Error: 6.7h (29% off)
- Files changed: 2

> ![Image](https://github.com/user-attachments/assets/a3bc4dbc-ef97-414e-89f8-3a7775abd33e)
Repro line:
```ts
			validResources = [
				URI.parse('file:///c:/test'),
				URI.parse('file:///test')];
```
Apparently onEnter rules are a simple regex and the `//` in `file:///` is throwing it off.

**kubernetes/kubernetes #137393** — [Flaky test][sig-apps]ReplicaSet Replicaset should have a working scale subresource [Conformance]

- Actual: **12.8h** (12.8h, bucket: 1 day)
- Predicted: **1.0d** (24.0h, bucket: 1-3 days)
- Error: 11.3h (88% off)
- Files changed: 1

> ### Which jobs are flaking?
* sig-release-master-informing
* kind-master-beta-enabled-conformance
### Which tests are flaking?
* [Kubernetes e2e suite.[It] [sig-apps] ReplicaSet Replicaset should have a working scale subresource [Conformance]](https://prow.k8s.io/view/gs/kubernetes-ci-logs/logs/ci-kubernetes-e2e-kind-beta-enabled-conformance/2029013345452953600)
### Since when has it been flaking?...

### Worst 3 predictions (least accurate)

**kubernetes/kubernetes #135145** — ValidatingAdmissionPolicies that use a CRD with a property of type=object and additionalProperties=true in matchConstraints crash kube-controller-manager

- Actual: **13.4h** (13.4h, bucket: 1 day)
- Predicted: **3.6w** (607.1h, bucket: 1-4 weeks)
- Error: 3.5w (4423% off)
- Files changed: 3

> ### What happened?
A CRD that includes an object property defined as `type: object` and `additionalProperties: true` is used in a `ValidatingAdmissionPolicy` in the `matchConstraints` field.
As soon as the `ValidatingAdmissionPolicy` is created, the `validatingadmissionpolicystatus` controller in `kube-controller-manager` does type-checking on the resource specified in the `matchConstraints` field...

**rust-lang/rust #152331** — [ICE]: `arg len already exists`

- Actual: **10.2h** (10.2h, bucket: 1 day)
- Predicted: **13.7d** (328.6h, bucket: 1-4 weeks)
- Error: 13.3d (3110% off)
- Files changed: 3

> <!--
[31mICE[0m: Rustc ./a.rs '' 'thread 'rustc' ($TID) panicked at compiler/rustc_errors/src/diagnostic.rs:359:9: 'arg len already exists'', 'thread 'rustc' ($TID) panicked at compiler/rustc_errors/src/diagnostic.rs:359:9: 'arg len already exists''
File: /tmp/im/2/a.rs
-->
auto-reduced (treereduce-rust):
````rust
fn main() {
    h2(|_: (), _: (), _: (), x: &_| {});
}
fn h2<F>(_: F)
where
    F:...

**microsoft/vscode #252907** — User mcp.json should follow standard mcp.json schema

- Actual: **8.5h** (8.5h, bucket: 1 day)
- Predicted: **11.0d** (264.5h, bucket: 1-4 weeks)
- Error: 10.7d (2996% off)
- Files changed: 9

> Currently servers in User MCP.json are in the form
```
{
	"servers": {
		"github": {
			"id": "github",
			"name": "github",
			"version": "0.0.1",
			"config": {
				"command": "docker",
				"args": [
					"run",
					"-i",
					"--rm",
					"-e",
					"GITHUB_PERSONAL_ACCESS_TOKEN",
					"ghcr.io/github/github-mcp-server"
				],
				"env": {
					"GITHUB_PERSONAL_ACCESS_TOKEN": "${input:github_t...

---

## Actual bucket: **1-3 days** (150 samples)

*Median absolute error: 2.8d, median relative error: 168%*

### Best 3 predictions (most accurate)

**microsoft/vscode #291089** — In agent session window, layout falls over when opening editors

- Actual: **1.4d** (34.7h, bucket: 1-3 days)
- Predicted: **1.5d** (34.8h, bucket: 1-3 days)
- Error: 5 min (0% off)
- Files changed: 2

> Testing #290241
1. Open agent session window
2. Run "Help: Welcome" command or "Show settings editor"
🐛 => this just pops my terminal (which is aligned to Justify)

**microsoft/vscode #291154** — Tools disabled by when clause show up in picker

- Actual: **2.7d** (64.4h, bucket: 1-3 days)
- Predicted: **2.7d** (65.3h, bucket: 1-3 days)
- Error: 50 min (1% off)
- Files changed: 4

> The search subagent should be hidden in VS Code when its setting is disabled, not just disabled in the agent's list at runtime. Do this by using a  `when` clause on the tool contribution in package.json
cc @24anisha can you take care of this?

**microsoft/TypeScript #51875** — Unexpected excess property error with intersection of index signatures

- Actual: **2.9d** (69.6h, bucket: 1-3 days)
- Predicted: **3.0d** (71.8h, bucket: 1-3 days)
- Error: 2.2h (3% off)
- Files changed: 6

> # Bug Report
### 🔎 Search Terms
index signature, intersection, excess property checking
### 🕗 Version & Regression Information
- This changed between versions 4.8.0-dev.20220613 and 4.8.0-dev.20220614
### ⏯ Playground Link
[Playground link with relevant code](https://www.typescriptlang.org/play?target=9#code/DYUwLgBAHgXBDeEDaBrOBnMAnAlgOwHMBdORAQzgAYIBfWiAMgWTQk10JOYCMr6aA3ACghUCAF5mAT1IQKESgBoIvB...

### Worst 3 predictions (least accurate)

**kubernetes/kubernetes #128442** — Allow ConcurrentDaemonSetSyncs to be set for kube-controller-manager

- Actual: **1.4d** (32.5h, bucket: 1-3 days)
- Predicted: **3.2w** (542.8h, bucket: 1-4 weeks)
- Error: 3.0w (1573% off)
- Files changed: 2

> ### What would you like to be added?
A possibility to configure the number of worker threads used in the DaemonSet controller at runtime. A relevant configuration option exists in the code but it is not exposed as a CLI flag right now.
### Why is this needed?
Currently, DaemonSet controller has 2 worker threads and this number is a [hardcoded value](https://github.com/kubernetes/kubernetes/blob/da...

**rust-lang/rust #151024** — ICE `const array must have an array type`

- Actual: **1.4d** (34.2h, bucket: 1-3 days)
- Predicted: **2.6w** (429.4h, bucket: 1-4 weeks)
- Error: 2.4w (1155% off)
- Files changed: 3

> <!--
[31mICE[0m: Rustc ./9C580B1C4A0AB31A282DB97B037889E522D67BEC8F0FE359106BF2A788D485B5.rs '' 'error: internal compiler error: const array must have an array type', 'error: internal compiler error: const array must have an array type'
File: /tmp/im/9C580B1C4A0AB31A282DB97B037889E522D67BEC8F0FE359106BF2A788D485B5.rs
-->
auto-reduced (treereduce-rust):
````rust
#![feature(min_generic_const_args)...

**kubernetes/kubernetes #131512** — spec.jobTemplate.spec.podFailurePolicy.rules[0].onPodConditions[0].status: Required value: valid values: ["False" "True" "Unknown"]

- Actual: **1.1d** (26.6h, bucket: 1-3 days)
- Predicted: **13.6d** (325.7h, bucket: 1-4 weeks)
- Error: 12.5d (1124% off)
- Files changed: 3

> ### What happened?
When I try to apply (patching) an existing `CronJob` with the following `podFailurePolicy`:
```
      podFailurePolicy:
        rules:
        - action: Ignore
          onPodConditions:
          - type: DisruptionTarget
```
I'm getting the following Error:
```
error when patching "/dev/shm/2794561279": CronJob.batch "mycronjob" is invalid: spec.jobTemplate.spec.podFailurePolic...

---

## Actual bucket: **3-7 days** (137 samples)

*Median absolute error: 2.7d, median relative error: 52%*

### Best 3 predictions (most accurate)

**kubernetes/kubernetes #134299** — [Flaking Test] UT k8s.io/kubernetes/pkg/controller: podautoscaler

- Actual: **6.2d** (149.9h, bucket: 3-7 days)
- Predicted: **6.3d** (151.3h, bucket: 3-7 days)
- Error: 1.4h (1% off)
- Files changed: 6

> ### Which jobs are flaking?
https://prow.k8s.io/view/gs/kubernetes-ci-logs/logs/ci-kubernetes-unit/1970799070624616448
https://prow.k8s.io/view/gs/kubernetes-ci-logs/logs/ci-kubernetes-unit/1970966677315129344
https://prow.k8s.io/view/gs/kubernetes-ci-logs/logs/ci-kubernetes-unit/1971179330184679424
https://prow.k8s.io/view/gs/kubernetes-ci-logs/logs/ci-kubernetes-unit/1971254828386488320
https://...

**rust-lang/rust #148144** — "Struct is never constructed" false positive (dead_code)

- Actual: **4.6d** (109.6h, bucket: 3-7 days)
- Predicted: **4.6d** (110.7h, bucket: 3-7 days)
- Error: 1.1h (1% off)
- Files changed: 2

> ### Code
```Shell
git clone https://salsa.debian.org/dgit-team/tag2upload-service-manager.git -b 2025-10-26-unused-false-positive
# commitid a52ede5c5ed44708c53e509ba26cfa8cd1c5eaee
cd tag2upload-service-manager/
env -u http_proxy cargo +stable test --locked --all-features --all-targets --workspace -- t_comprehensive
# Note, there will be a *great deal* of output; you'll maybe want:
env -u http_pr...

**microsoft/vscode #308745** — NES: Replace chatResponseFailure polling with stream-level error propagation in XtabProvider

- Actual: **4.2d** (100.7h, bucket: 3-7 days)
- Predicted: **4.3d** (102.1h, bucket: 3-7 days)
- Error: 1.4h (1% off)
- Files changed: 7

> ## Problem
\`chatResponseFailure\` is a mutable \`let\` variable set asynchronously via \`fetchResultPromise.then()\` and read via a \`getFetchFailure()\` closure scattered across multiple \`await\`/\`yield\` points in \`_streamEditsImpl\`. Every new async suspension point requires the developer to remember to add a \`getFetchFailure()\` check — this polling pattern is fragile and error-prone.
Cur...

### Worst 3 predictions (least accurate)

**microsoft/TypeScript #60985** — `lib.d.ts` Updates for TypeScript 5.8

- Actual: **5.9d** (142.0h, bucket: 3-7 days)
- Predicted: **5.4w** (910.3h, bucket: > 4 weeks)
- Error: 4.6w (541% off)
- Files changed: 9

> Including
* https://github.com/microsoft/TSJS-lib-generator/
* Outstanding `lib.d.ts` PRs to TS

**microsoft/TypeScript #49001** — Missing properties quickfix does not add missing imports

- Actual: **3.1d** (74.0h, bucket: 3-7 days)
- Predicted: **2.1w** (353.8h, bucket: 1-4 weeks)
- Error: 11.7d (378% off)
- Files changed: 2

> # Bug Report
<!--
  Please fill in each section completely. Thank you!
-->
### 🔎 Search Terms
quickfix missing properties imports
### 🕗 Version & Regression Information
The quickfix was added in https://github.com/microsoft/TypeScript/pull/44576 (cc @a-tarasyuk @komyg) but it doesn't appear to add missing imports.
### 💻 Code
<!-- Please post the relevant code sample here as well-->
```ts
// foo.ts...

**rust-lang/rust #142948** — `{UnsafeCell,Cell}::from_mut` on `&mut [T; 0]` then unsize-coerced in consteval reports UB in safe code

- Actual: **3.9d** (94.1h, bucket: 3-7 days)
- Predicted: **2.3w** (379.8h, bucket: 1-4 weeks)
- Error: 11.9d (304% off)
- Files changed: 321

> This code makes the compiler report undefined behavior in safe code during consteval.
```rust
use std::cell::UnsafeCell;
const X: &mut UnsafeCell<[i32]> = UnsafeCell::from_mut(&mut []);
```
```
error[E0080]: constructing invalid value at .<deref>: encountered `UnsafeCell` in read-only memory
 --> src/lib.rs:2:1
  |
2 | const X: &mut UnsafeCell<[i32]> = UnsafeCell::from_mut(&mut []);
  | ^^^^^^^^^^...

---

## Actual bucket: **1-4 weeks** (239 samples)

*Median absolute error: 9.4d, median relative error: 61%*

### Best 3 predictions (most accurate)

**rust-lang/rust #146163** — Miscomputation error on nightly starting with 2025-08-11

- Actual: **7.7d** (185.9h, bucket: 1-4 weeks)
- Predicted: **7.8d** (186.3h, bucket: 1-4 weeks)
- Error: 26 min (0% off)
- Files changed: 1

> This is a miscomputation error inside an implementation of a cryptographic algorithm (I am on an `aarch64-apple-darwin` and have not checked other targets) .
https://github.com/RustCrypto/password-hashes/tree/master/yescrypt
The source code in question, the `yescrypt` crate, has been mechanically translated from C (using corrode), contains ample usage of `unsafe` and is not idiomatic Rust (somethi...

**rust-lang/rust #149412** — Ambiguous glob import of `main` errors even in library crate

- Actual: **14.0d** (334.9h, bucket: 1-4 weeks)
- Predicted: **14.0d** (335.7h, bucket: 1-4 weeks)
- Error: 49 min (0% off)
- Files changed: 115

> I compiled the following code with `rustc --crate-type=lib repro.rs`
```rust
mod a {
    pub fn main() {}
}
mod b {
    pub fn main() {}
}
use a::*;
use b::*;
```
I expected the code to compile, but instead I got the following error:
```
error[E0659]: `main` is ambiguous
  |
  = note: ambiguous because of multiple glob imports of a name in the same module
note: `main` could refer to the function i...

**microsoft/TypeScript #56699** — [Formatting] Missing space after `implements` / `extends` generic 

- Actual: **8.9d** (213.4h, bucket: 1-4 weeks)
- Predicted: **9.3d** (222.1h, bucket: 1-4 weeks)
- Error: 8.8h (4% off)
- Files changed: 3

> ### 🔎 Search Terms
- implement
- format / formatting
- generic
### 🕗 Version & Regression Information
5.4.0-dev.20231205
Not a regression 
### ⏯ Playground Link
_No response_
### 💻 Code
```ts
class Foo implements Array<string>{
}
class Bar implements Number{
}
```

1. Run format
### 🙁 Actual behavior
No space is inserted after `implements Array<string>`. A space is inserted after `implements Numbe...

### Worst 3 predictions (least accurate)

**microsoft/TypeScript #55296** — `attachFileToDiagnostics`: Debug Failure crash 

- Actual: **8.0d** (192.8h, bucket: 1-4 weeks)
- Predicted: **4.0w** (671.3h, bucket: 1-4 weeks)
- Error: 2.8w (248% off)
- Files changed: 7

> ### 🔎 Search Terms
Hi TypeScript team,
In an ongoing effort to secure the JS/TS ecosystem, we integrated the TypeScript project into [Google's OSS-Fuzz project recently](https://github.com/google/oss-fuzz/tree/92cbef824dc66722e3e50eca0069e2461f6d6b91/projects/typescript) with our JS/TS fuzzer [Jazzer.js](https://github.com/CodeIntelligenceTesting/jazzer.js).
Looking at the reports, it seems we wer...

**microsoft/TypeScript #48912** — Type definition for `fractionalSecondDigits` in Intl.DateTimeFormatOptions has incorrect `0`.

- Actual: **7.4d** (178.6h, bucket: 1-4 weeks)
- Predicted: **3.7w** (615.3h, bucket: 1-4 weeks)
- Error: 2.6w (244% off)
- Files changed: 1

> # lib Update Request
<!--
  Please fill in each section completely. Thank you!
  Are you here for one of these commonly-requested lib changes?
    * Object.keys - see https://stackoverflow.com/questions/55012174/
    * Array methods - see https://github.com/microsoft/TypeScript/issues/36554
    * parseInt, parseFloat, isFinite, isNaN, etc. - see https://github.com/microsoft/TypeScript/issues/4002...

**rust-lang/rust #144968** — when a fn is missing a parameter type, the help advice could be improved

- Actual: **9.8d** (235.4h, bucket: 1-4 weeks)
- Predicted: **3.8w** (635.7h, bucket: 1-4 weeks)
- Error: 2.4w (170% off)
- Files changed: 17

> ### Code
```Rust
fn is_even(value) -> bool {
    value % 2 == 0
}
```
### Current output
```plaintext
error: expected one of `:`, `@`, or `|`, found `)`
 --> src/lib.rs:1:17
  |
1 | fn is_even(value) -> bool {
  |                 ^ expected one of `:`, `@`, or `|`
  |
  = note: anonymous parameters are removed in the 2018 edition (see RFC 1685)
help: if this is a `self` type, give it a parameter n...

---

## Actual bucket: **> 4 weeks** (176 samples)

*Median absolute error: 5.2w, median relative error: 85%*

### Best 3 predictions (most accurate)

**microsoft/TypeScript #50099** — `lib.d.ts` Updates for TypeScript 4.9

- Actual: **7.7w** (1292.4h, bucket: > 4 weeks)
- Predicted: **7.8w** (1315.8h, bucket: > 4 weeks)
- Error: 23.3h (2% off)
- Files changed: 11

> Including
* https://github.com/microsoft/TSJS-lib-generator/
* Outstanding `lib.d.ts` PRs to TS

**rust-lang/rust #141122** — CopyProp doesn't always respect Tree Borrows

- Actual: **5.0w** (836.5h, bucket: > 4 weeks)
- Predicted: **4.8w** (805.2h, bucket: > 4 weeks)
- Error: 1.3d (4% off)
- Files changed: 4

> Reduced example from rustlantis, which is accepted by Miri using Tree Borrows without optimizations enabled:
```rust
#![feature(custom_mir, core_intrinsics)]
#![allow(internal_features)]
use std::intrinsics::mir::*;
#[custom_mir(dialect = "runtime")]
fn main() {
  mir! {
    let _1;
    let _2;
    let _3;
    let _4;
    let _5;
    let _6;
    let _7;
    {
      _1 = core::ptr::addr_of!(_2);...

**microsoft/TypeScript #48523** — Missing type of ES2022 `Intl.Segmenter`

- Actual: **4.8w** (807.0h, bucket: > 4 weeks)
- Predicted: **4.3w** (725.0h, bucket: > 4 weeks)
- Error: 3.4d (10% off)
- Files changed: 13

> # lib Update Request
<!--
  Please fill in each section completely. Thank you!
  Are you here for one of these commonly-requested lib changes?
    * Object.keys - see https://stackoverflow.com/questions/55012174/
    * Array methods - see https://github.com/microsoft/TypeScript/issues/36554
    * parseInt, parseFloat, isFinite, isNaN, etc. - see https://github.com/microsoft/TypeScript/issues/4002...

### Worst 3 predictions (least accurate)

**microsoft/vscode #293002** — Switching to plan mode in a new session disables editing tools for the prior running session

- Actual: **5.2w** (865.4h, bucket: > 4 weeks)
- Predicted: **14.5h** (14.5h, bucket: 1 day)
- Error: 5.1w (98% off)
- Files changed: 1

> STR:
1. Plan a change in an agent session, then move to start implementation
2. Navigate back to agent sessions and switch to plan mode for a new task, send that
3.  🐛 First session will have lost edit tools and maybe started showing codeblocks instead
![Image](https://github.com/user-attachments/assets/86edab94-4b63-48c6-909e-62b5bd4147e1)

**microsoft/vscode #233675** — Enter inserts //

- Actual: **12.0w** (2013.7h, bucket: > 4 weeks)
- Predicted: **1.4d** (34.1h, bucket: 1-3 days)
- Error: 11.8w (98% off)
- Files changed: 2

> ![Image](https://github.com/user-attachments/assets/9a265cd1-89a7-4177-b84b-58e50ac9056c)
```ts
		const obsWorkspace = new FakedObservableWorkspace();
		obsWorkspace.addDocument({ 
			uri: createDocumentUri(URI.parse(`file://test.ts`).toString()), initialValue: '' });
		const originalTextDoc = new StringValue(
			);
		const singleEdit = SingleEdit.insert(11, '3D');
```

**facebook/react #31717** — [eslint-plugin-react-hooks] v5.1.0 was released without any changes in github

- Actual: **12.4w** (2075.1h, bucket: > 4 weeks)
- Predicted: **1.7d** (41.5h, bucket: 1-3 days)
- Error: 12.1w (98% off)
- Files changed: 1

> The newer version is released https://www.npmjs.com/package/eslint-plugin-react-hooks/v/5.1.0
However, there aren't any changes in the package dir here as of the time of posting the issue.
https://github.com/facebook/react/tree/372ec00c0384cd2089651154ea7c67693ee3f2a5/packages/eslint-plugin-react-hooks
This is concerning because it could indicate that someone published on behalf of the react team.

---
