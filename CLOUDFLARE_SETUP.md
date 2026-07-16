# Cloudflare Pages Deployment Setup

## Overview

This repository is configured to deploy to **Cloudflare Pages** with the following architecture:

- **Frontend**: Static assets served by Cloudflare Pages
- **Backend**: Remix SSR handled by Cloudflare Pages Functions
- **Build Output**: `build/client` (frontend) and `build/server` (backend)
- **Project Name**: `boltecho`

## Prerequisites

1. **Cloudflare Account** with Pages enabled
2. **API Tokens** with the following permissions:
   - Account > Cloudflare Pages > Edit
   - Account > Workers Scripts > Edit
3. **API Keys** for external services:
   - Anthropic API key (required)
   - OpenAI API key (optional)

## Local Development Setup

### 1. Install Dependencies

```bash
# Ensure you have Node.js 20+ and pnpm 9.4.0
corepack enable
pnpm install --frozen-lockfile
```

### 2. Configure Environment Variables

```bash
# Copy the example file
cp .dev.vars.example .dev.vars

# Edit .dev.vars and add your API keys
# ANTHROPIC_API_KEY=your_key_here
# VITE_LOG_LEVEL=debug
```

### 3. Local Development Server

```bash
# Run the development server
pnpm run dev

# Or run with Cloudflare Pages emulation
pnpm run preview
```

## Cloudflare Pages Configuration

### Environment Variables

Set these in the Cloudflare Pages dashboard:

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Navigate to: **Pages** > **boltecho** > **Settings** > **Environment variables**
3. Add the following variables:

| Variable | Value | Environment |
|----------|-------|-------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Production & Preview |
| `VITE_LOG_LEVEL` | `info` or `debug` | Production & Preview |
| `OPENAI_API_KEY` | Your OpenAI API key (optional) | Production & Preview |

### Build Configuration

The build is configured in `.cloudflare/pages.toml`:

```toml
[build]
command = "corepack enable && pnpm install --frozen-lockfile && pnpm run build:pages"
output_directory = "build/client"
base_directory = "."
root_directory = "."
```

**Build Settings in Cloudflare Dashboard:**
- Framework preset: **None** (custom Remix configuration)
- Build command: (use the command from pages.toml)
- Build output directory: `build/client`
- Root directory: `/`
- Node.js version: `20`

## Deployment Methods

### Method 1: GitHub Actions (Recommended)

The repository uses `wrangler-deploy-pages.yml` workflow that:
- Triggers on push to `main` branch
- Can be manually triggered via workflow_dispatch
- Builds and deploys automatically

**Setup:**
1. Add secrets to your GitHub repository:
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_ACCOUNT_ID`
   - `ANTHROPIC_API_KEY` (optional, for build-time usage)
   - `OPENAI_API_KEY` (optional)

2. Push to main branch:
```bash
git push origin main
```

### Method 2: Manual CLI Deployment

```bash
# Authenticate with Cloudflare (one-time)
npx wrangler login

# Build and deploy
pnpm run deploy

# Or deploy a specific branch
wrangler pages deploy build/client --project-name boltecho --branch preview
```

### Method 3: Cloudflare Dashboard

1. Connect your GitHub repository in Cloudflare Pages
2. Configure build settings as described above
3. Deployments will trigger automatically on push

## Project Structure

```
bolt.echo/
├── .cloudflare/
│   └── pages.toml              # Cloudflare Pages build config
├── .github/
│   └── workflows/
│       └── wrangler-deploy-pages.yml  # Primary deployment workflow
├── app/                        # Remix application source
├── build/
│   ├── client/                 # Frontend build output (deployed)
│   └── server/                 # Backend build output (used by Functions)
├── functions/
│   └── [[path]].ts            # Cloudflare Pages Functions handler
├── public/                     # Static assets
├── .dev.vars.example          # Environment variables template
├── wrangler.toml              # Cloudflare configuration
├── package.json               # Dependencies and scripts
└── vite.config.ts             # Vite build configuration
```

## Build Scripts

| Script | Description |
|--------|-------------|
| `pnpm run dev` | Start development server |
| `pnpm run build` | Build for production |
| `pnpm run build:pages` | Build specifically for Cloudflare Pages |
| `pnpm run deploy` | Build and deploy to Cloudflare Pages |
| `pnpm run preview` | Preview production build locally |
| `pnpm run start` | Start local Cloudflare Pages dev server |

## Troubleshooting

### Build Fails with "pnpm not found"

**Solution:** Ensure `corepack enable` is in the build command and Node.js 20+ is selected.

### "Missing entry-point" Error

**Solution:** Update Wrangler to v4.27.0 or later:
```bash
pnpm add -D wrangler@latest
```

### 404 Errors on Deployed Site

**Possible causes:**
1. Environment variables not set in Cloudflare Pages dashboard
2. Build output directory incorrect
3. Functions handler not properly configured

**Solution:** Verify all environment variables are set and build output exists in `build/client`.

### Deployment Fails with 403 Unauthorized

**Solution:** Regenerate your Cloudflare API token with the correct permissions:
- Account > Cloudflare Pages > Edit
- Account > Workers Scripts > Edit

### Large Bundle Size Warnings

**Current status:** Known issue, does not block deployment.

**Future optimization:** Implement code splitting and dynamic imports.

## Database Configuration (Optional)

If you need D1 database support:

1. Create a D1 database:
```bash
wrangler d1 create boltecho-db
```

2. Update `wrangler.toml`:
```toml
[[pages_plugins]]
binding = "DB"
plugin_type = "D1"
database_id = "your-database-id-here"
```

3. Run migrations:
```bash
wrangler d1 migrations apply boltecho-db
```

## Monitoring and Logs

### View Deployment Logs
- Cloudflare Dashboard > Pages > boltecho > Deployments
- Click on any deployment to see build logs

### View Runtime Logs
- Cloudflare Dashboard > Pages > boltecho > Functions
- Use `wrangler pages deployment tail` for real-time logs

### Analytics
- Enable Pages Analytics in the Cloudflare dashboard
- View traffic, performance, and error metrics

## Production URLs

- **Production**: https://boltecho.pages.dev (or custom domain)
- **Preview Deployments**: https://[branch].boltecho.pages.dev

## Custom Domain Setup

1. Go to: Pages > boltecho > Custom domains
2. Click "Set up a custom domain"
3. Enter your domain (e.g., bolt.echocog.org)
4. Follow DNS configuration instructions
5. Wait for SSL certificate provisioning

## Security Best Practices

1. **Never commit** `.dev.vars` to version control
2. **Rotate API keys** regularly
3. **Use environment-specific** keys (separate for production/preview)
4. **Enable** Cloudflare Access for staging environments
5. **Review** Pages Functions logs for suspicious activity

## Support and Resources

- [Cloudflare Pages Documentation](https://developers.cloudflare.com/pages/)
- [Remix on Cloudflare](https://remix.run/docs/en/main/guides/deployment#cloudflare-pages)
- [Wrangler CLI Documentation](https://developers.cloudflare.com/workers/wrangler/)
- [Repository Issues](https://github.com/cogpy/bolt.echo/issues)

## Version Information

- **Node.js**: 20.15.1+
- **pnpm**: 9.4.0
- **Wrangler**: 4.27.0+
- **Remix**: 2.10.2
- **Cloudflare Pages**: Latest

---

Last Updated: November 2024
