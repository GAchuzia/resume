# Updating and releasing the resume

## Update the PDF and preview

1. Edit the LaTeX sections in `src/` on a branch, then commit and push your changes.
2. Merge the branch into `main`.
3. Wait for **Update Resume PDF and Preview** in [GitHub Actions](https://github.com/GAchuzia/resume/actions) to finish.

When `src/` changes reach `main` or `master`, `.github/workflows/update_readme_resume.yml` builds the PDF, checks that it is one page and contains your email, generates the preview, and commits both files:

- `build/Resume_GrantAchuzia.pdf`
- `images/resume.png`

Pushing a feature branch alone does not run this workflow.

## Publish a versioned PDF

There is no version file to edit. A Git tag names each release.

After merging and waiting for the PDF/preview update:

```sh
cd ~/personal/resume
git switch main
git pull --ff-only
git fetch origin --tags
git tag --sort=-version:refname
```

Choose an unused version. For example, if the latest is `v5.3.0`, publish `v5.3.1`:

```sh
git tag v5.3.1
git push origin v5.3.1
```

Pushing a `vX.Y.Z` tag triggers **Auto Release Resume** (`.github/workflows/auto_release.yml`). It builds the tagged source and creates a [GitHub Release](https://github.com/GAchuzia/resume/releases) with the PDF attached.

The tag always points to the current commit. You can also release an approved feature branch by checking it out before tagging; this does not merge it into `main` or update the PDF/preview on `main`. The release workflow builds the PDF directly from that branch's tagged source.

Check both workflows in GitHub Actions. If a release fails, inspect the failed run before creating another tag; do not move or reuse published version tags.

## Build

With TeX Live (including `latexmk`) installed, run from the repository root:

```sh
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error \
  -jobname=Resume_GrantAchuzia -outdir=../build src/resume.tex
```

The PDF is written to `build/Resume_GrantAchuzia.pdf`. Edit the sections in `src/`;
VS Code's LaTeX Workshop uses the same output name. On `main`, GitHub Actions
rebuilds the PDF and preview together. Pushing a `vX.Y.Z` tag creates a PDF release.
See [Updating and releasing the resume](docs/releases.md) for the steps.

## Preview
