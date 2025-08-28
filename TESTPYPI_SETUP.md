# TestPyPI Setup Instructions

To enable automatic package publishing to TestPyPI when tags are pushed, you need to set up a TestPyPI API token:

## 1. Create a TestPyPI Account
- Go to https://test.pypi.org/
- Create an account if you don't have one

## 2. Generate API Token
- Log in to TestPyPI
- Go to Account Settings → API tokens
- Click "Add API token"
- Set scope to "Entire account" (or specific to this project if it exists)
- Copy the generated token (starts with `pypi-`)

## 3. Add Secret to GitHub Repository
- Go to your GitHub repository
- Settings → Secrets and variables → Actions
- Click "New repository secret"
- Name: `TEST_PYPI_API_TOKEN`
- Value: Paste your TestPyPI API token
- Click "Add secret"

## 4. Create a Release
To trigger the build and upload:

```bash
# Create and push a tag
git tag v0.1.0
git push origin v0.1.0
```

Or create a release through GitHub's web interface.

## 5. Install from TestPyPI
Once published, you can test the installation:

```bash
pip install --index-url https://test.pypi.org/simple/ beaglegaze
```

## Production PyPI
When ready for production, you can:
1. Create a PyPI account at https://pypi.org/
2. Generate a PyPI API token
3. Add it as `PYPI_API_TOKEN` secret
4. Modify the workflow to publish to PyPI instead of TestPyPI
