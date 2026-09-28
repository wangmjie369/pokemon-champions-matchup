# 在线更新说明

当前项目会从在线更新源检查：

- `update/version.json`
- `update/update-pack.json`

工作流：

- `.github/workflows/update-champions.yml`
- 每 4 小时运行一次
- 也可以手动触发

## 启用 GitHub Pages 或在线文件

1. 把整个项目上传到 GitHub 仓库。
2. 让仓库根目录下的 `update/` 可以被 HTTPS 访问。
3. 修改根目录的 `update-config.js`：

```js
window.CHAMPIONS_UPDATE_CONFIG = {
  baseUrl: "https://你的用户名.github.io/你的仓库名/update",
  checkIntervalHours: 4
};
```

如果使用 GitHub Raw，也可以填写对应的 `raw.githubusercontent.com` 地址。

## Android APK

网页版放在服务器上时，更新地址可以直接使用相对路径。  
APK 使用 `file:///android_asset/index.html`，所以要联网更新 APK 内的数据，必须把 `baseUrl` 改成上面的 HTTPS 绝对地址，然后重新打包一次 APK。

之后冠军版数据更新时：

1. GitHub Actions 自动更新数据
2. APK 启动时检查版本
3. 发现新版本后下载更新包
4. 下次启动使用新数据
