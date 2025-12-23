"""调试导入导出检测"""
import sys
sys.path.insert(0, '.')

from quality_gates import L0StaticGate

files = {
    'src/pages/Index.tsx': '''
import React from 'react';
import {
  computeOrderStats,
  generateMockOrders,
  type Order,
} from '@/lib/generated/dashboard-orders';

export default function Index() {
  const orders = generateMockOrders(100);
  const stats = computeOrderStats(orders);
  return <div>{stats.totalOrders}</div>;
}
''',
    'src/lib/generated/dashboard-orders.ts': '''
export type Order = {
  id: string;
  customer: string;
  total: number;
};

export function getOrders(): Order[] {
  return [];
}

export function getOrderStats(orders: Order[]) {
  return { totalOrders: orders.length };
}
'''
}

gate = L0StaticGate()
result = gate.check(files)

print("所有问题:")
for issue in result.issues:
    if issue.get('rule_id') == 'import_export_mismatch':
        print(f"  - {issue['message']}")
        print(f"    建议: {issue['suggestion']}")

