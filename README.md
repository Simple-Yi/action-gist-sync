# action-gist-sync

一个用于将仓库文件同步到 GitHub Gist 的 GitHub Action。

## 📋 功能特性

- 🔄 **自动同步**：根据映射规则自动将指定文件同步到 Gist
- 📝 **灵活配置**：支持通过文件或直接内容配置映射规则
- 🗑️ **智能清理**：自动删除 Gist 中不再需要的旧文件
- 🔍 **文件验证**：自动检查源文件是否存在和可读
- 🎯 **精确控制**：支持自定义 Gist 中的文件名

## 🚀 快速开始

### 基本用法

```yaml
name: Sync to Gist
on:
  push:
    branches:
      - main

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Sync to Gist
        uses: Simple-Yi/action-gist-sync@main
        with:
          gist_id: 'your-gist-id-here'
          gist_token: ${{ secrets.GIST_TOKEN }}
          mapping_content: |
            src/config.json:config.json
            docs/README.md:README.md
            LICENSE
```

## 📖 详细配置

### 输入参数

| 参数名 | 描述 | 必需 | 默认值 |
|--------|------|------|--------|
| `gist_id` | 目标 Gist 的 ID | ✅ | - |
| `gist_token` | 具有 gist 权限的 Personal Access Token | ✅ | - |
| `mapping_file` | 映射规则文件的路径 | ❌ | - |
| `mapping_content` | 直接指定的映射规则内容（优先级高于 mapping_file） | ❌ | - |

**注**：`mapping_file`和`mapping_content`虽在输入参数中为非必须，但必须至少提供一个，程序才能正常运行。

### 映射规则格式

映射规则采用 `源文件路径:目标文件名` 的格式，每行一个规则：

```
# 这是注释行，会被忽略
src/config.json:config.json
docs/README.md:documentation.md
scripts/deploy.sh
# 如果不指定目标文件名，将使用源文件名
LICENSE
```

**规则说明：**
- 以 `#` 开头的行为注释，会被忽略
- 空行会被忽略
- 格式：`源文件路径:目标文件名`
- 如果省略 `:目标文件名`，将使用源文件名作为目标文件名
- 不存在或不可读的文件会被跳过并显示警告

## 💡 使用示例

### 示例 1：使用映射内容

```yaml
- name: Sync to Gist
  uses: Simple-Yi/action-gist-sync@main
  with:
    gist_id: 'abcdef1234567890'
    gist_token: ${{ secrets.GIST_TOKEN }}
    mapping_content: |
      # 配置文件
      src/config.json:config.json
      .env.example:environment-template
      
      # 文档文件
      README.md:project-readme.md
      docs/api.md:api-documentation.md
      
      # 脚本文件
      scripts/build.sh:build-script.sh
```

### 示例 2：使用映射文件

首先创建映射文件 `.github/gist-mapping.txt`：

```
# 项目配置
package.json:package.json
tsconfig.json:typescript-config.json

# 文档
README.md:readme.md
CHANGELOG.md:changelog.md

# 示例代码
examples/basic.js:example-basic.js
examples/advanced.ts:example-advanced.ts
```

然后在工作流中使用：

```yaml
- name: Sync to Gist
  uses: Simple-Yi/action-gist-sync@main
  with:
    gist_id: 'abcdef1234567890'
    gist_token: ${{ secrets.GIST_TOKEN }}
    mapping_file: '.github/gist-mapping.txt'
```

### 示例 3：条件同步

```yaml
name: Conditional Gist Sync
on:
  push:
    paths:
      - 'docs/**'
      - 'examples/**'
      - 'README.md'

jobs:
  sync-docs:
    runs-on: ubuntu-latest
    if: contains(github.event.head_commit.message, '[sync-gist]')
    steps:
      - uses: actions/checkout@v4
      - name: Sync documentation to Gist
        uses: Simple-Yi/action-gist-sync@main
        with:
          gist_id: 'your-docs-gist-id'
          gist_token: ${{ secrets.GIST_TOKEN }}
          mapping_content: |
            README.md:project-readme.md
            docs/installation.md:installation-guide.md
            docs/usage.md:usage-examples.md
            examples/basic.py:basic-example.py
```

## 🔧 设置 Personal Access Token

1. 访问 [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. 点击 "Generate new token"
3. 选择适当的过期时间
4. 勾选 `gist` 权限
5. 生成并复制 token
6. 在你的仓库中添加名为 `GIST_TOKEN` 的 Secret

## 📋 工作原理

1. **解析映射规则**：从 `mapping_content` 或 `mapping_file` 中解析文件映射关系
2. **验证源文件**：检查源文件是否存在且可读，跳过无效文件
3. **克隆 Gist**：将目标 Gist 克隆到本地
4. **清理旧文件**：删除 Gist 中不在映射列表中的文件
5. **同步新文件**：将源文件复制到 Gist 本地副本
6. **提交推送**：如有更改，提交并推送到 Gist

## ⚠️ 注意事项

- 确保 Gist Token 具有 `gist` 权限
- 源文件必须是文本文件且可读
- Gist 中不在映射列表中的文件将被删除
- 如果没有检测到更改，Action 将跳过提交步骤

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔗 相关链接

- [GitHub Actions 官方文档](https://docs.github.com/en/actions)
- [GitHub Gist API](https://docs.github.com/en/rest/gists)
- [Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
