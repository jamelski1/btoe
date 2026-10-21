# Example Predictions — Model B (model_b_repo_only)

Test set: 865 samples

For each actual-duration bucket, this report shows:
- **3 best predictions** (smallest relative error)
- **3 worst predictions** (largest relative error)

---

## Actual bucket: **< 1 day** (72 samples)

*Median absolute error: 3.3d, median relative error: 2944%*

### Best 3 predictions (most accurate)

**microsoft/vscode #299152** — Pressing `Alt` doesn't cause the Steering vs Queueing icon to change

- Actual: **7.9h** (7.9h, bucket: < 1 day)
- Predicted: **3.4d** (80.7h, bucket: 3-7 days)
- Error: 3.0d (927% off)
- Files changed: 1

> If you press `Alt` in VS Code you'll see many icons change, showing their alternative actions. This is not the case for the steering/queueing action in the chat. I always queue messages but I'm always unsure if the keybinding `Alt + Enter` will actually do what I want because it does not change the icon
<img width="217" height="121" alt="Image" src="https://github.com/user-attachments/assets/1e17a...

**facebook/react #34791** — Bug: “Display density” field appears twice in React Developer Tools settings

- Actual: **7.8h** (7.8h, bucket: < 1 day)
- Predicted: **3.4d** (80.7h, bucket: 3-7 days)
- Error: 3.0d (934% off)
- Files changed: 1

> <img width="469" height="275" alt="Image" src="https://github.com/user-attachments/assets/476fb9e9-b8b0-47db-9943-8ca253826e67" />
DevTools version: [7.0.0-3b2a398106](https://github.com/facebook/react/blob/main/packages/react-devtools/CHANGELOG.md#700)
## Steps To Reproduce
1. Open React Developer Tools in your browser.
2. Go to the General settings tab.
The associated PR : [Anatole-Godard:pr3479...

**microsoft/vscode #247098** — JAWS incorrectly announces toolbar label "Toolbar for code block which can be reached via tab" information pulled from ARIA attributes:A11y_Visual Studio Code Client_get started with accessibility feature_Usable

- Actual: **7.7h** (7.7h, bucket: < 1 day)
- Predicted: **3.4d** (80.7h, bucket: 3-7 days)
- Error: 3.0d (948% off)
- Files changed: 1

> [[Check out Accessibility Insights!](https://accessibilityinsights.io/)]- Identify accessibility bugs before check-in and make bug fixing faster and easier.
## GitHub Tags:
#A11yeDAD; #A11yTCS; #DesktopApp; #Win32; #Visual Studio Code Client; #BM-VisualStudioCodeClient-Win32-Jan2024; #A11yUsable; #Keyboard; #FTP; #Win32; #JAWS; #Closed; #A11yFixed;
## Environment and OS details:
Visual Studio Code...

### Worst 3 predictions (least accurate)

**microsoft/vscode #270489** — Show ✨ for rename suggestions OOTB

- Actual: **1.4h** (1.4h, bucket: < 1 day)
- Predicted: **5.7d** (135.8h, bucket: 3-7 days)
- Error: 5.6d (9741% off)
- Files changed: 2

> When you do not have Copilot installed, showing the ✨ in the F2 rename box OOTB to trigger setup:
<img width="336" height="164" alt="Image" src="https://github.com/user-attachments/assets/4716d198-d10f-4e4e-b52b-7b11b40bcf84" />
//cc @cwebster-99

**microsoft/vscode #259765** — Run in terminal: Auto approve should default to case insensitive for pwsh

- Actual: **1.5h** (1.5h, bucket: < 1 day)
- Predicted: **5.8d** (138.4h, bucket: 3-7 days)
- Error: 5.7d (9018% off)
- Files changed: 3

> pwsh is case insensitive on mac too.
https://github.com/microsoft/vscode/blob/2c804a60266ce4f499599b1171b245a7c4386c88/src/vs/workbench/contrib/terminalContrib/chatAgentTools/common/terminalChatAgentToolsConfiguration.ts#L88-L110

**microsoft/TypeScript #52277** — `switch`/`case` completions fail when has a negative literal type

- Actual: **2.3h** (2.3h, bucket: < 1 day)
- Predicted: **7.9d** (190.6h, bucket: 1-4 weeks)
- Error: 7.8d (8109% off)
- Files changed: 3

> Found from https://github.com/microsoft/TypeScript/issues/52253#issuecomment-1383261940
```ts
export function foo(position: -1 | 0 | 1) {
  switch (position) {
    /**/
  }
}
```
Request completions with snippet text (`includeInsertTextCompletions`) at `/**/`
This currently errors:
```
Response received: completionInfo (2114). Request took 186 ms. Success: false . Message: Error processing request...

---

## Actual bucket: **1 day** (91 samples)

*Median absolute error: 4.9d, median relative error: 730%*

### Best 3 predictions (most accurate)

**facebook/react #21541** — Create GitHub actions to auto verify DevTools issues have repro steps

- Actual: **23.0h** (23.0h, bucket: 1 day)
- Predicted: **3.4d** (80.7h, bucket: 3-7 days)
- Error: 2.4d (251% off)
- Files changed: 1

> Many of the issues created with the with the [`devtools_bug_report.yml`](https://github.com/facebook/react/blob/master/.github/ISSUE_TEMPLATE/devtools_bug_report.yml) template are missing repro information (e.g. a "localhost" or otherwise invalid URL, missing or no repro description). I usually have to review, label, comment, and close this by hand.
It would be nice if we had an automated action t...

**microsoft/vscode #249772** — [14f] potential listener LEAK detected, having 1063 listeners already. MOST frequent listener (851):

- Actual: **22.5h** (22.5h, bucket: 1 day)
- Predicted: **3.4d** (80.7h, bucket: 3-7 days)
- Error: 2.4d (259% off)
- Files changed: 1

> ```javascript
Error
at l0i.create in ./file:/Users/cloudtest/vss/_work/1/s/src/vs/base/common/event.ts:927:15
at p4e.q [as onDidChangeReadonly] in ./file:/Users/cloudtest/vss/_work/1/s/src/vs/base/common/event.ts:1112:34
at c8e.t in ./file:/Users/cloudtest/vss/_work/1/s/src/vs/workbench/common/editor/resourceEditorInput.ts:67:49
at new Qce in ./file:/Users/cloudtest/vss/_work/1/s/src/vs/workbench/...

**kubernetes/kubernetes #663** — Minions failing health checks should not cause apiserver to emit 500's

- Actual: **22.4h** (22.4h, bucket: 1 day)
- Predicted: **3.4d** (80.7h, bucket: 3-7 days)
- Error: 2.4d (260% off)
- Files changed: 1

> Report via email:
```
E0728 16:23:38.989876 12691 pod_cache.go:79] Error synchronizing container list: &url.Error{Op:"Get", URL:"http://kubernetes-minion-2.c.mbennett-gce.internal:10250/healthz", Err:(*net.OpError)(0xc21012c340)}
I0728 16:23:39.075820 12691 log.go:135] GET /api/v1beta1/pods: (169.438832ms) 500
goroutine 35 [running]:
github.com/GoogleCloudPlatform/kubernetes/pkg/httplog.(*respLogg...

### Worst 3 predictions (least accurate)

**microsoft/TypeScript #55545** — Wrong code suggestion when using "Mapped Types" as function parameter

- Actual: **8.0h** (8.0h, bucket: 1 day)
- Predicted: **7.9d** (190.6h, bucket: 1-4 weeks)
- Error: 7.6d (2278% off)
- Files changed: 2

> Type: **Bug**
Extension version: 5.3.20230827
Version: 1.81.1 (user setup)
Commit: 6c3e3dba23e8fadc360aed75ce363ba185c49794
Date: 2023-08-09T22:22:42.175Z
Electron: 22.3.18
ElectronBuildId: 22689846
Chromium: 108.0.5359.215
Node.js: 16.17.1
V8: 10.8.168.25-electron.0
OS: Windows_NT x64 10.0.19045
Problem:
The Codesuggestion shows "1", "2", "3", "4" event though `a` is "valA".  When hovering it als...

**microsoft/vscode #252907** — User mcp.json should follow standard mcp.json schema

- Actual: **8.5h** (8.5h, bucket: 1 day)
- Predicted: **7.2d** (172.0h, bucket: 1-4 weeks)
- Error: 6.8d (1913% off)
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

**microsoft/TypeScript #59836** — `Array.fromAsync` type define on its `mapFn` missing the index as second argument

- Actual: **9.7h** (9.7h, bucket: 1 day)
- Predicted: **7.9d** (190.6h, bucket: 1-4 weeks)
- Error: 7.5d (1867% off)
- Files changed: 5

> ### 🔎 Search Terms
fromAsync index
### 🕗 Version & Regression Information
- This changed between versions **5.4** and **5.5**
- This changed in commit or PR #57748
- This is the behavior in every version I tried, and I reviewed the FAQ for entries about `Array.fromAsync`
- I was unable to test this on prior versions because it only introduced in **5.4**

### ⏯ Playground Link
https://www.typescrip...

---

## Actual bucket: **1-3 days** (150 samples)

*Median absolute error: 4.6d, median relative error: 218%*

### Best 3 predictions (most accurate)

**microsoft/vscode #253032** — Rm reset command after testing

- Actual: **3.0d** (71.7h, bucket: 1-3 days)
- Predicted: **3.4d** (80.7h, bucket: 3-7 days)
- Error: 8.9h (12% off)
- Files changed: 1

> Rm this from `terminal.suggest.contribution.ts` after testing
```
registerActiveInstanceAction({
	id: TerminalSuggestCommandId.ResetDiscoverability,
	title: localize2('workbench.action.terminal.resetDiscoverability', 'Reset Suggest Discoverability'),
	f1: true,
	precondition: ContextKeyExpr.and(
		ContextKeyExpr.or(TerminalContextKeys.processSupported, TerminalContextKeys.terminalHasBeenCreated),...

**microsoft/vscode #250895** — VS Code fails silently when no default browser is set — GitHub authentication hangs without fallback

- Actual: **3.0d** (71.4h, bucket: 1-3 days)
- Predicted: **3.4d** (80.7h, bucket: 3-7 days)
- Error: 9.2h (13% off)
- Files changed: 1

> **Description:**
When no default browser is set in Windows 10 (e.g. user removed Edge and no other browser is configured), GitHub authentication in VS Code fails silently. The message `Signing in to github.com...` is shown indefinitely, and no fallback (like device code or manual URL copy) is presented to the user.
This results in complete authentication failure with no guidance.
---
**Steps to Re...

**microsoft/vscode #239996** — chat should keep playing the accessibilty chat response pending cue, not timeout

- Actual: **3.0d** (71.3h, bucket: 1-3 days)
- Predicted: **3.4d** (80.7h, bucket: 3-7 days)
- Error: 9.4h (13% off)
- Files changed: 1

> cc @jooyoungseo
The chat accessibility progress signal times out after a while. We should not let that happen as an edits session can take a long time.

### Worst 3 predictions (least accurate)

**microsoft/TypeScript #48541** — Refactoring to "extract to inner/local function" crashes in concise arrow function

- Actual: **1.0d** (24.1h, bucket: 1-3 days)
- Predicted: **7.9d** (190.6h, bucket: 1-4 weeks)
- Error: 6.9d (692% off)
- Files changed: 8

> Repro of https://github.com/microsoft/TypeScript/issues/46947
```ts
let x = [1, 2, 3];
let y = x.map(e => [|e + e|])
```
Request "extract to inner function in arrow function" on that `[|region|]`.
```
Response received: getEditsForRefactor (810). Request took 2 ms. Success: false . Message: Error processing request. Debug Failure. False expression: Changes overlap
Verbose Debug Information: {"pos"...

**rust-lang/rust #153732** — [E0284] suggestion is useless

- Actual: **1.0d** (24.4h, bucket: 1-3 days)
- Predicted: **7.9d** (190.6h, bucket: 1-4 weeks)
- Error: 6.9d (682% off)
- Files changed: 16

> ### Code
```Rust
trait S {
    type Assoc<U>: T;
    fn f<B, F>(self, f: Self::Assoc<F>) -> Self::Assoc<B>;
}
trait T: S { }
fn g<A>(a: A) where A: T {
    a.f::<A::Assoc<A>, _>(todo!());
}
```
### Current output
```Shell
error[E0282]: type annotations needed
 --> src/lib.rs:9:7
  |
9 |     a.f::<A::Assoc<A>, _>(todo!());
  |       ^ cannot infer type of the type parameter `F` declared on the meth...

**rust-lang/rust #150755** — `alloc_error_handler` signature mismatch

- Actual: **1.0d** (24.6h, bucket: 1-3 days)
- Predicted: **7.9d** (190.6h, bucket: 1-4 weeks)
- Error: 6.9d (675% off)
- Files changed: 46

> I tried this code: https://github.com/Spxg/bisect/tree/master/alloc_signature_mismatch
output:
```sh
$ RUSTFLAGS="-Dwarnings" cargo build --target wasm32-unknown-unknown
   Compiling alloc_signature_mismatch v0.1.0 (/home/uharsn/repo/bisect/alloc_signature_mismatch)
error: linker stderr: rust-lld: function signature mismatch: _RNvCsiGVaDesi5rv_7___rustc26___rust_alloc_error_handler
       >>> defi...

---

## Actual bucket: **3-7 days** (137 samples)

*Median absolute error: 2.5d, median relative error: 45%*

### Best 3 predictions (most accurate)

**kubernetes/kubernetes #133916** — [cli-runtime] [client-go] ConfigFlags when set cert/key fields get validation error when merging with kubeconfig data

- Actual: **5.9d** (141.7h, bucket: 3-7 days)
- Predicted: **5.8d** (138.4h, bucket: 3-7 days)
- Error: 3.3h (2% off)
- Files changed: 3

> ### What happened?
When using ConfigFlags with CertFile and KeyFile set to override a kubeconfig configuration that contains inline certificate data (ClientCertificateData and ClientKeyData), the configuration merge process fails with validation errors: 
```sh
invalid configuration: [client-cert-data and client-cert are both specified for <user>. client-cert-data will override., client-key-data an...

**microsoft/vscode #240866** — Wrong command for Zsh Integration RC file since `ZSH_VERSION` use Semantic Versioning

- Actual: **3.5d** (83.0h, bucket: 3-7 days)
- Predicted: **3.4d** (80.7h, bucket: 3-7 days)
- Error: 2.3h (3% off)
- Files changed: 1

> <!-- ⚠️⚠️ Do Not Delete This! bug_report_template ⚠️⚠️ -->
<!-- Please read our Rules of Conduct: https://opensource.microsoft.com/codeofconduct/ -->
<!-- 🕮 Read our guide about submitting issues: https://github.com/microsoft/vscode/wiki/Submitting-Bugs-and-Suggestions -->
<!-- 🔎 Search existing issues to avoid creating duplicates. -->
<!-- 🧪 Test using the latest Insiders build to see if your iss...

**kubernetes/kubernetes #26526** — Update API Reference script

- Actual: **3.5d** (83.3h, bucket: 3-7 days)
- Predicted: **3.4d** (80.7h, bucket: 3-7 days)
- Error: 2.6h (3% off)
- Files changed: 1

> Hi, 
there is a minor bug in the [hack/update-api-reference-docs.sh](https://github.com/kubernetes/kubernetes/blob/master/hack/update-api-reference-docs.sh) script or at least some inconsistency. When I run the update script white spaces are ignores with the `-w`option [see line 98](https://github.com/kubernetes/kubernetes/blob/master/hack/update-api-reference-docs.sh#L98) but in the [verify scrip...

### Worst 3 predictions (least accurate)

**microsoft/vscode #284758** — Add more custom glyphs to the terminal

- Actual: **3.3d** (78.2h, bucket: 3-7 days)
- Predicted: **10.0d** (240.5h, bucket: 1-4 weeks)
- Error: 6.8d (208% off)
- Files changed: 9

> https://www.unicode.org/charts/PDF/U1FB00.pdf
Upstream: https://github.com/xtermjs/xterm.js/issues/5464, https://github.com/xtermjs/xterm.js/issues/5466 (and more...)

**microsoft/TypeScript #54106** — Error from completionEntryDetails on entry before definition of merged variable and type alias

- Actual: **3.0d** (72.3h, bucket: 3-7 days)
- Predicted: **7.9d** (190.6h, bucket: 1-4 weeks)
- Error: 4.9d (164% off)
- Files changed: 3

> Minimal repro:
```ts
/**/
type lolol = any;
declare const lolol: any;
```
Request completions and view completion entry details on `lolol`.
**Expected:**
Something like
```
type lolol = any;
var lolol: any;
```
**Actual:**
```
Response received: completionEntryDetails (486). Request took 4 ms. Success: false . Message: Error processing request. Cannot read properties of undefined (reading 'kind')...

**rust-lang/rust #143523** — Diagnostic suggests changing `&mut vec![1]` to `mut vec![1]`

- Actual: **3.0d** (72.4h, bucket: 3-7 days)
- Predicted: **7.9d** (190.6h, bucket: 1-4 weeks)
- Error: 4.9d (163% off)
- Files changed: 48

> ### Code
```Rust
trait Trait {}
impl Trait for Vec<i32> {}
fn foo(_: impl Trait) {}
fn main() {
    foo(&mut vec![1]);
}
```
### Current output
```Shell
error[E0277]: the trait bound `&mut Vec<{integer}>: Trait` is not satisfied
 --> src/main.rs:8:9
  |
8 |     foo(&mut vec![1]);
  |     --- ^^^^^^^^^^^^ the trait `Trait` is not implemented for `&mut Vec<{integer}>`
  |     |
  |     required by a...

---

## Actual bucket: **1-4 weeks** (239 samples)

*Median absolute error: 9.5d, median relative error: 60%*

### Best 3 predictions (most accurate)

**microsoft/TypeScript #55296** — `attachFileToDiagnostics`: Debug Failure crash 

- Actual: **8.0d** (192.8h, bucket: 1-4 weeks)
- Predicted: **7.9d** (190.6h, bucket: 1-4 weeks)
- Error: 2.2h (1% off)
- Files changed: 7

> ### 🔎 Search Terms
Hi TypeScript team,
In an ongoing effort to secure the JS/TS ecosystem, we integrated the TypeScript project into [Google's OSS-Fuzz project recently](https://github.com/google/oss-fuzz/tree/92cbef824dc66722e3e50eca0069e2461f6d6b91/projects/typescript) with our JS/TS fuzzer [Jazzer.js](https://github.com/CodeIntelligenceTesting/jazzer.js).
Looking at the reports, it seems we wer...

**microsoft/TypeScript #51688** — Type narrowing regression with switch + for in TypeScript 4.9

- Actual: **8.1d** (193.6h, bucket: 1-4 weeks)
- Predicted: **7.9d** (190.6h, bucket: 1-4 weeks)
- Error: 2.9h (2% off)
- Files changed: 6

> # Bug Report
It is possible to generate a `"Variable 'X' is used before being assigned."` error on TypeScript 4.9 where it previously did not in TypeScript 4.8.  This seems to be when we have combination of `switch` statements and `for` loop.
### 🔎 Search Terms
switch
for
type check
### 🕗 Version & Regression Information
- This changed between versions 4.8.4 and 4.9.3
- This continues to error wit...

**rust-lang/rust #146163** — Miscomputation error on nightly starting with 2025-08-11

- Actual: **7.7d** (185.9h, bucket: 1-4 weeks)
- Predicted: **7.9d** (190.6h, bucket: 1-4 weeks)
- Error: 4.8h (3% off)
- Files changed: 1

> This is a miscomputation error inside an implementation of a cryptographic algorithm (I am on an `aarch64-apple-darwin` and have not checked other targets) .
https://github.com/RustCrypto/password-hashes/tree/master/yescrypt
The source code in question, the `yescrypt` crate, has been mechanically translated from C (using corrode), contains ample usage of `unsafe` and is not idiomatic Rust (somethi...

### Worst 3 predictions (least accurate)

**kubernetes/kubernetes #117909** — generic vs platform/backend-specific options in kube-proxy

- Actual: **4.2w** (702.6h, bucket: 1-4 weeks)
- Predicted: **3.4d** (80.7h, bucket: 3-7 days)
- Error: 3.7w (89% off)
- Files changed: 1

> There was some discussion in #117297 about generic vs platform-specific options, especially around `--detect-local-mode`, which can be specified on Windows even though it doesn't actually make sense there. (Or at least, it's not _implemented_ there... I'm not sure if winkernel would benefit from it or not?)
Current version of kube-proxy config:
```
kind: KubeProxyConfiguration
apiVersion: kubeprox...

**microsoft/vscode #275048** — Inline chat: picking "Rephrase" should restore the prompt I had

- Actual: **4.2w** (701.0h, bucket: 1-4 weeks)
- Predicted: **3.4d** (80.7h, bucket: 3-7 days)
- Error: 3.7w (88% off)
- Files changed: 1

> Testing #274768
When a prompt results in the dialog to show up to rephrase or continue in panel chat, picking "Rephrase" does not put my prompt back into inline chat.
<img width="316" height="359" alt="Image" src="https://github.com/user-attachments/assets/a6ffecdb-a22f-4975-b8b8-1cfdee659957" />

**facebook/react #2896** — Clarify --harmony dependence in 'Transferring with ... in JSX' docs

- Actual: **4.2w** (698.9h, bucket: 1-4 weeks)
- Predicted: **3.4d** (80.7h, bucket: 3-7 days)
- Error: 3.7w (88% off)
- Files changed: 1

> New to React. I was following the tutorial and ran into a snag. Copy pasting the example
[Transferring with ... in JSX](http://facebook.github.io/react/docs/transferring-props.html#transferring-with-...-in-jsx) example lead to `Uncaught SyntaxError: Unexpected token {` on line 2 on Chrome. 
I was using the in-browser JSX transformer.
It took me awhile to figure out this is a proposed JavaScript th...

---

## Actual bucket: **> 4 weeks** (176 samples)

*Median absolute error: 5.7w, median relative error: 86%*

### Best 3 predictions (most accurate)

**kubernetes/kubernetes #136786** — kube-proxy fails to sync in nftables mode when newer nftables sets exist

- Actual: **5.0w** (833.3h, bucket: > 4 weeks)
- Predicted: **10.1d** (243.3h, bucket: 1-4 weeks)
- Error: 3.5w (71% off)
- Files changed: 12

> ### What happened?
kube-proxy crashes repeatedly, causing the container network to not function.
```
E0205 20:24:21.385767       1 proxier.go:1217] "Failed to list existing sets" err="failed to run nft: signal: segmentation fault (core dumped)" ipFamily="IPv4"
E0205 20:24:22.721950       1 proxier.go:1788] "nftables sync failed" err="signal: segmentation fault (core dumped)" ipFamily="IPv4"
I0205...

**microsoft/TypeScript #50832** — False positive "await has no effect on the type" diagnostic with mixed generic union

- Actual: **4.3w** (720.3h, bucket: > 4 weeks)
- Predicted: **7.9d** (190.6h, bucket: 1-4 weeks)
- Error: 3.2w (74% off)
- Files changed: 2

> # Bug Report
### 🔎 Search Terms
await has no effect on type, 80007
### 🕗 Version & Regression Information
- This is the behavior in every version I tried
### ⏯ Playground Link
[Playground link with relevant code](https://www.typescriptlang.org/play?ts=4.9.0-dev.20220918#code/IYZwngdgxgBAZgV2gFwJYHsLwgJgDwAqMApgB7LEQAmIMACgE7oC2qIxeAbuqlQHwwAPjG68+ACmAAuGAQCUMAN4AoGDGAB3YKmTqA3MoC+QA)
### 💻 Code
``...

**microsoft/TypeScript #62720** — Conditional type inference fails when generic parameter has Readonly<T> in function parameter position

- Actual: **4.3w** (724.1h, bucket: > 4 weeks)
- Predicted: **7.9d** (190.6h, bucket: 1-4 weeks)
- Error: 3.2w (74% off)
- Files changed: 7

> ### 🔎 Search Terms
Readonly generic parameter conditional type inference conditional type matching with Readonly parameter generic constraint Readonly intersection type mapped type readonly conditional inference failure Readonly parameter affects return type inference
### 🕗 Version & Regression Information
- This is the behavior in every version I tried, and I reviewed the FAQ for entries about co...

### Worst 3 predictions (least accurate)

**facebook/react #31717** — [eslint-plugin-react-hooks] v5.1.0 was released without any changes in github

- Actual: **12.4w** (2075.1h, bucket: > 4 weeks)
- Predicted: **3.4d** (80.7h, bucket: 3-7 days)
- Error: 11.9w (96% off)
- Files changed: 1

> The newer version is released https://www.npmjs.com/package/eslint-plugin-react-hooks/v/5.1.0
However, there aren't any changes in the package dir here as of the time of posting the issue.
https://github.com/facebook/react/tree/372ec00c0384cd2089651154ea7c67693ee3f2a5/packages/eslint-plugin-react-hooks
This is concerning because it could indicate that someone published on behalf of the react team.

**microsoft/vscode #250424** — Commands in warning hover are heavily truncated

- Actual: **10.5w** (1756.4h, bucket: > 4 weeks)
- Predicted: **3.4d** (80.7h, bucket: 3-7 days)
- Error: 10.0w (95% off)
- Files changed: 1

> Testing #249660
<img width="537" alt="Image" src="https://github.com/user-attachments/assets/606ee26f-31bf-4980-9e5f-0ce593ba0ef5" />

**kubernetes/kubernetes #119632** — NCC-E003660-TTV: Timing Side Channel in Bootstrap Tokens Generation and Handling

- Actual: **10.1w** (1691.0h, bucket: > 4 weeks)
- Predicted: **3.4d** (80.7h, bucket: 3-7 days)
- Error: 9.6w (95% off)
- Files changed: 1

> ### NCC-E003660-TTV: Timing Side Channel in Bootstrap Tokens Generation and Handling
This issue was reported in the [Kubernetes 1.24 Security Audit Report](https://github.com/kubernetes/sig-security/blob/main/sig-security-external-audit/security-audit-2021-2022/findings/Kubernetes%20v1.24%20Final%20Report.pdf)
**Impact**
Attackers may determine Bootstrap Token values based on timing-based side cha...

---
