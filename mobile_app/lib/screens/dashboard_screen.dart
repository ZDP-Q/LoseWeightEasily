import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:google_fonts/google_fonts.dart';
import '../utils/app_colors.dart';
import '../widgets/glass_card.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 120,
            floating: true,
            backgroundColor: Colors.transparent,
            elevation: 0,
            flexibleSpace: FlexibleSpaceBar(
              titlePadding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
              title: Text(
                '早安, 开发者',
                style: GoogleFonts.poppins(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
            ),
          ),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildMainStats(context),
                  const SizedBox(height: 32),
                  Text(
                    '今日目标',
                    style: Theme.of(context).textTheme.titleLarge,
                  ).animate().fadeIn(delay: 400.ms).slideX(),
                  const SizedBox(height: 16),
                  _buildGoalGrid(context),
                  const SizedBox(height: 32),
                  Text(
                    '体重趋势',
                    style: Theme.of(context).textTheme.titleLarge,
                  ).animate().fadeIn(delay: 600.ms).slideX(),
                  const SizedBox(height: 16),
                  _buildWeightTrend(context),
                  const SizedBox(height: 100),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMainStats(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(24),
      color: AppColors.primary.withOpacity(0.15),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '剩余热量',
                  style: GoogleFonts.poppins(
                    color: AppColors.textSecondary,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '1,420 kcal',
                  style: GoogleFonts.poppins(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    const Icon(Icons.bolt, color: AppColors.accent, size: 16),
                    const SizedBox(width: 4),
                    Text(
                      '已消耗 580 kcal',
                      style: TextStyle(color: AppColors.textSecondary, fontSize: 12),
                    ),
                  ],
                ),
              ],
            ),
          ),
          Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: 80,
                height: 80,
                child: CircularProgressIndicator(
                  value: 0.3,
                  strokeWidth: 8,
                  backgroundColor: Colors.white.withOpacity(0.1),
                  color: AppColors.primary,
                  strokeCap: StrokeCap.round,
                ),
              ).animate().scale(duration: 800.ms, curve: Curves.easeOutBack),
              Text(
                '30%',
                style: GoogleFonts.poppins(
                  fontWeight: FontWeight.bold,
                  color: AppColors.primary,
                ),
              ),
            ],
          ),
        ],
      ),
    ).animate().fadeIn().slideY(begin: 0.2, end: 0);
  }

  Widget _buildGoalGrid(BuildContext context) {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      mainAxisSpacing: 16,
      crossAxisSpacing: 16,
      childAspectRatio: 1.5,
      children: [
        _buildStatItem('饮水量', '1.2/2.5 L', FontAwesomeIcons.droplet, Colors.blue),
        _buildStatItem('步数', '6,432', FontAwesomeIcons.personWalking, Colors.orange),
        _buildStatItem('蛋白质', '45/120 g', FontAwesomeIcons.egg, Colors.green),
        _buildStatItem('睡眠', '7.5h', FontAwesomeIcons.moon, Colors.indigo),
      ],
    ).animate().fadeIn(delay: 500.ms);
  }

  Widget _buildStatItem(String title, String value, IconData icon, Color color) {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 16),
              const SizedBox(width: 8),
              Text(title, style: TextStyle(color: AppColors.textSecondary, fontSize: 12)),
            ],
          ),
          Text(
            value,
            style: GoogleFonts.poppins(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppColors.textPrimary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildWeightTrend(BuildContext context) {
    return GlassCard(
      height: 120,
      width: double.infinity,
      child: Center(
        child: Text(
          '图表加载中...',
          style: TextStyle(color: AppColors.textMuted),
        ),
      ),
    ).animate().fadeIn(delay: 700.ms);
  }
}
