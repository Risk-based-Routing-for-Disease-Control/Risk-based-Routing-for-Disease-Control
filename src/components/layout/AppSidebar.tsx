import { Box, List, ListItemButton, ListItemIcon, ListItemText } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import MapIcon from '@mui/icons-material/MapOutlined';
import LocalShippingIcon from '@mui/icons-material/LocalShippingOutlined';

const NAV_ITEMS = [
  { to: '/map', label: '방역 계획', icon: MapIcon, activePaths: ['/map', '/dispatch'] },
  { to: '/confirmed', label: '방역 진행 현황', icon: LocalShippingIcon, activePaths: ['/confirmed'] },
] as const;

export function AppSidebar() {
  const location = useLocation();

  return (
    <Box
      sx={{
        width: 200,
        flexShrink: 0,
        borderRight: '1px solid',
        borderColor: 'divider',
        bgcolor: 'background.paper',
      }}
    >
      <List sx={{ py: 0 }}>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const selected = item.activePaths.some((path) => location.pathname.startsWith(path));
          return (
            <ListItemButton
              key={item.to}
              component={Link}
              to={item.to}
              selected={selected}
              sx={{
                py: 1.5,
                '&.Mui-selected': {
                  bgcolor: 'primary.main',
                  color: '#fff',
                  '&:hover': { bgcolor: 'primary.dark' },
                  '& .MuiListItemIcon-root': { color: '#fff' },
                },
              }}
            >
              <ListItemIcon sx={{ minWidth: 36 }}>
                <Icon fontSize="small" />
              </ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          );
        })}
      </List>
    </Box>
  );
}
