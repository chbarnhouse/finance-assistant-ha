# Publishing Guide: Finance Assistant Home Assistant Integration

## 🚀 Quick Start

### Step 1: Create GitHub Repository

**Option A: Using GitHub CLI (Recommended)**
```bash
cd homeassistant-integration
./setup_github.sh
```

**Option B: Manual Creation**
1. Go to https://github.com/new
2. Repository name: `finance-assistant-ha`
3. Description: `Finance Assistant Home Assistant Integration`
4. Make it public
5. Don't initialize with README (we already have one)
6. Click "Create repository"

### Step 2: Push Code to GitHub

If you used the setup script, this is already done. Otherwise:

```bash
cd homeassistant-integration
git init
git remote add origin https://github.com/chbarnhouse/finance-assistant-ha.git
git add .
git commit -m "Initial release: Finance Assistant Home Assistant Integration v0.14.63"
git push -u origin main
git tag -a v0.14.63 -m "Release v0.14.63"
git push origin v0.14.63
```

### Step 3: Verify GitHub Actions

1. Go to https://github.com/chbarnhouse/finance-assistant-ha/actions
2. Check that the validation workflow passes
3. Verify the release workflow runs when you push tags

### Step 4: Submit to HACS

1. Go to https://hacs.xyz/docs/publish/include
2. Fill out the form:
   - **Repository**: `chbarnhouse/finance-assistant-ha`
   - **Category**: `Integration`
   - **Description**: `Finance Assistant Home Assistant Integration`
3. Submit the request

### Step 5: Update Documentation

Update the main Finance Assistant repository to reference the new integration:

1. Update `README.md` to mention the HACS integration
2. Update `PRDs/Finance_Assistant.md` to mark integration as complete
3. Update `Cursor Continuity.md` with the new repository information

## 📋 Repository Checklist

- [ ] Repository created at `chbarnhouse/finance-assistant-ha`
- [ ] All integration files committed
- [ ] GitHub Actions workflows added
- [ ] Initial release tag created (v0.14.63)
- [ ] Validation workflow passes
- [ ] HACS submission completed
- [ ] Documentation updated

## 🔗 Important URLs

- **Repository**: https://github.com/chbarnhouse/finance-assistant-ha
- **HACS Submission**: https://hacs.xyz/docs/publish/include
- **GitHub Actions**: https://github.com/chbarnhouse/finance-assistant-ha/actions

## 📝 Files Included

### Core Integration
- `custom_components/finance_assistant/__init__.py`
- `custom_components/finance_assistant/manifest.json`
- `custom_components/finance_assistant/config_flow.py`
- `custom_components/finance_assistant/coordinator.py`
- `custom_components/finance_assistant/sensor.py`
- `custom_components/finance_assistant/calendar.py`
- `custom_components/finance_assistant/const.py`
- `custom_components/finance_assistant/translations/en.json`

### HACS Support
- `hacs.json`
- `.github/workflows/validate.yml`
- `.github/workflows/release.yml`
- `README.md`
- `LICENSE`
- `.gitignore`

### Documentation
- `HACS_SUBMISSION.md`
- `PUBLISH_GUIDE.md`
- `test_integration.py`

## 🎯 Next Steps After Publishing

1. **Monitor HACS Submission**: Check for approval
2. **Test Installation**: Install via HACS in a test Home Assistant instance
3. **Community Feedback**: Monitor GitHub Issues for user feedback
4. **Updates**: Plan future releases and improvements
5. **Documentation**: Keep documentation up to date

## 🚨 Troubleshooting

### GitHub Actions Fail
- Check that all files are properly committed
- Verify manifest.json syntax
- Ensure translations are complete

### HACS Rejection
- Review HACS requirements: https://hacs.xyz/docs/publish/start
- Check validation workflow output
- Ensure all required files are present

### Installation Issues
- Test manual installation first
- Verify API endpoints are accessible
- Check Home Assistant logs for errors 