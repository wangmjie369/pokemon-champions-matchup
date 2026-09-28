# 在线更新说明

当前项目会从在线更新源检查：

- `update/version.json`
- `update/update-pack.json`

工作流：

- `.github/workflows/update-champions.yml`
- 每 4 小时运行一次
- 也可以手动触发

## 使用 GitHub Raw 更新源

1. 把整个项目上传到 GitHub 仓库。
2. 更新源使用 GitHub Raw 即可，不需要开启 Pages。
3. 修改根目录的 `update-config.js`：

```js
window.CHAMPIONS_UPDATE_CONFIG = {
  baseUrl: "https://raw.githubusercontent.com/wangmjie369/pokemon-champions-matchup/main/update",
  checkIntervalHours: 4
};
```



## Android APK

APK 使用 `file:///android_asset/index.html`，所以要联网更新 APK 内的数据，必须把 `baseUrl` 改成上面的 HTTPS 绝对地址，然后重新打包一次 APK。

之后冠军版数据更新时：

1. GitHub Actions 自动更新数据
2. APK 启动时检查版本
3. 发现新版本后下载更新包
4. 下次启动使用新数据
