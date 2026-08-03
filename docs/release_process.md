# Release Process & Versioning Policy 📦

## 1. Semantic Versioning (SemVer)
The platform follows [Semantic Versioning 2.0.0](https://semver.org/):
- **MAJOR (`v1.0.0`)**: Breaking API schema or model registry compatibility changes.
- **MINOR (`v1.1.0`)**: New feature additions, new feature definitions, or updated model architectures.
- **PATCH (`v1.0.1`)**: Bug fixes, performance optimizations, or documentation updates.

---

## 2. Release Checklist

Before tagging a release:
1. [ ] Run pytest test suite: `./.venv/bin/pytest`
2. [ ] Build browser extension: `cd extension && npm run build`
3. [ ] Verify container build: `docker compose build`
4. [ ] Update `CHANGELOG.md` with version notes.
5. [ ] Create Git release tag:
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0: Production Readiness & Manifest V3 Extension"
   git push origin v1.0.0
   ```

---

## 3. Extension Artifact Packaging
To package the Chrome Web Store distribution zip:
```bash
cd extension
npm run build
zip -r ../dist/extension_v1.0.0.zip dist/
```
