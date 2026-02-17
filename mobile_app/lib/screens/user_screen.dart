import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:provider/provider.dart';
import '../providers/theme_provider.dart';
import '../providers/user_provider.dart';
import '../utils/app_colors.dart';
import '../widgets/glass_card.dart';

class UserScreen extends StatelessWidget {
  const UserScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final userProvider = context.watch<UserProvider>();
    final themeProvider = context.watch<ThemeProvider>();

    return Scaffold(
      appBar: AppBar(title: const Text('个人中心')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            _buildProfileHeader(userProvider),
            const SizedBox(height: 24),
            _buildInfoSection(context, userProvider),
            const SizedBox(height: 24),
            _buildGoalSection(context, userProvider),
            const SizedBox(height: 24),
            _buildSettingsSection(context, themeProvider),
            const SizedBox(height: 32),
            _buildActionButtons(context),
          ],
        ),
      ),
    );
  }

  Widget _buildProfileHeader(UserProvider provider) {
    return Column(
      children: [
        const CircleAvatar(
          radius: 50,
          backgroundColor: AppColors.primary,
          child: Icon(Icons.person, size: 50, color: Colors.white),
        ),
        const SizedBox(height: 16),
        Text(
          provider.displayName,
          style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
        ),
        Text(
          provider.hasUser ? '已开启减重之旅' : '暂未设置资料',
          style: const TextStyle(color: AppColors.textSecondary),
        ),
      ],
    );
  }

  Widget _buildInfoSection(BuildContext context, UserProvider provider) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(' 基本信息', style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.textSecondary)),
        const SizedBox(height: 12),
        GlassCard(
          padding: EdgeInsets.zero,
          child: Column(
            children: [
              _buildListTile(context, '年龄', '${provider.user?.age ?? "--"} 岁', FontAwesomeIcons.calendar),
              _buildDivider(),
              _buildListTile(context, '身高', '${provider.user?.heightCm ?? "--"} cm', FontAwesomeIcons.arrowsUpDown),
              _buildDivider(),
              _buildListTile(context, '性别', provider.user?.gender == 'male' ? '男' : '女', FontAwesomeIcons.venusMars),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildGoalSection(BuildContext context, UserProvider provider) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(' 目标与代谢', style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.textSecondary)),
        const SizedBox(height: 12),
        GlassCard(
          padding: EdgeInsets.zero,
          child: Column(
            children: [
              _buildListTile(context, '目标体重', '${provider.user?.targetWeightKg ?? "--"} kg', FontAwesomeIcons.bullseye),
              _buildDivider(),
              _buildListTile(context, '活动水平', _formatActivity(provider.user?.activityLevel), FontAwesomeIcons.personRunning),
              _buildDivider(),
              _buildListTile(context, 'TDEE', '${provider.user?.tdee?.toStringAsFixed(0) ?? "--"} kcal', FontAwesomeIcons.bolt),
            ],
          ),
        ),
      ],
    );
  }

  String _formatActivity(String? level) {
    switch (level) {
      case 'sedentary': return '久坐';
      case 'light': return '轻度活动';
      case 'moderate': return '中度活动';
      case 'active': return '活跃';
      case 'very_active': return '极度活跃';
      default: return '未设置';
    }
  }

  Widget _buildSettingsSection(BuildContext context, ThemeProvider themeProvider) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(' 系统设置', style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.textSecondary)),
        const SizedBox(height: 12),
        GlassCard(
          padding: EdgeInsets.zero,
          child: Column(
            children: [
              ListTile(
                leading: const Icon(Icons.palette_outlined, size: 18, color: AppColors.primary),
                title: const Text('外观显示', style: TextStyle(fontSize: 15)),
                trailing: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(themeProvider.themeName, style: const TextStyle(color: AppColors.textSecondary)),
                    const Icon(Icons.chevron_right, size: 20, color: AppColors.border),
                  ],
                ),
                onTap: () => _showThemeDialog(context, themeProvider),
              ),
            ],
          ),
        ),
      ],
    );
  }

  void _showThemeDialog(BuildContext context, ThemeProvider themeProvider) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('选择外观'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _buildThemeOption(context, themeProvider, ThemeMode.system, '跟随系统', Icons.brightness_auto),
            _buildThemeOption(context, themeProvider, ThemeMode.light, '浅色模式', Icons.light_mode),
            _buildThemeOption(context, themeProvider, ThemeMode.dark, '深色模式', Icons.dark_mode),
          ],
        ),
      ),
    );
  }

  Widget _buildThemeOption(BuildContext context, ThemeProvider provider, ThemeMode mode, String title, IconData icon) {
    return ListTile(
      leading: Icon(icon),
      title: Text(title),
      trailing: provider.themeMode == mode ? const Icon(Icons.check, color: AppColors.primary) : null,
      onTap: () {
        provider.setThemeMode(mode);
        Navigator.pop(context);
      },
    );
  }

  Widget _buildListTile(BuildContext context, String title, String value, IconData icon) {
    return ListTile(
      leading: Icon(icon, size: 18, color: AppColors.primary),
      title: Text(title, style: const TextStyle(fontSize: 15)),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(value, style: const TextStyle(color: AppColors.textSecondary)),
          const Icon(Icons.chevron_right, size: 20, color: AppColors.border),
        ],
      ),
      onTap: () {
        // TODO: 实现修改功能
      },
    );
  }

  Widget _buildDivider() {
    return Divider(height: 1, indent: 50, color: AppColors.border.withValues(alpha: 0.1));
  }

  Widget _buildActionButtons(BuildContext context) {
    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          child: ElevatedButton(
            onPressed: () {
              // TODO: 实现保存
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            ),
            child: const Text('保存配置', style: TextStyle(fontWeight: FontWeight.bold)),
          ),
        ),
        TextButton(
          onPressed: () {},
          child: const Text('退出登录', style: TextStyle(color: AppColors.danger)),
        ),
      ],
    );
  }
}
