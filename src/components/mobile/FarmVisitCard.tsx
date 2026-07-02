import { useRef, useState, type PointerEvent } from 'react';
import { Box, Button, IconButton, Stack, Typography } from '@mui/material';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutlineOutlined';
import CloseIcon from '@mui/icons-material/Close';
import ContentCopyIcon from '@mui/icons-material/ContentCopyOutlined';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutlineOutlined';
import PhoneOutlinedIcon from '@mui/icons-material/PhoneOutlined';
import ScheduleIcon from '@mui/icons-material/Schedule';
import type { DispatchStop } from '../../types/dispatch';
import { copyText } from '../../utils/clipboard';
import { formatTimestampLabel } from '../../utils/time';

interface FarmVisitCardProps {
  stop: DispatchStop;
  phone: string;
  riskLabel: string;
  riskColor: string;
  onComplete: () => void;
  onCancel: () => void;
}

const swipeThreshold = 82;

function telHref(phone: string) {
  const digits = phone.replace(/[^\d+]/g, '');
  return digits ? `tel:${digits}` : undefined;
}

export function FarmVisitCard({ stop, phone, riskLabel, riskColor, onComplete, onCancel }: FarmVisitCardProps) {
  const startXRef = useRef<number | null>(null);
  const [offsetX, setOffsetX] = useState(0);
  const [copied, setCopied] = useState(false);
  const isCompleted = stop.status === 'completed';
  const isCancelled = stop.status === 'cancelled';
  const canComplete = stop.status === 'upcoming';
  const canCancel = isCompleted;
  const canSwipe = canComplete || canCancel;
  const address = stop.farm.address.trim();
  const phoneLink = telHref(phone);

  const handlePointerDown = (event: PointerEvent<HTMLDivElement>) => {
    if (!canSwipe) return;
    startXRef.current = event.clientX;
    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const handlePointerMove = (event: PointerEvent<HTMLDivElement>) => {
    if (startXRef.current === null || !canSwipe) return;
    const delta = event.clientX - startXRef.current;
    const min = canCancel ? -112 : 0;
    const max = canComplete ? 112 : 0;
    setOffsetX(Math.max(min, Math.min(max, delta)));
  };

  const handlePointerEnd = () => {
    if (!canSwipe) return;
    if (canComplete && offsetX > swipeThreshold) onComplete();
    if (canCancel && offsetX < -swipeThreshold) onCancel();
    setOffsetX(0);
    startXRef.current = null;
  };

  const handleCopyAddress = async () => {
    if (!address) return;
    await copyText(address);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1200);
  };

  return (
    <Box
      sx={{
        position: 'relative',
        overflow: 'hidden',
        borderRadius: 1,
        border: '1px solid #E3E6EA',
        bgcolor: '#fff',
      }}
    >
      {canComplete && (
        <Stack
          sx={{
            position: 'absolute',
            insetBlock: 0,
            left: 0,
            width: 92,
            alignItems: 'center',
            justifyContent: 'center',
            bgcolor: '#36B84A',
            color: '#fff',
            pointerEvents: 'none',
          }}
        >
          <CheckCircleOutlineIcon />
          <Typography variant="body2" sx={{ fontWeight: 900 }}>
            완료
          </Typography>
        </Stack>
      )}
      {canCancel && (
        <Stack
          sx={{
            position: 'absolute',
            insetBlock: 0,
            right: 0,
            width: 92,
            alignItems: 'center',
            justifyContent: 'center',
            bgcolor: '#E53935',
            color: '#fff',
            pointerEvents: 'none',
          }}
        >
          <CloseIcon />
          <Typography variant="body2" sx={{ fontWeight: 900 }}>
            취소
          </Typography>
        </Stack>
      )}

      <Box
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerEnd}
        onPointerCancel={handlePointerEnd}
        sx={{
          position: 'relative',
          transform: `translateX(${offsetX}px)`,
          transition: startXRef.current === null ? 'transform 0.18s ease' : 'none',
          bgcolor: isCompleted || isCancelled ? '#F5F6F7' : '#fff',
          opacity: 1,
          px: 2,
          py: 1.8,
          touchAction: 'pan-y',
          userSelect: 'none',
        }}
      >
        <Stack direction="row" spacing={2} sx={{ alignItems: 'center' }}>
          <Stack sx={{ width: 42, alignItems: 'center', color: isCompleted ? '#43A047' : isCancelled ? '#E53935' : 'primary.main' }}>
            <Typography sx={{ fontSize: 34, fontWeight: 900, lineHeight: 1 }}>
              {stop.order}
            </Typography>
            {isCompleted && <CheckCircleOutlineIcon sx={{ fontSize: 22, mt: 0.6 }} />}
            {isCancelled && <ErrorOutlineIcon sx={{ fontSize: 22, mt: 0.6 }} />}
          </Stack>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Stack direction="row" sx={{ alignItems: 'center', justifyContent: 'space-between', gap: 1 }}>
              <Stack direction="row" spacing={0.25} sx={{ alignItems: 'center', minWidth: 0 }}>
                <Typography sx={{ fontWeight: 900, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {stop.farm.name}
                </Typography>
                <IconButton
                  size="small"
                  aria-label={`${stop.farm.name} 주소 복사`}
                  title={copied ? '주소 복사됨' : address || '주소 없음'}
                  disabled={!address}
                  onClick={(event) => {
                    event.stopPropagation();
                    void handleCopyAddress();
                  }}
                  onPointerDown={(event) => event.stopPropagation()}
                  sx={{
                    width: 28,
                    height: 28,
                    color: copied ? '#43A047' : '#667085',
                    flexShrink: 0,
                  }}
                >
                  <ContentCopyIcon sx={{ fontSize: 17 }} />
                </IconButton>
              </Stack>
              <Box
                sx={{
                  px: 0.8,
                  py: 0.25,
                  borderRadius: 999,
                  bgcolor: isCompleted || isCancelled ? `${riskColor}66` : riskColor,
                  color: '#fff',
                  fontSize: 12,
                  fontWeight: 900,
                  flexShrink: 0,
                }}
              >
                {riskLabel}
              </Box>
            </Stack>
            <Stack
              component="a"
              href={phoneLink}
              direction="row"
              spacing={0.6}
              onPointerDown={(event) => event.stopPropagation()}
              sx={{
                alignItems: 'center',
                color: '#5F6876',
                mt: 0.55,
                textDecoration: 'none',
                width: 'fit-content',
                WebkitTapHighlightColor: 'transparent',
              }}
            >
              <PhoneOutlinedIcon sx={{ fontSize: 15 }} />
              <Typography variant="body2">{phone}</Typography>
            </Stack>
            <Stack direction="row" spacing={1} sx={{ alignItems: 'center', color: '#374151', mt: 0.75 }}>
              <Typography variant="body2">{stop.farm.livestockType}</Typography>
              <Typography variant="body2" color="text.secondary">
                |
              </Typography>
              <Typography variant="body2">{`${stop.farm.livestockCount.toLocaleString()}${stop.farm.livestockUnit}`}</Typography>
            </Stack>
            <Stack direction="row" spacing={0.6} sx={{ alignItems: 'center', color: isCompleted ? '#43A047' : '#374151', mt: 0.8 }}>
              <ScheduleIcon sx={{ fontSize: 16 }} />
              <Typography variant="body2" sx={{ fontWeight: 700 }}>
                {isCompleted
                  ? `실제 ${stop.actualDurationMinutes ?? stop.farm.estimatedDurationMinutes}분`
                  : isCancelled
                    ? `취소 ${formatTimestampLabel(stop.cancelledAt)}`
                    : `${stop.farm.estimatedDurationMinutes}분`}
              </Typography>
            </Stack>
          </Box>
        </Stack>
        {(canComplete || canCancel) && (
          <Button
            fullWidth
            variant="contained"
            color={canComplete ? 'success' : 'error'}
            startIcon={canComplete ? <CheckCircleOutlineIcon /> : <CloseIcon />}
            onPointerDown={(event) => event.stopPropagation()}
            onClick={(event) => {
              event.stopPropagation();
              if (canComplete) onComplete();
              else onCancel();
            }}
            sx={{ mt: 1.4, fontWeight: 800 }}
          >
            {canComplete ? '완료 처리' : '완료 취소'}
          </Button>
        )}
      </Box>
    </Box>
  );
}
