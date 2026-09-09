# basic-ai-agent

A minimal FastAPI service that wraps Azure OpenAI chat completions, built to
demonstrate a "build once, deploy many times" Docker + Helm + ArgoCD release
pipeline through JFrog Artifactory.

## Local development

```bash
cp .env.example .env   # fill in AZURE_OPENAI_* values
make install
make test
uvicorn app.main:app --reload
```

`POST /chat {"message": "hi"}` returns `{"reply": "..."}`. `/healthz` and
`/readyz` are liveness/readiness endpoints.

## Architecture

Two repos:

- **This repo** (`basic-ai-agent`): application code, Dockerfile, CI/CD
  workflows, and the `Makefile` used to cut releases.
- **`cloudutsukpilot/basic-ai-agent-apps`**: the GitOps repo. Holds the Helm
  chart (`charts/basic-ai-agent`) and per-environment values
  (`environments/{dev,staging,prod}/values.yaml`). ArgoCD watches this repo
  only.

## Release flow (build once, deploy many)

1. **PR merges to `main`** → `build-and-push.yml` builds the Docker image
   exactly once and pushes it to JFrog tagged `sha-<gitsha>`.
2. **`make tag VERSION=1.2.3`** creates and pushes git tag `v1.2.3`. This
   triggers `release.yml`, which:
   - **promotes** (never rebuilds) the existing `sha-<gitsha>` image to
     `v1.2.3` and `latest` via `docker buildx imagetools create` (a
     manifest/tag copy inside the registry, no re-pull/re-push of layers),
   - packages the Helm chart from the apps repo, bumps `Chart.yaml`, and
     pushes it to JFrog's Helm OCI repo,
   - opens a PR on the apps repo bumping `environments/dev/values.yaml` to
     the new image tag and chart version.
3. **Merging that PR** lets ArgoCD sync `dev` with the new version.
4. **`make promote ENV=staging VERSION=v1.2.3`** (or `ENV=production`) runs
   `promote.yml`, gated by the `staging`/`production` GitHub Environment's
   required reviewers. Once approved, it opens a PR on the apps repo
   bumping that environment's values to the *same already-built* version.
   Merging it lets ArgoCD sync that environment.

No step after the initial build ever rebuilds the image or repackages the
chart from source — every later stage promotes the exact artifact produced
in step 1.

## Makefile

```
make install   # dev dependencies
make lint      # ruff
make test      # pytest
make build     # docker build, tagged with current git sha
make push      # push the sha-tagged image to JFrog
make pr        # push current branch + open a PR into main (gh CLI)
make tag VERSION=1.2.3                    # cut a release
make promote ENV=staging VERSION=v1.2.3   # request approval-gated promotion
```

## Required repository configuration

**Variables** (Settings → Secrets and variables → Actions → Variables):

| Name | Example | Purpose |
|---|---|---|
| `JFROG_DOCKER_REGISTRY` | `mycompany.jfrog.io/docker-local` | Docker push target |
| `JFROG_URL_HOST` | `mycompany.jfrog.io` | Host used for `helm registry login` |
| `JFROG_HELM_REPO` | `helm-oci-local` | OCI repo key charts are pushed to |
| `APPS_REPO` | `cloudutsukpilot/basic-ai-agent-apps` | GitOps repo `owner/name` |

**Secrets**:

| Name | Purpose |
|---|---|
| `JFROG_USER` / `JFROG_TOKEN` | JFrog Artifactory credentials |
| `APPS_REPO_TOKEN` | PAT (or GitHub App token) with `contents:write`/`pull-requests:write` on the apps repo — the default `GITHUB_TOKEN` can't push to a different repository |

**GitHub Environments** (Settings → Environments): create `staging` and
`production`, each with required reviewers configured. `promote.yml`'s job
runs under `environment: ${{ inputs.environment }}`, so it blocks on that
environment's approval before opening the promotion PR.

## Azure OpenAI configuration

The app reads these environment variables (see `.env.example`):
`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`,
`AZURE_OPENAI_API_VERSION`. In cluster these are injected via the Helm
chart's Secret/ConfigMap (see the apps repo).
