import { Box } from '@mui/material';

interface LivestockIconProps {
  livestockType: string;
  size?: number;
}

const LIVESTOCK_ICON_BY_TYPE: Record<string, string> = {
  닭: '/livestock-icons/hen.png',
  오리: '/livestock-icons/duck.png',
  기타가금: '/livestock-icons/quail.png',
  기타가금류: '/livestock-icons/quail.png',
};

export function LivestockIcon({ livestockType, size = 24 }: LivestockIconProps) {
  const baseType = livestockType.split('-')[0];
  const iconSrc = LIVESTOCK_ICON_BY_TYPE[baseType] ?? LIVESTOCK_ICON_BY_TYPE.기타가금;

  return (
    <Box
      component="img"
      src={iconSrc}
      alt={`${livestockType} 아이콘`}
      sx={{
        width: size,
        height: size,
        flexShrink: 0,
        objectFit: 'contain',
      }}
    />
  );
}
