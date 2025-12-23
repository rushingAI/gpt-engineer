"""
真实案例测试 - 模拟用户报告的问题
"""

import sys
sys.path.insert(0, '.')

from quality_gates import L0StaticGate
import json


def test_user_reported_issue():
    """测试用户报告的真实问题"""
    print("=" * 70)
    print("真实案例测试 - 用户报告的依赖和数据问题")
    print("=" * 70)
    
    # 模拟生成的文件（简化版）
    files = {
        'vibe.meta.json': json.dumps({
            "dependencies": {
                "requested": {
                    "recharts": "^2.10.0",
                    "@vitejs/plugin-react": "^4.0.0",
                    "path": "builtin",
                    "url": "builtin"
                },
                "approved": {
                    "recharts": "^2.10.0"
                },
                "rejected": {
                    "@vitejs/plugin-react": "development dependency",
                    "path": "Node.js builtin module",
                    "url": "Node.js builtin module"
                }
            }
        }, indent=2),
        
        'vite.config.ts': '''
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { fileURLToPath } from 'url';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
''',
        
        'src/pages/Index.tsx': '''
import React from 'react';
import {
  computeOrderStats,
  generateMockOrders,
  type Order,
} from '@/lib/generated/dashboard-orders';
import { OrdersChart } from '@/components/generated/dashboard/OrdersChart';
import { OrdersTable } from '@/components/generated/dashboard/OrdersTable';

export default function Index() {
  const orders = generateMockOrders(100);
  const stats = computeOrderStats(orders);
  
  return (
    <div>
      <OrdersChart data={stats} />
      <OrdersTable orders={orders} />
    </div>
  );
}
''',
        
        'src/lib/generated/dashboard-orders.ts': '''
export type Order = {
  id: string;
  customer: string;
  total: number;
  date: string;
};

// AI 在自愈时改了名字，但没有同步 Index.tsx
export function getOrders(count: number = 50): Order[] {
  return Array.from({ length: count }, (_, i) => ({
    id: `ORD-${i + 1}`,
    customer: `Customer ${i + 1}`,
    total: Math.random() * 1000,
    date: new Date().toISOString(),
  }));
}

export function getOrderStats(orders: Order[]) {
  return {
    totalOrders: orders.length,
    totalRevenue: orders.reduce((sum, o) => sum + o.total, 0),
    avgOrderValue: orders.reduce((sum, o) => sum + o.total, 0) / orders.length,
  };
}
''',
        
        'src/components/generated/dashboard/OrdersChart.tsx': '''
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export const OrdersChart = ({ data }: any) => {
  // data 是 undefined，因为 Index.tsx 调用失败
  const chartData = data?.chartData || [];
  
  return (
    <LineChart width={600} height={300} data={chartData}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="name" />
      <YAxis />
      <Tooltip />
      <Legend />
      <Line type="monotone" dataKey="value" stroke="#8884d8" />
    </LineChart>
  );
};
''',
        
        'src/components/generated/dashboard/OrdersTable.tsx': '''
import React from 'react';

export const OrdersTable = ({ orders }: any) => {
  // orders 是 undefined，因为 Index.tsx 调用失败
  return (
    <table>
      <thead>
        <tr>
          <th>订单号</th>
          <th>客户</th>
          <th>金额</th>
        </tr>
      </thead>
      <tbody>
        {orders.map((order: any) => (
          <tr key={order.id}>
            <td>{order.id}</td>
            <td>{order.customer}</td>
            <td>{order.total.toLocaleString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};
''',
    }
    
    print("\n🔍 运行质量门禁检查...")
    gate = L0StaticGate()
    result = gate.check(files)
    
    print(f"\n{'='*70}")
    print(f"检查结果: {'✅ 通过' if result.passed else '❌ 失败'}")
    print(f"{'='*70}")
    
    if not result.passed:
        print(f"\n发现 {len(result.issues)} 个问题:\n")
        
        dependency_issues = []
        import_export_issues = []
        other_issues = []
        
        for issue in result.issues:
            rule_id = issue.get('rule_id', '')
            if 'dependency' in rule_id.lower():
                dependency_issues.append(issue)
            elif 'import_export' in rule_id.lower():
                import_export_issues.append(issue)
            else:
                other_issues.append(issue)
        
        if dependency_issues:
            print("📦 依赖问题:")
            for issue in dependency_issues:
                print(f"  ❌ {issue['message']}")
                print(f"     💡 建议: {issue['suggestion']}")
                print()
        
        if import_export_issues:
            print("🔗 导入导出不一致问题:")
            for issue in import_export_issues:
                print(f"  ❌ {issue['message']}")
                print(f"     💡 建议: {issue['suggestion']}")
                print()
        
        if other_issues:
            print("⚠️  其他问题:")
            for issue in other_issues[:3]:
                print(f"  - {issue['message']}")
            if len(other_issues) > 3:
                print(f"  - ... 还有 {len(other_issues) - 3} 个问题")
    
    print("\n" + "="*70)
    print("问题根因分析")
    print("="*70)
    
    has_dep_issues = any('dependency' in i.get('rule_id', '').lower() for i in result.issues)
    has_import_export = any('import_export' in i.get('rule_id', '').lower() for i in result.issues)
    
    if has_dep_issues:
        print("\n✅ 层面1: 依赖检测已正确过滤")
        print("   - @vitejs/plugin-react (开发依赖) → 不再报错")
        print("   - path, url (Node.js 内置) → 不再报错")
    else:
        print("\n❌ 层面1: 仍有依赖误报")
    
    if has_import_export:
        print("\n✅ 层面2: 导入导出不一致已被检测")
        print("   - Index.tsx 导入 computeOrderStats/generateMockOrders")
        print("   - dashboard-orders.ts 导出 getOrderStats/getOrders")
        print("   → 门禁捕获了这个不一致，防止运行时错误")
    else:
        print("\n❌ 层面2: 导入导出不一致未被检测")
    
    print("\n" + "="*70)
    print("修复建议")
    print("="*70)
    print("""
如果这些问题被门禁捕获，自愈流程会：

1. 收到 import_export_mismatch 错误
2. 动态规则注入 import_export_consistency 指导
3. AI 会看到建议：
   - 将 getOrderStats 改名为 computeOrderStats
   - 将 getOrders 改名为 generateMockOrders
   - 或者在 Index.tsx 中使用正确的导入名称

这样可以避免前端出现：
  ❌ Uncaught TypeError: Cannot read properties of undefined
  ❌ Error: <circle> attribute cy: Expected length, "NaN"
""")
    
    return has_dep_issues == False and has_import_export == True


if __name__ == '__main__':
    success = test_user_reported_issue()
    exit(0 if success else 1)

