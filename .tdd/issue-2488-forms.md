# Workflow forms for #2488 — the exit the runs-on-pull-requests predicate must produce

Reconstructed from the review of d6ca06c90 (51 forms driven through `main()` with `gh` faked). `expected_exit` is what the design must produce; `today` is what d6ca06c90 produced. Notes starting "FLAGGED:" are the ten forms that reached exit 4 where 3 is right. `gs_marketplace_real` is ps-mutuus/gs-marketplace's `.github/workflows` at 4956044d0.

```json
[
 {
  "name": "scalar",
  "files": {
   "a.yml": "on: pull_request\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "scalar trigger"
 },
 {
  "name": "flow_list",
  "files": {
   "a.yml": "on: [push, pull_request]\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "flow sequence of events"
 },
 {
  "name": "block_list",
  "files": {
   "a.yml": "on:\n  - push\n  - pull_request\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "block sequence of events"
 },
 {
  "name": "flow_map",
  "files": {
   "a.yml": "on: {push: {}, pull_request: {}}\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "flow mapping of events"
 },
 {
  "name": "dq_on",
  "files": {
   "a.yml": "\"on\":\n  pull_request:\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "double-quoted on key"
 },
 {
  "name": "sq_on",
  "files": {
   "a.yml": "'on':\n  pull_request:\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "single-quoted on key"
 },
 {
  "name": "true_key",
  "files": {
   "a.yml": "true:\n  pull_request:\n"
  },
  "expected_exit": 4,
  "today": 4,
  "note": "true: is not GitHub's on key; no trigger"
 },
 {
  "name": "quoted_pr_key_closed",
  "files": {
   "a.yml": "on:\n  'pull_request':\n    types: [closed]\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "conservative"
 },
 {
  "name": "comment_after_key",
  "files": {
   "a.yml": "on:\n  pull_request: # types: [closed]\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "types only in a comment; default types fire"
 },
 {
  "name": "comment_in_types",
  "files": {
   "a.yml": "on:\n  pull_request:\n    types: [closed] # opened later\n"
  },
  "expected_exit": 4,
  "today": 4,
  "note": "opened only in a comment"
 },
 {
  "name": "if_mention_only",
  "files": {
   "a.yml": "on: push\njobs:\n  x:\n    if: github.event_name == 'pull_request'\n"
  },
  "expected_exit": 4,
  "today": 4,
  "note": "pull_request only in a job if:"
 },
 {
  "name": "anchor_types_alias",
  "files": {
   "a.yml": "on:\n  issues:\n    types: &t [opened]\n  pull_request:\n    types: *t\n"
  },
  "expected_exit": 3,
  "today": 4,
  "note": "FLAGGED: types aliased to an anchor naming opened"
 },
 {
  "name": "merge_key",
  "files": {
   "a.yml": "on:\n  pull_request:\n    <<: *x\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "merge key, no literal types"
 },
 {
  "name": "multidoc_leading",
  "files": {
   "a.yml": "---\non:\n  pull_request:\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "leading document marker"
 },
 {
  "name": "crlf_opened",
  "files": {
   "a.yml": "on:\r\n  pull_request:\r\n    types: [opened]\r\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "CRLF line endings"
 },
 {
  "name": "crlf_closed",
  "files": {
   "a.yml": "on:\r\n  pull_request:\r\n    types: [closed]\r\n"
  },
  "expected_exit": 4,
  "today": 4,
  "note": "CRLF, closed only"
 },
 {
  "name": "indent4",
  "files": {
   "a.yml": "on:\n    pull_request:\n        types:\n        - opened\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "4-space indent, block types"
 },
 {
  "name": "types_block_same_indent",
  "files": {
   "a.yml": "on:\n  pull_request:\n    types:\n    - closed\n    - opened\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "block list at types' own indent"
 },
 {
  "name": "types_block_comment_gap",
  "files": {
   "a.yml": "on:\n  pull_request:\n    types:\n      - closed\n      # x\n\n      - opened\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "comment and blank line inside block list"
 },
 {
  "name": "types_scalar",
  "files": {
   "a.yml": "on:\n  pull_request:\n    types: opened\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "scalar types"
 },
 {
  "name": "types_quoted",
  "files": {
   "a.yml": "on:\n  pull_request:\n    types: ['opened']\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "quoted type name"
 },
 {
  "name": "types_multiline_flow",
  "files": {
   "a.yml": "on:\n  pull_request:\n    types: [closed,\n      opened]\n"
  },
  "expected_exit": 3,
  "today": 4,
  "note": "FLAGGED: flow list continued on the next line"
 },
 {
  "name": "types_flow_next_line",
  "files": {
   "a.yml": "on:\n  pull_request:\n    types:\n      [opened]\n"
  },
  "expected_exit": 3,
  "today": 4,
  "note": "FLAGGED: flow list on the line after types:"
 },
 {
  "name": "types_on_other_trigger",
  "files": {
   "a.yml": "on:\n  pull_request:\n  issues:\n    types: [closed]\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "types belongs to issues, not pull_request"
 },
 {
  "name": "flow_null_then_types",
  "files": {
   "a.yml": "on: {pull_request: null, issues: {types: [closed]}}\n"
  },
  "expected_exit": 3,
  "today": 4,
  "note": "FLAGGED: sibling trigger's types read as pull_request's"
 },
 {
  "name": "flow_empty_then_types",
  "files": {
   "a.yml": "on: {pull_request: , issues: {types: [closed]}}\n"
  },
  "expected_exit": 3,
  "today": 4,
  "note": "FLAGGED: same, empty value"
 },
 {
  "name": "flow_multiline_root_on",
  "files": {
   "a.yml": "on: {\n  pull_request: {types: [closed]},\n  pull_request_target: {}\n}\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "multi-line flow on map"
 },
 {
  "name": "filters_only",
  "files": {
   "a.yml": "on:\n  pull_request:\n    branches: [main]\n    paths: ['src/**']\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "branches/paths filters, default types"
 },
 {
  "name": "paths_contains_types_colon",
  "files": {
   "a.yml": "on:\n  pull_request:\n    paths: ['docs/types:old/**']\n"
  },
  "expected_exit": 3,
  "today": 4,
  "note": "FLAGGED: types: matched inside a path string"
 },
 {
  "name": "uppercase_on",
  "files": {
   "a.yml": "On:\n  pull_request:\n"
  },
  "expected_exit": 4,
  "today": 4,
  "note": "On: is not GitHub's on key; no trigger"
 },
 {
  "name": "trailing_spaces",
  "files": {
   "a.yml": "on:   \n  pull_request:   \n    types: [ opened ]   \n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "trailing spaces"
 },
 {
  "name": "tab_after_colon",
  "files": {
   "a.yml": "on:\tpull_request\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "tab separator"
 },
 {
  "name": "indented_root",
  "files": {
   "a.yml": "  name: x\n  on:\n    pull_request:\n"
  },
  "expected_exit": 3,
  "today": 4,
  "note": "FLAGGED: root mapping indented 2 spaces"
 },
 {
  "name": "json_root",
  "files": {
   "a.yml": "{\"on\": {\"pull_request\": {}}, \"jobs\": {}}\n"
  },
  "expected_exit": 3,
  "today": 4,
  "note": "FLAGGED: JSON document"
 },
 {
  "name": "flow_root_yaml",
  "files": {
   "a.yml": "{on: pull_request, jobs: {}}\n"
  },
  "expected_exit": 3,
  "today": 4,
  "note": "FLAGGED: flow-mapping root"
 },
 {
  "name": "multiline_dq_name",
  "files": {
   "a.yml": "name: \"x\non: push\"\non:\n  pull_request:\n"
  },
  "expected_exit": 3,
  "today": 4,
  "note": "FLAGGED: on: inside a multi-line quoted scalar matched first"
 },
 {
  "name": "block_scalar_before",
  "files": {
   "a.yml": "name: >-\n  on: push\non:\n  pull_request:\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "indented on: inside a block scalar"
 },
 {
  "name": "yaml_ext",
  "files": {
   "a.yaml": "on:\n  pull_request:\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": ".yaml extension"
 },
 {
  "name": "readme_plus_push",
  "files": {
   "README.md": "# on: pull_request docs\n",
   "a.yml": "on: push\n"
  },
  "expected_exit": 4,
  "today": 4,
  "note": "README mention plus push-only workflow"
 },
 {
  "name": "readme_only",
  "files": {
   "README.md": "Workflows here.\n"
  },
  "expected_exit": 4,
  "today": 4,
  "note": "README contributes nothing"
 },
 {
  "name": "empty_file",
  "files": {
   "a.yml": ""
  },
  "expected_exit": 4,
  "today": 4,
  "note": "empty body, no on: region"
 },
 {
  "name": "large",
  "files": {
   "a.yml": "GENERATED: 'name: x\\n' + '# pad\\n' * 200000 + 'on:\\n  pull_request:\\n'"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "~1.2 MB file, trigger at the end; body generated in the test, not stored here"
 },
 {
  "name": "pr_review_only",
  "files": {
   "a.yml": "on:\n  pull_request_review:\n"
  },
  "expected_exit": 3,
  "today": 3,
  "note": "conservative"
 },
 {
  "name": "listing_subdir",
  "listing": "[{\"path\": \".github/workflows/sub\", \"type\": \"dir\"}, {\"path\": \".github/workflows/a.yml\", \"type\": \"file\"}]",
  "expected_exit": 3,
  "today": 3,
  "note": "listing with a dir entry (whose raw read returns a JSON listing) plus a.yml = on: pull_request"
 },
 {
  "name": "listing_dict",
  "listing": "{\"path\": \".github/workflows\", \"type\": \"file\"}",
  "expected_exit": 3,
  "today": 2,
  "note": "listing is an object (workflows is a file); uncaught TypeError"
 },
 {
  "name": "listing_null",
  "listing": "null",
  "expected_exit": 3,
  "today": 2,
  "note": "listing is null; uncaught TypeError"
 },
 {
  "name": "listing_entry_no_path",
  "listing": "[{\"name\": \"a.yml\"}]",
  "expected_exit": 3,
  "today": 2,
  "note": "entry lacks path; uncaught KeyError"
 },
 {
  "name": "listing_empty",
  "listing": "[]",
  "expected_exit": 4,
  "today": 4,
  "note": "empty workflows directory"
 },
 {
  "name": "listing_404",
  "listing": {
   "exit": 1,
   "stdout": "{\"message\":\"Not Found\"}\n",
   "stderr": "gh: Not Found (HTTP 404)\n"
  },
  "expected_exit": 4,
  "today": 4,
  "note": "workflows directory absent"
 },
 {
  "name": "listing_403_json",
  "listing": {
   "exit": 1,
   "stdout": "{\"message\":\"Resource not accessible\"}",
   "stderr": ""
  },
  "expected_exit": 3,
  "today": 3,
  "note": "non-404 JSON error body"
 },
 {
  "name": "gs_marketplace_real",
  "files": {
   "ci.yml": "name: CI\n\n# Runs only after a merge to main (veri verifies on the branch locally).\non:\n  push:\n    branches: [main]\n\nconcurrency:\n  group: ci-${{ github.ref }}\n  cancel-in-progress: true\n\njobs:\n  check:\n    runs-on: ubuntu-latest\n    timeout-minutes: 15\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-node@v4\n        with:\n          node-version: 22\n          cache: npm\n      - run: npm ci\n      - run: npm ci --prefix infra\n      - run: npm run lint\n      - run: npm run typecheck\n      - run: npm test\n      - run: npm run build\n      - run: npm run build:admin\n      - run: node scripts/check-dist-dev-tools.mjs dist\n      - run: npm run test:infra\n\n  e2e:\n    runs-on: ubuntu-latest\n    timeout-minutes: 15\n    needs: check\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-node@v4\n        with:\n          node-version: 22\n          cache: npm\n      - run: npm ci\n      - run: npm ci --prefix infra\n      - run: npx playwright install --with-deps chromium\n      - run: npm run test:e2e\n      - uses: actions/upload-artifact@v4\n        if: failure()\n        with:\n          name: playwright-report\n          path: playwright-report\n          retention-days: 7\n",
   "deploy.yml": "name: Deploy\n\non:\n  pull_request:\n    types: [closed]\n    branches: [main]\n  workflow_dispatch:\n\npermissions:\n  id-token: write\n  contents: read\n\n# One deploy at a time: a second CloudFormation update on the same stack fails while the first runs.\n# Queued, not cancelled, so every deploy-labelled merge still deploys.\nconcurrency:\n  group: deploy-${{ github.workflow }}\n  cancel-in-progress: false\n\njobs:\n  dev:\n    if: github.event.pull_request.merged && contains(github.event.pull_request.labels.*.name, 'deploy')\n    runs-on: ubuntu-latest\n    timeout-minutes: 15\n    steps:\n      - uses: actions/checkout@v4\n        with:\n          ref: ${{ github.event.pull_request.merge_commit_sha }}\n      - name: Require AWS_DEPLOY_ROLE_ARN\n        env:\n          AWS_DEPLOY_ROLE_ARN: ${{ vars.AWS_DEPLOY_ROLE_ARN }}\n        run: |\n          if [ -z \"$AWS_DEPLOY_ROLE_ARN\" ]; then\n            echo \"::error::Repo variable AWS_DEPLOY_ROLE_ARN is not set\"\n            exit 1\n          fi\n      - uses: aws-actions/configure-aws-credentials@v4\n        with:\n          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}\n          aws-region: us-east-1\n      - name: Build dev bundle\n        env:\n          VITE_DEV_TOOLS: \"true\"\n          VITE_ALLOW_REJECTED_RETRY: \"true\"\n          VITE_SERVICES: core\n          VITE_CORE_API_BASE: https://devmutuusservices2.azurewebsites.net/api\n          VITE_TERCEROS_API_BASE: https://mutuustercerosdev.azurewebsites.net/api\n          VITE_CORE_EXTENSIONS_BASE: https://api.core-extensions.mutuus.click\n          VITE_HOS_PROMO_CODE: GRUPOSALINASTECUIDA2099\n          VITE_HOS_CLAVE_AGENTE: A-0001\n          VITE_HOS_FORMA_PAGO_TARJETA: Anual\n          VITE_HOS_TARJETA: \"false\"\n          VITE_CORE_EXTENSIONS_API_KEY: ${{ secrets.CORE_EXTENSIONS_API_KEY }}\n          VITE_BACKEND_BASE: https://api.gstecuida.mutuus.click\n          VITE_BACKEND_API_KEY: ${{ secrets.VITE_BACKEND_API_KEY }}\n        run: |\n          npm ci\n          npm ci --prefix infra\n          npm run build\n          npm run build:admin\n      - name: Deploy BackendStack-dev\n        working-directory: infra\n        run: |\n          npm ci\n          npx cdk deploy BackendStack-dev --require-approval never\n      - name: Deploy StaticSiteStack-dev\n        working-directory: infra\n        run: |\n          npm ci\n          npx cdk deploy StaticSiteStack-dev --require-approval never\n      - name: Deploy AdminSiteStack-dev\n        working-directory: infra\n        run: |\n          npm ci\n          npx cdk deploy AdminSiteStack-dev --require-approval never\n  prod:\n    if: github.event_name == 'workflow_dispatch'\n    runs-on: ubuntu-latest\n    timeout-minutes: 15\n    steps:\n      - uses: actions/checkout@v4\n      - name: Require a prod domain\n        working-directory: infra\n        run: |\n          if ! grep -Eq '\"certificateArn\": *\"arn:' config/prod.json; then\n            echo \"::error::infra/config/prod.json has no domain with a certificateArn\"\n            exit 1\n          fi\n      - uses: aws-actions/configure-aws-credentials@v4\n        with:\n          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}\n          aws-region: us-east-1\n      - name: Build prod bundle\n        run: |\n          npm ci\n          npm ci --prefix infra\n          npm run build\n          npm run build:admin\n      - name: Deploy StaticSiteStack-prod\n        working-directory: infra\n        run: |\n          npm ci\n          npx cdk deploy StaticSiteStack-prod --require-approval never\n      - name: Deploy AdminSiteStack-prod\n        working-directory: infra\n        run: |\n          npm ci\n          npx cdk deploy AdminSiteStack-prod --require-approval never\n"
  },
  "expected_exit": 4,
  "today": 4,
  "note": "ps-mutuus/gs-marketplace @4956044d0: push-only ci, pull_request types [closed] deploy (today via runs_on_pull_requests, not main())"
 }
]
```
