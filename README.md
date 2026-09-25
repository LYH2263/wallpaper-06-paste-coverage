# 18-wallpaper（墙纸卷数）

Wallpaper — 幅宽分幅 + 花高匹配损耗后的卷数向上取整

## 启动

```bash
docker compose up --build
```

| 入口 | 地址 |
| --- | --- |
| 前端 | http://localhost:4700 |
| API | http://localhost:9700 |

## 主链

周长层高+花匹配 → 卷数 → 展开示意；可选胶浆：周长×层高扣门洞得净面积，÷涂布率向上取整得升数，与卷数同 run 落库。涂布率≤0 或净面积为负时拒绝且不写历史。设置页维护默认涂布率，改动不影响已保存的 run。

## 技术栈

Python 3.12 + FastAPI + SQLite；Vue 3 + Vite + Nginx。
