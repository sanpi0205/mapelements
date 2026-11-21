# 发布流程

本文是维护者手册。日常开发只需要推送 `main`；发版只需要在 GitHub
网页创建一个 Release，其余工作由 Actions 完成。

## 版本规则

- 版本号唯一来源是 git tag，格式 `vMAJOR.MINOR.PATCH`，例如 `v0.2.0`。
- `pyproject.toml` 不写死版本号，由 `setuptools-scm` 从 tag 推导。
- 预发布使用 `v0.2.0rc1` 这类 tag，并在 GitHub Release 上勾选
  “Set as a pre-release”。
- 0.x 阶段：新功能或破坏性改动升 minor，修复升 patch。
- 1.0 之后：严格遵循 Semantic Versioning。
- 已经上传到 PyPI 的版本不能覆盖，也不能删除后重发；只能发 patch 并
  在 PyPI 上 yank 坏版本。

## 日常更新

```powershell
git switch main
git pull --ff-only
# 修改代码或文档
pytest -q
git add .
git commit -m "fix: ..."
git push origin main
```

推送后确认 CI 全绿。文档改动会自动部署到 GitHub Pages，不需要发版。

## 发版

1. 确认 `main` 的最新 CI 是绿的。
2. 打开 GitHub 仓库的 **Releases** 页面，点击 **Draft a new release**。
3. Tag 填新版本，例如 `v0.2.0`；target 选 `main`。
4. 点击 **Generate release notes**，检查自动生成的说明。
5. 点击 **Publish release**。

发布后 `Publish` workflow 会自动：

1. 在 Python 3.9 和 3.14 上再跑一遍测试；
2. 构建 sdist 和 wheel，执行 `twine check --strict`；
3. 校验 tag 与构建出的版本一致；
4. 在干净虚拟环境中安装 wheel，检查 `py.typed` 和 `__version__`；
5. 通过 PyPI Trusted Publishing 上传；
6. 把 wheel、sdist 和 `SHA256SUMS` 挂到 GitHub Release。

不要在本机执行 `twine upload`。发布只走 GitHub Release。

## 发布后检查

```powershell
pip install --upgrade "mapelements==0.2.0"
python -c "import mapelements; print(mapelements.__version__)"
```

同时确认：

- PyPI 项目页出现新版本；
- GitHub Release 上有构建产物；
- <https://sanpi0205.github.io/mapelements/> 可以访问。

## 手动重跑

`Publish` workflow 支持 `workflow_dispatch`：

- 在 Actions 页面选择 `Publish` → **Run workflow**；
- **必须选择对应的 `v*` tag**，不要选 `main`；
- `dry_run` 保持勾选时只构建和检查，不会上传 PyPI；
- 取消勾选才会真正上传。

## 失败处理

- **测试或构建失败，还没上传 PyPI**：修复后重新发布；如果 Release 已经
  公开，先删除该 Release 和 tag，再重新创建同一个版本。
- **已经上传 PyPI**：不要删除版本。在 PyPI 上 yank，然后发布 patch。
- **只是 Release 资产上传失败**：重跑 workflow 即可，不影响 PyPI。
- **文档部署失败**：代码发布不受影响；修复文档后重跑 Docs workflow。

## 一次性设置

- PyPI → 项目 → Publishing → Trusted Publisher：
  - Owner: `sanpi0205`
  - Repository: `mapelements`
  - Workflow name: `publish.yml`
  - Environment: `pypi`
- GitHub → Settings → Pages → Source 选择 **GitHub Actions**。
- 给 `v*` tag 配置保护规则，禁止误删或移动已经发布的 tag。
- GitHub 和 PyPI 都开启双因素认证。

## 变更日志

从 0.1.1 起，变更记录由 GitHub Releases 自动生成，不再手工维护
`CHANGELOG.md`。`CHANGELOG.md` 只保留 0.1.0 的历史内容。
