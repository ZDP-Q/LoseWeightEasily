# 小松 移动端 📱

基于 Flutter 构建的现代化减重助手客户端。

## 🎨 视觉风格

- **设计规范**: Material 3
- **核心风格**: Glassmorphism (毛玻璃) 视觉效果
- **配色**: 靛蓝色 (Indigo) 与 翡翠绿 (Emerald)
- **字体**: Poppins

## 🛠️ 技术栈

- **框架**: [Flutter](https://flutter.dev/) (SDK ^3.11.0)
- **状态管理**: [Provider](https://pub.dev/packages/provider)
- **图表库**: [fl_chart](https://pub.dev/packages/fl_chart)
- **动画**: [flutter_animate](https://pub.dev/packages/flutter_animate), [animations](https://pub.dev/packages/animations)
- **网络请求**: `http`

## 🚀 运行指南

### 1. 安装依赖

```bash
flutter pub get
```

### 2. 配置后端地址

在 `lib/services/api_service.dart` 中配置后端 API 的基础 URL。
- Android 模拟器: `http://10.0.2.2:8000`
- iOS 模拟器/真机: `http://localhost:8000` 或 局域网 IP

### 3. 运行应用

```bash
flutter run
```

## 📂 项目结构

```text
lib/
├── models/         # 领域对象模型
├── providers/      # 状态管理逻辑
├── screens/        # 功能页面 (Dashboard, Search, BMR, Weight, MealPlan)
├── services/       # API 客户端与后端通信
├── utils/          # 配色、主题及通用工具
└── widgets/        # 可复用的自定义 UI 组件
```

## 🧪 静态检查

在提交代码前，请确保通过以下检查：

```bash
flutter analyze
```
