# 发布前检查总入口

默认流程：

```text
用户选择平台
↓
调用通用短视频检查
↓
调用对应平台专项检查
↓
输出评分、问题和修改稿
```

先读：

- `references/platforms/common-short-video-rules.md`
- `references/prepublish/common-checklist.md`

再按平台读取：

- 小红书：`references/platforms/xiaohongshu-rules.md` + `references/prepublish/xiaohongshu-checklist.md`
- 抖音：`references/platforms/douyin-rules.md` + `references/prepublish/douyin-checklist.md`
- 视频号：`references/platforms/wechat-channels-rules.md` + `references/prepublish/wechat-channels-checklist.md`

统一输出四档结论：

1. **可以直接发布**
2. **小改后发布**
3. **建议重写**
4. **不建议发布**

总分不是目的。任何严重证据、合规、原创或平台失配问题，都应阻止发布或降为“建议重写 / 不建议发布”。
