import { Box, Stack, Tooltip } from '@mui/material';
import type { XaiFactor } from '../../types/farm';

interface XaiFactorIconsProps {
  factors: XaiFactor[];
  size?: number;
  imageSize?: number;
}

function resolveIconSrc(icon: string) {
  if (icon.startsWith("/")) return icon;
  if (icon === "bird") return "/xai-icons/bird.png";
  if (icon === "truck") return "/xai-icons/map_pin.png";
  return `/xai-icons/${icon.endsWith(".png") ? icon : `${icon}.png`}`;
}

export function XaiFactorIcons({ factors, size = 32, imageSize = 20 }: XaiFactorIconsProps) {
  if (factors.length === 0) return null;

  return (
    <Stack direction="row" spacing={0.75} useFlexGap sx={{ flexWrap: 'wrap' }}>
      {factors.map((factor) => (
        <Tooltip key={factor.id} title={factor.label} arrow placement="top">
          <Box
            component="span"
            tabIndex={0}
            aria-label={factor.label}
            sx={{
              width: size,
              height: size,
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
              borderRadius: 1,
              bgcolor: '#FDECEA',
              border: '1px solid #F5B5B5',
              cursor: 'help',
              '&:focus-visible': {
                outline: '2px solid #C62828',
                outlineOffset: 2,
              },
            }}
          >
            <Box
              component="img"
              src={resolveIconSrc(factor.icon)}
              alt=""
              sx={{
                width: imageSize,
                height: imageSize,
                display: 'block',
                objectFit: 'contain',
              }}
            />
          </Box>
        </Tooltip>
      ))}
    </Stack>
  );
}
