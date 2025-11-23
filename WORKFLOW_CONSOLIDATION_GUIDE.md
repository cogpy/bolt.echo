# Workflow Consolidation Guide

## Background

Due to GitHub App permissions restrictions, the automated consolidation of deployment workflows could not be completed. This guide provides manual steps to complete the workflow consolidation.

## Current Situation

The repository currently has **three deployment workflows** that trigger on the same event (push to main):

1. `.github/workflows/deploy-pages.yml` - Full deployment with project creation
2. `.github/workflows/wrangler-deploy-pages.yml` - Simplified deployment (RECOMMENDED)
3. `.github/workflows/deploy.yml` - Additional deployment workflow

Having multiple workflows triggering on the same event can cause:
- Duplicate deployments
- Race conditions
- Confusion about which workflow is authoritative
- Wasted CI/CD resources

## Recommended Action

**Keep only `wrangler-deploy-pages.yml` as the primary deployment workflow.**

### Option 1: Disable Workflows via GitHub UI (Recommended)

1. Go to: https://github.com/cogpy/bolt.echo/actions
2. Click on "Deploy Cloudflare Pages" workflow
3. Click the "..." menu (top right)
4. Select "Disable workflow"
5. Repeat for "Deploy to Cloudflare" workflow

This keeps the files but prevents them from running.

### Option 2: Rename Workflow Files

Manually rename the files to disable them:

```bash
cd .github/workflows/
mv deploy-pages.yml deploy-pages.yml.disabled
mv deploy.yml deploy.yml.disabled
```

Then commit and push:

```bash
git add .github/workflows/
git commit -m "chore: Disable redundant deployment workflows"
git push origin main
```

**Note:** This requires the `workflows` permission which may not be available to all users.

### Option 3: Delete Redundant Workflows

If you're certain you won't need these workflows:

```bash
cd .github/workflows/
git rm deploy-pages.yml deploy.yml
git commit -m "chore: Remove redundant deployment workflows"
git push origin main
```

## Active Workflow

After consolidation, only this workflow should be active:

**`.github/workflows/wrangler-deploy-pages.yml`**

This workflow:
- ✅ Uses the latest Wrangler v4
- ✅ Properly sets up Node.js 20 and pnpm 9.4.0
- ✅ Runs the correct build command
- ✅ Deploys to Cloudflare Pages
- ✅ Has minimal configuration and clear steps

## Verification

After disabling/removing the redundant workflows:

1. Go to: https://github.com/cogpy/bolt.echo/actions
2. Verify only "Deploy Cloudflare Pages with Wrangler" appears in the workflow list
3. Make a test commit to main branch
4. Verify only one deployment runs

## Troubleshooting

### "Workflow not found" Error

If you get this error after disabling workflows, it's expected. The workflow files still exist but are disabled.

### Multiple Deployments Still Running

Check that all redundant workflows are properly disabled in the GitHub Actions UI.

### Need to Re-enable a Workflow

1. Go to: https://github.com/cogpy/bolt.echo/actions
2. Find the disabled workflow
3. Click "Enable workflow"

## Summary

**Immediate Action Required:**
- Choose one of the three options above to consolidate workflows
- Recommended: Use Option 1 (disable via GitHub UI) for safety

**Expected Result:**
- Single deployment workflow running on push to main
- Cleaner CI/CD pipeline
- No duplicate deployments

---

For questions or issues, refer to the main [CLOUDFLARE_SETUP.md](./CLOUDFLARE_SETUP.md) documentation.
