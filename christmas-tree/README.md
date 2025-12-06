# 🎄 Grand Luxury Interactive 3D Christmas Tree

> 一个基于 **React**, **Three.js (R3F)** 和 **AI 手势识别** 的高保真 3D 圣诞树 Web 应用。

这个项目不仅仅是一棵树，它是一个承载记忆的交互式画廊。成百上千个粒子、璀璨的彩灯和悬浮的拍立得照片共同组成了一棵奢华的圣诞树。用户可以通过手势控制树的形态（聚合/散开）和视角旋转，体验电影级的视觉盛宴。

![Project Preview](public/preview.png)
*(注：建议在此处上传一张你的项目运行截图)*

## ✨ 核心特性

* **极致视觉体验**：由 45,000+ 个发光粒子组成的树身，配合动态光晕 (Bloom) 和辉光效果，营造梦幻氛围。
* **记忆画廊**：照片以“拍立得”风格悬浮在树上，每一张都是一个独立的发光体，支持双面渲染。
* **AI 手势控制**：无需鼠标，通过摄像头捕捉手势即可控制树的形态（聚合/散开）和视角旋转。
* **丰富细节**：包含动态闪烁的彩灯、飘落的金银雪花、以及随机分布的圣诞礼物和糖果装饰。
* **高度可定制**：**支持用户轻松替换为自己的照片，并自由调整照片数量。**

## 🛠️ 技术栈

* **框架**: React 18, Vite
* **3D 引擎**: React Three Fiber (Three.js)
* **工具库**: @react-three/drei, Maath
* **后期处理**: @react-three/postprocessing
* **AI 视觉**: MediaPipe Tasks Vision (Google)

## 🚀 快速开始

### 面向零命令行经验的使用步骤
1) 安装 Node.js：访问 [Node.js 官网](https://nodejs.org/)，下载并安装 **v18 或更高版本**。
2) 打开终端：
   - macOS：按 `Command + 空格` 搜索“终端”，打开后你会看到一个黑色窗口。
   - Windows：按 `Win + R` 输入 `cmd` 并回车。
3) 进入项目文件夹：在终端中输入 `cd` 后面加上项目路径，例如：
   ```bash
   cd /Users/你的用户名/Desktop/Fun/christmas-tree
   ```
4) 安装依赖（只需第一次运行）：在终端输入并回车：
   ```bash
   npm install
   ```
   看到没有报错并回到可输入状态就表示安装完成。
5) 启动项目：在同一个终端输入：
   ```bash
   npm run dev
   ```
   终端会显示一个本地地址，通常是 `http://localhost:5173/`。按住 `Command`（或 `Ctrl`）点击这个地址即可在浏览器打开。
6) 停止运行：回到终端，按 `Ctrl + C` 结束开发服务器。

### 🖼️ 自定义照片
### 1. 准备照片
- 打开 `public/photos/` 文件夹。
- 顶端封面：命名为 `top.jpg`（显示在树顶的立体五角星上）。
- 树身照片：命名为 `1.jpg`, `2.jpg`, `3.jpg` ... 依次类推。
- 建议使用正方形或 4:3 比例，单张图片 500 KB 以内，避免卡顿。

### 2. 替换照片
把你的照片直接复制进 `public/photos/`，覆盖原有文件，保持文件名不变（例如继续使用 `1.jpg`、`2.jpg`）。

### 3. 修改照片数量（想放更多或更少）
如果放入了更多照片（默认 31 张），需要调整代码里的数字：
1) 用任意文本编辑器打开 `src/App.tsx`。
2) 找到注释 `// --- 动态生成照片列表 (top.jpg + 1.jpg 到 31.jpg) ---` 附近的常量：
   ```ts
   const TOTAL_NUMBERED_PHOTOS = 31; // <--- 修改这个数字！
   ```
3) 把 `31` 改成你的照片总数（不含 `top.jpg`），保存文件并刷新浏览器。
### 🖐️ 手势控制说明
* **本项目内置 AI 手势识别，请在有摄像头的环境下使用**。屏幕右下角有 DEBUG 按钮可以查看摄像头画面。
* 手势说明：
  - 🖐 张开手掌 (Open Palm)：Disperse（散开）— 树炸裂成漫天粒子和照片。
  - ✊ 握紧拳头 (Closed Fist)：Assemble（聚合）— 所有元素瞬间聚合成树。
  - 👋 手掌左右移动：旋转视角 — 手向左移树向左转，向右移树向右转。
  - 👋 手掌上下移动：俯仰视角 — 手向上移视角抬高，向下移视角降低。
### ⚙️ 进阶配置
* **如果你熟悉代码，可以在 src/App.tsx 中的 CONFIG 对象里调整更多视觉参数**：
  const CONFIG = {
  colors: { ... }, // 修改树、灯光、边框的颜色
  counts: {
    foliage: 15000,   // 修改树叶粒子数量 (配置低可能会卡)
    ornaments: 300,   // 修改悬挂的照片/拍立得数量
    lights: 400       // 修改彩灯数量
  },
  tree: { height: 22, radius: 9 }, // 修改树的大小
  // ...
};
### 📄 License
MIT License. Feel free to use and modify for your own holiday celebrations!
### Merry Christmas! 🎄✨
