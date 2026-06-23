import type { RiskLevel } from '../types/farm';

export const RISK_LEVEL_COLOR: Record<RiskLevel, string> = {
  critical: '#E53935',
  high: '#FB8C00',
  warning: '#43A047',
};

export const RISK_LEVEL_LABEL: Record<RiskLevel, string> = {
  critical: '매우위험',
  high: '위험',
  warning: '경고',
};

export const RISK_LEVELS: { value: RiskLevel; label: string; color: string }[] = [
  { value: 'critical', label: RISK_LEVEL_LABEL.critical, color: RISK_LEVEL_COLOR.critical },
  { value: 'high', label: RISK_LEVEL_LABEL.high, color: RISK_LEVEL_COLOR.high },
  { value: 'warning', label: RISK_LEVEL_LABEL.warning, color: RISK_LEVEL_COLOR.warning },
];
