import { Box, List, ListItemButton, ListItemIcon, ListItemText } from '@mui/material';
import { NavLink } from 'react-router-dom';
import MapIcon from '@mui/icons-material/Map';
import AltRouteIcon from '@mui/icons-material/AltRoute';
import AssignmentTurnedInIcon from '@mui/icons-material/AssignmentTurnedIn';

const NAV_ITEMS = [
  { to: '/map', label: '지도', icon: MapIcon },
  { to: '/dispatch', label: '경로 배치', icon: AltRouteIcon },
  { to: '/confirmed', label: '확정 경로', icon: AssignmentTurnedInIcon },
] as const;

export function AppSidebar() {
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
          return (
            <ListItemButton
              key={item.to}
              component={NavLink}
              to={item.to}
              sx={{
                py: 1.5,
                '&.active': {
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
