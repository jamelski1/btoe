# Example Predictions — Model B (model_b_repo_only)

Test set: 896 samples

For each actual-duration bucket, this report shows:
- **3 best predictions** (smallest relative error)
- **3 worst predictions** (largest relative error)

---

## Actual bucket: **< 1 day** (86 samples)

*Median absolute error: 5.3d, median relative error: 3694%*

### Best 3 predictions (most accurate)

**facebook/react #34791** — Bug: “Display density” field appears twice in React Developer Tools settings

- Actual: **7.8h** (7.8h, bucket: < 1 day)
- Predicted: **3.0d** (72.6h, bucket: 3-7 days)
- Error: 2.7d (831% off)
- Files changed: 1

> <img width="469" height="275" alt="Image" src="https://github.com/user-attachments/assets/476fb9e9-b8b0-47db-9943-8ca253826e67" />
DevTools version: [7.0.0-3b2a398106](https://github.com/facebook/react/blob/main/packages/react-devtools/CHANGELOG.md#700)
## Steps To Reproduce
1. Open React Developer Tools in your browser.
2. Go to the General settings tab.
The associated PR : [Anatole-Godard:pr3479...

**facebook/react #21986** — [DevTools Bug]: Component tree size too small, components can't be selected

- Actual: **7.9h** (7.9h, bucket: < 1 day)
- Predicted: **3.4d** (81.9h, bucket: 3-7 days)
- Error: 3.1d (940% off)
- Files changed: 3

> ### Website or app
https://reactjs.org/
### Repro steps
1. Visit reactjs.org
2. Open devtools
3. Open "Components" tab
At first the component tree won't appear. Once I'm at the "Components" tab, I then have to also refresh the page to make the tree render. And when it does render, it still doesn't work properly.
As a note, this issue started happening after I had to forcibly restart my computer. S...

**facebook/react #20829** — Scheduler's use of SharedArrayBuffer will require cross-origin isolation

- Actual: **6.3h** (6.3h, bucket: < 1 day)
- Predicted: **3.0d** (72.6h, bucket: 3-7 days)
- Error: 2.8d (1054% off)
- Files changed: 1

> React version: v17.0.1
## Steps To Reproduce
1. `npx create-react-app myapp`
2. `cd myapp && npm start`
3. Open http://localhost:3000 in **Chrome 88 or 89, regular or Incognito mode**
4. Open DevTools: the warning is displayed
Link to code example: https://react-z95km1.stackblitz.io/
https://stackblitz.com/edit/react-z95km1
## The current behavior
Warning: `scheduler.development.js:298 [Deprecatio...

### Worst 3 predictions (least accurate)

**microsoft/vscode #242248** — window.title loses information when switching tabs on Windows

- Actual: **1.0h** (1.0h, bucket: < 1 day)
- Predicted: **5.4d** (129.9h, bucket: 3-7 days)
- Error: 5.4d (12499% off)
- Files changed: 2

> 1. On the latest Insiders, open a repository with multiple files, some of them modified. Enable Command Center.
2. Open a modified file. Enable screen reader accessibility mode.
3. :bug: The window title flashes or doesn't seem to change.
4. Disable screen reader accessibility mode.
5. Switch to another tab and back.
6. :bug: Window title goes back to being the repository name.
![Screencap of step...

**facebook/react #21792** — [DevTools] Use line number and column number to match hook

- Actual: **1.2h** (1.2h, bucket: < 1 day)
- Predicted: **5.9d** (140.5h, bucket: 3-7 days)
- Error: 5.8d (11637% off)
- Files changed: 24

> DevTools named hook parsing logic currently matches AST nodes using the original line number:
https://github.com/facebook/react/blob/ed6c091fe961a3b95e956ebcefe8f152177b1fb7/packages/react-devtools-extensions/src/parseHookNames.js#L341-L346
But this may not be sufficient, as mentioned in comment https://github.com/facebook/react/pull/21641#discussion_r662951987:
> Are we assuming that a line numbe...

**microsoft/vscode #260110** — Smoke-test failure: directory not empty

- Actual: **1.1h** (1.1h, bucket: < 1 day)
- Predicted: **5.4d** (129.9h, bucket: 3-7 days)
- Error: 5.4d (11572% off)
- Files changed: 3

> ```
> cd test/smoke && node test/index.js --web --tracing --headless
D:\a\_work\1\s\test\smoke\node_modules\rimraf\rimraf.js:310
        throw er
        ^
Error: ENOTEMPTY: directory not empty, rmdir 'C:\Users\CLOUDT~1\AppData\Local\Temp\vscsmoke'
    at Object.rmdirSync (node:fs:1201:11)
    at rmkidsSync (D:\a\_work\1\s\test\smoke\node_modules\rimraf\rimraf.js:349:27)
    at rmdirSync (D:\a\_wo...

---

## Actual bucket: **1 day** (90 samples)

*Median absolute error: 4.7d, median relative error: 651%*

### Best 3 predictions (most accurate)

**facebook/react #1115** — Support HTML5 anchor tag attributes

- Actual: **23.8h** (23.8h, bucket: 1 day)
- Predicted: **3.0d** (72.6h, bucket: 3-7 days)
- Error: 2.0d (205% off)
- Files changed: 1

> React does not currently support the HTML5 anchor tag attributes `download` and `hreflang`. I do not know what the current status for adoption of those attributes are, but I know that Chrome supports `download` it and I am pretty sure that Firefox supports it as well.
I could really care less about `hreflang`, but I thought I'd mention it out of completeness.
See also:
- http://www.w3.org/html/wg/...

**facebook/react #31100** — [DevTools Bug]: Script tag connection method not working in 6.0.0

- Actual: **19.8h** (19.8h, bucket: 1 day)
- Predicted: **3.0d** (72.6h, bucket: 3-7 days)
- Error: 2.2d (266% off)
- Files changed: 1

> ### Website or app
A basic Create React App project with React DevTools connected via script tag.
### Repro steps
1. Install React DevTools globally: `npm install -g react-devtools` or `yarn global add react-devtools`
2. Create a new React app: `npx create-react-app my-app`
3. Navigate to the project directory: `cd my-app`
4. Open `public/index.html` and add the following script tag at the beginni...

**facebook/react #26821** — [DevTools Bug]: Strict mode badge points to the old docs

- Actual: **18.1h** (18.1h, bucket: 1 day)
- Predicted: **3.0d** (72.6h, bucket: 3-7 days)
- Error: 2.3d (301% off)
- Files changed: 1

> ### Website or app
https://fb.me/devtools-strict-mode
### Repro steps
The Strict mode warning badge points to https://fb.me/devtools-strict-mode which points to the strict mode section in [the old docs](https://legacy.reactjs.org/docs/strict-mode.html) instead of [the new docs](https://react.dev/reference/react/StrictMode).
Badge:
<img width="273" alt="Screenshot 2023-05-16 at 20 20 59" src="https...

### Worst 3 predictions (least accurate)

**kubernetes/kubernetes #131432** — [Flaking Test] UT k8s.io/apiserver/pkg/storage: etcd3 TestWatchErrResultNotBlockAfterCancel

- Actual: **8.1h** (8.1h, bucket: 1 day)
- Predicted: **5.4d** (129.9h, bucket: 3-7 days)
- Error: 5.1d (1500% off)
- Files changed: 2

> ### Which jobs are flaking?
https://prow.k8s.io/job-history/gs/kubernetes-ci-logs/logs/ci-kubernetes-unit
https://prow.k8s.io/job-history/gs/kubernetes-ci-logs/logs/ci-kubernetes-unit-ppc64le
### Which tests are flaking?
k8s.io/apiserver/pkg/storage: etcd3 TestWatchErrResultNotBlockAfterCancel
### Since when has it been flaking?
Probably since https://github.com/kubernetes/kubernetes/pull/131162 m...

**microsoft/TypeScript #62657** — Decorator declaration inside a function causes the typescript language server to crash

- Actual: **8.2h** (8.2h, bucket: 1 day)
- Predicted: **5.4d** (129.9h, bucket: 3-7 days)
- Error: 5.1d (1484% off)
- Files changed: 11

> ### 🔎 Search Terms
decorator language server crash
### 🕗 Version & Regression Information
- This is the behavior in every version I tried (5.9.3 and 5.4.5), and I reviewed the FAQ for entries about "decorator"
### ⏯ Playground Link
https://www.typescriptlang.org/play/?#code/KYDwDg9gTgLgBAMwK4DsDGMCWEVwM4zBgAUMAhlAObAwBccxAdMxZXvWSgJ4DaAugEo4AXgB8cTlwA0cNDkIg6cAMIAbMnjwBZGgAsIAEwAiwOVDIxoy+aBhCA3gC...

**kubernetes/kubernetes #134622** — build: _output/bin/ginkgo not found

- Actual: **8.5h** (8.5h, bucket: 1 day)
- Predicted: **5.4d** (129.9h, bucket: 3-7 days)
- Error: 5.1d (1421% off)
- Files changed: 1

> ### What happened?
Several DRA presubmit jobs do:
```
make 'WHAT=github.com/onsi/ginkgo/v2/ginkgo k8s.io/kubernetes/test/e2e/e2e.test'
ginkgo=_output/bin/ginkgo
e2e_test=_output/bin/e2e.test
```
This started to fail [sometime around Oct 14 23:14:54](https://prow.k8s.io/job-history/gs/kubernetes-ci-logs/pr-logs/directory/pull-kubernetes-kind-dra) with:
```
+ _output/bin/ginkgo run --nodes=8 --timeo...

---

## Actual bucket: **1-3 days** (157 samples)

*Median absolute error: 3.5d, median relative error: 189%*

### Best 3 predictions (most accurate)

**facebook/react #22293** — Bug: Maximum call stack size exceeded (React Devtools)

- Actual: **3.0d** (71.9h, bucket: 1-3 days)
- Predicted: **3.0d** (72.6h, bucket: 3-7 days)
- Error: 42 min (1% off)
- Files changed: 1

> I encountered the same issue as #20640 but using `react-devtools` as a stand-alone app instead of from the the browser.
The bottom line is that the profiler becomes unresponsive after any interaction with a heavily loaded react page.
React version:
* React: 17.0.2
* ReactDOM: 17.0.2
* React Devtools: 4.18.0
## Steps To Reproduce
1. Attach a react-devtools stand-alone (`yarn run react-devtools`) to...

**facebook/react #22422** — [DevTools Bug]: Emoji as visual helper produce strange symbole

- Actual: **2.9d** (68.5h, bucket: 1-3 days)
- Predicted: **2.9d** (69.7h, bucket: 1-3 days)
- Error: 1.1h (2% off)
- Files changed: 3

> ### Website or app
https://codesandbox.io/s/react-playground-forked-j4niq
### Repro steps
Emoji seem supported but produce strange symbole
![image](https://user-images.githubusercontent.com/24865815/133793744-55a55582-90ad-425f-8a40-4c061a3c1d80.png)
To test emoji on Window Os, use `[win]+[.]` 🟩

### How often does this bug happen?
Every time
### DevTools package (automated)
_No response_
### DevT...

**facebook/react #22834** — [DevTools Bug]: CDN-based site not working

- Actual: **2.9d** (70.5h, bucket: 1-3 days)
- Predicted: **3.0d** (72.6h, bucket: 3-7 days)
- Error: 2.1h (3% off)
- Files changed: 1

> ### Website or app
https://lcdev.shaped.ca
### Repro steps
Dev tools not working in FF or Chrome, says "This page doesn't appear to be using react".
React is included via CDN as shown on react website https://reactjs.org/docs/cdn-links.html:
``
	<script crossorigin="anonymous" src="https://unpkg.com/react@17/umd/react.development.js"></script>
``
Web Console on said page says:
``
Download the Reac...

### Worst 3 predictions (least accurate)

**facebook/react #6742** — ReactPrerfTools: 15.1.0-alpha.1 

- Actual: **1.0d** (24.7h, bucket: 1-3 days)
- Predicted: **8.3d** (199.3h, bucket: 1-4 weeks)
- Error: 7.3d (707% off)
- Files changed: 9

> I was testing latest refactor of PerfTools.
When using printOperations() often (but not always) I get 
```
Uncaught TypeError: Cannot read property 'displayName' of undefined
```
in getOperations() on the line:
```
var {displayName, ownerID} = treeSnapshot[instanceID];
```

**facebook/react #17073** — [DevTools] polish hooks: complex values preview 

- Actual: **1.2d** (29.2h, bucket: 1-3 days)
- Predicted: **8.3d** (199.3h, bucket: 1-4 weeks)
- Error: 7.1d (582% off)
- Files changed: 9

> We create many `useDebugValue` helpers, loggers and so one now, so we can feel less pain.
What matter (**Updated**)
- previewing complex values brifely like chrome devtools does it for arrays, sets, maps, objects,,,
I [wrote related twit](https://twitter.com/mxtnr/status/1178271362890240001) recently with one of my DebugValue helpers. screenshot out here:
<img width="556" alt="Screenshot 2019-09-2...

**facebook/react #21868** — [DevTools] Named hooks compatibility for create-react-app DEV mode

- Actual: **1.0d** (25.0h, bucket: 1-3 days)
- Predicted: **5.8d** (139.5h, bucket: 3-7 days)
- Error: 4.8d (458% off)
- Files changed: 15

> Something about the source maps config causes problems for a simple create-react-app running in DEV mode. Column numbers are always reported as 0 (by 'source-maps') which causes the AST node matching to fail so hook names can't be located. We should really fix this, since a lot of people use create-react-app for prototyping.
Note that source maps work correctly in production builds.
Repro: https:/...

---

## Actual bucket: **3-7 days** (133 samples)

*Median absolute error: 1.0d, median relative error: 22%*

### Best 3 predictions (most accurate)

**rust-lang/rust #150725** — [aarch64-pc-windows-gnullvm] Can't build simple test app, fails with `rust-lld: error: undefined symbol: __chkstk`

- Actual: **5.4d** (129.9h, bucket: 3-7 days)
- Predicted: **5.4d** (129.9h, bucket: 3-7 days)
- Error: 0 min (0% off)
- Files changed: 1

> I created a new test application using `cargo new testapp`.
Using `nightly-2025-12-23-aarch64-pc-windows-gnullvm` with
```
[target.aarch64-pc-windows-gnullvm]
linker = "rust-lld"
```
in my `.cargo\config.toml`, I try to build my application via `cargo build`.
I'm reproducibly getting the error:
```
   Compiling testapp v0.1.0 (C:\Users\Colin Finck\testapp)
error: linking with `rust-lld` failed: ex...

**rust-lang/rust #146855** — rustdoc intra-doc link: cannot disambiguate between primitive and type alias

- Actual: **5.4d** (129.5h, bucket: 3-7 days)
- Predicted: **5.4d** (129.9h, bucket: 3-7 days)
- Error: 26 min (0% off)
- Files changed: 6

> <!--
Thank you for filing a bug report! 🐛 Please provide a short summary of the bug,
along with any information you feel relevant to replicating the bug.
-->
Related https://github.com/rust-lang/rust/issues/135897
After shadowing a **primitive** with a **type-alias**, it seems impossible to disambiguate a rustdoc link to the **type-alias**. Using the `type@` disambiguator does not help.
```rust
st...

**rust-lang/rust #153545** — E0716 without "let's call this" and spurious "requirement introduced here"

- Actual: **5.4d** (130.7h, bucket: 3-7 days)
- Predicted: **5.4d** (129.9h, bucket: 3-7 days)
- Error: 49 min (1% off)
- Files changed: 28

> Edit (2026-03-07T23:28:55+01:00): massively simplified code
### Code
```rust
use std::cell::RefCell;
use std::sync::Arc;
use std::collections::HashMap;
use std::collections::hash_map::Entry;
fn apply<'a>(
    f: Arc<dyn Fn(Entry<'a, String, String>) + 'a>,
) -> impl Fn(RefCell<HashMap<String, String>>)
{
    move |map| {
        let value = map.borrow_mut().entry("foo".to_string());
        let wr...

### Worst 3 predictions (least accurate)

**facebook/react #22705** — Timeline screenshots are sometimes way too small (depending on aspect ratio)

- Actual: **3.1d** (73.5h, bucket: 3-7 days)
- Predicted: **8.3d** (199.3h, bucket: 1-4 weeks)
- Error: 5.2d (171% off)
- Files changed: 9

> For example:
<img width="1904" alt="Screen Shot 2021-11-05 at 11 59 05 AM" src="https://user-images.githubusercontent.com/29597/140540816-25d6d47b-7aea-4121-aeaa-565accc65b1f.png">

**microsoft/vscode #237897** — Editor GPU: Support emoji

- Actual: **3.0d** (72.4h, bucket: 3-7 days)
- Predicted: **5.4d** (129.9h, bucket: 3-7 days)
- Error: 2.4d (79% off)
- Files changed: 1

> They currently show like this:
<img width="79" alt="Image" src="https://github.com/user-attachments/assets/c87bdf6f-7a1d-4ed1-bdd8-823b7f5ca63e" />

**microsoft/TypeScript #57693** — `null` gets accidentally eliminated when narrowing by undefined's equality

- Actual: **3.2d** (75.8h, bucket: 3-7 days)
- Predicted: **5.4d** (129.9h, bucket: 3-7 days)
- Error: 2.3d (71% off)
- Files changed: 4

> ### 🔎 Search Terms
null undefined narrow narrowing reduction equality narrowby
### 🕗 Version & Regression Information
- This is the behavior in every version I tried* 
*it worked differently in 5.1-5.3 because those had a bug in them ( https://github.com/microsoft/TypeScript/pull/57202 )
### ⏯ Playground Link
https://www.typescriptlang.org/play?ts=5.5.0-dev.20240308#code/C4TwDgpgBAggdiA8gIwFYQMbCg...

---

## Actual bucket: **1-4 weeks** (263 samples)

*Median absolute error: 9.6d, median relative error: 65%*

### Best 3 predictions (most accurate)

**kubernetes/kubernetes #128783** — [Failing Test] Container Runtime blackbox test on terminated container should report termination message if TerminationMessagePath is set as non-root user and at a non-default path [NodeConformance] [Conformance]

- Actual: **7.0d** (168.6h, bucket: 1-4 weeks)
- Predicted: **5.4d** (129.9h, bucket: 3-7 days)
- Error: 1.6d (23% off)
- Files changed: 8

> ### Which jobs are failing?
* sig-release-master-informing
* capz-windows-master
### Which tests are failing?
* [Container Runtime blackbox test on terminated container should report termination message if TerminationMessagePath is set as non-root user and at a non-default path [NodeConformance] [Conformance]](https://prow.k8s.io/view/gs/kubernetes-ci-logs/logs/ci-kubernetes-e2e-capz-master-window...

**microsoft/TypeScript #56856** — Declarations can't be emitted when types from inner modules are exported through separate export declarations

- Actual: **7.0d** (169.2h, bucket: 1-4 weeks)
- Predicted: **5.4d** (129.9h, bucket: 3-7 days)
- Error: 1.6d (23% off)
- Files changed: 9

> ### 🔎 Search Terms
declarations portable emit modules export declaration alias aliasing
### 🕗 Version & Regression Information
- This is the behavior in every version I tried
### ⏯ Playground Link
N/A
### 💻 Code
```ts
// @strict: true
// @declaration: true
// @module: nodenext
// @moduleResolution: nodenext
// @target: esnext
// @filename: node_modules/@tanstack/vue-query/build/modern/useQuery-CPq...

**microsoft/vscode #241832** — Comments panel appears without having GHPR installed

- Actual: **7.1d** (169.9h, bucket: 1-4 weeks)
- Predicted: **5.4d** (129.9h, bucket: 3-7 days)
- Error: 1.7d (24% off)
- Files changed: 2

> From a fresh install with Copilot, I see the "Comments" panel after having opened `vscode` repo:
<img width="775" alt="Image" src="https://github.com/user-attachments/assets/56da8fb5-b113-4fd8-9a8e-1e733e6d42f2" />
I think I would only expect the comments panel to appear if:
* there are comments
* I am in a PR review where I can leave comments

### Worst 3 predictions (least accurate)

**facebook/react #20905** — Redundant condition in react-devtools-shared

- Actual: **3.6w** (602.6h, bucket: 1-4 weeks)
- Predicted: **3.0d** (72.6h, bucket: 3-7 days)
- Error: 3.2w (88% off)
- Files changed: 1

> This is not important but it seems that this if statement is superfluous since `typeof` always returns a string. 
https://github.com/facebook/react/blob/553440bd1578ef71982c4a10e2cc8c462f33d9be/packages/react-devtools-shared/src/hydration.js#L246

**facebook/react #7430** — `HTMLDOMPropertyConfig` contains non-standard `icon` property

- Actual: **3.5w** (591.3h, bucket: 1-4 weeks)
- Predicted: **3.0d** (72.6h, bucket: 3-7 days)
- Error: 3.1w (88% off)
- Files changed: 1

> **Do you want to request a _feature_ or report a _bug_?**
Report a bug.
**What is the current behavior?**
The `HTMLDOMPropertyConfig` object [includes an `icon` property](https://github.com/facebook/react/blob/cccef3c68310df3bd611df2a7b98a530645c67c0/src/renderers/dom/shared/HTMLDOMPropertyConfig.js#L85) in a section title `Standard Properties`, but `icon` isn’t an attribute supported by any stand...

**facebook/react #20806** — Bug: devtools reload-and-profile feature is defeated by sync-xhr feature policy

- Actual: **4.0w** (668.5h, bucket: 1-4 weeks)
- Predicted: **3.5d** (83.6h, bucket: 3-7 days)
- Error: 3.5w (87% off)
- Files changed: 4

> React version: all
## Steps To Reproduce
1. Visit a site that uses `Feature-Policy: sync-xhr 'none'` and has the profiling build of react enabled
2. Attempt to use the "reload and start profiling" feature of devtools
3. The xhr request will fail on reload because it [attempts to make a synchronous XHR call](https://github.com/facebook/react/blob/9198a5cec0936a21a5ba194a22fcbac03eba5d1d/packages/re...

---

## Actual bucket: **> 4 weeks** (167 samples)

*Median absolute error: 6.5w, median relative error: 90%*

### Best 3 predictions (most accurate)

**microsoft/TypeScript #57924** — [ServerErrors][JavaScript] 5.5.0-dev.20240324

- Actual: **4.3w** (720.2h, bucket: > 4 weeks)
- Predicted: **5.4d** (129.9h, bucket: 3-7 days)
- Error: 3.5w (82% off)
- Files changed: 2

> The following errors were reported by 5.5.0-dev.20240324
[Pipeline that generated this bug](https://typescript.visualstudio.com/TypeScript/_build?definitionId=48)
[Logs for the pipeline run](https://typescript.visualstudio.com/TypeScript/_build/results?buildId=160709)
[File that generated the pipeline](https://github.com/microsoft/typescript-error-deltas/blob/main/azure-pipelines-gitTests.yml)
Thi...

**microsoft/TypeScript #51845** — No JSX attributes snippets after curly

- Actual: **4.3w** (729.8h, bucket: > 4 weeks)
- Predicted: **5.4d** (129.9h, bucket: 3-7 days)
- Error: 3.6w (82% off)
- Files changed: 2

> # Bug Report
<!--
  Please fill in each section completely. Thank you!
-->
### 🔎 Search Terms
React, JSX attributes snippets, VSCode VS Code
<!--
  What search terms did you use when trying to find an existing bug report?
  List them here so people in the future can find this one more easily.
-->
### 🕗 Version & Regression Information
4.9
<!-- When did you start seeing this bug occur?
"Bugs" that...

**rust-lang/rust #153158** — `Vec`'s const_make_global method erroring when `Vec` is empty

- Actual: **4.3w** (730.6h, bucket: > 4 weeks)
- Predicted: **5.4d** (129.9h, bucket: 3-7 days)
- Error: 3.6w (82% off)
- Files changed: 9

> I tried this code:
```rust
#![feature(const_heap)]
fn main() {
    const {
        let mut inner_vec = Vec::<i32>::new();
        let inner_slice = inner_vec.const_make_global();
    }
}
```
I expected `const_make_global()` to just return an empty `'static` slice
Instead, it gave me this error:
```
error[E0080]: pointer not dereferenceable: pointer must point to some allocation, but got 0x4[noallo...

### Worst 3 predictions (least accurate)

**facebook/react #31422** — [DevTools Bug]: Copy to clipboard doesn't work

- Actual: **10.2w** (1707.6h, bucket: > 4 weeks)
- Predicted: **2.9d** (69.7h, bucket: 1-3 days)
- Error: 9.7w (96% off)
- Files changed: 3

> ### Website or app
https://www.arbounie.nl/
### Repro steps
1. Open the devtools to the Components tab
2. Select a component. I used the first Context.Provider, but I suspect it doesn't matter.
3. In the `props` panel, click the top-right "copy to clipboard" icon.
4. Observe what gets put into the clipboard.
### How often does this bug happen?
Every time
### DevTools package (automated)
_No respon...

**facebook/react #791** — Link to React devtools in official docs

- Actual: **9.6w** (1618.4h, bucket: > 4 weeks)
- Predicted: **3.0d** (72.6h, bucket: 3-7 days)
- Error: 9.2w (96% off)
- Files changed: 1

> I don't know where the right place to link to them is. Maybe "Getting started", "Tutorial" and "Tooling integration"?

**facebook/react #17935** — Bug: Excessive cpu usage of the page when react-devtools is active

- Actual: **9.6w** (1613.0h, bucket: > 4 weeks)
- Predicted: **3.0d** (72.6h, bucket: 3-7 days)
- Error: 9.2w (95% off)
- Files changed: 1

> When option "Highlight updates when components render" is activated the whole page repaints in rapid succession after the components state has been changed. It causes 100% CPU usage by the browser and unpleasant DX due low fps.
React version: 16.12.0
DevTools version 4.4.0-f749045a5
The sequance of actions is important:
1. Open react application
2. Open react-devtools
3. Check option "Highlight up...

---
