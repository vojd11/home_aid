import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../hooks/useAuth'
import { useQuery } from '@tanstack/react-query'
import api from '../lib/api'
import { Household } from '../types'
import MedicationList from '../components/MedicationList'
import CreateHouseholdDialog from '../components/CreateHouseholdDialog'
import LanguageSelector from '../components/LanguageSelector'
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  CardActions,
  Avatar,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  CircularProgress,
  Paper,
  Stack,
  Divider,
  useTheme,
  useMediaQuery,
  Drawer,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material'
import {
  Add as AddIcon,
  Logout as LogoutIcon,
  Home as HomeIcon,
  AccountCircle as AccountCircleIcon,
  Check as CheckIcon,
  MedicalServices as MedicalServicesIcon,
  Menu as MenuIcon,
  AdminPanelSettings as AdminIcon,
  Person as PersonIcon
} from '@mui/icons-material'

export default function DashboardPage() {
  const { user, logout } = useAuth()
  const { t } = useTranslation()
  const [selectedHousehold, setSelectedHousehold] = useState<number | null>(null)
  const [isCreateHouseholdOpen, setIsCreateHouseholdOpen] = useState(false)
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false)
  
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  
  const { data: households, isLoading: householdsLoading } = useQuery({
    queryKey: ['households'],
    queryFn: async () => {
      const response = await api.get('/households/')
      return response.data as Household[]
    },
  })

  const selectedHouseholdData = households?.find((h: Household) => h.id === selectedHousehold)

  const handleUserMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleUserMenuClose = () => {
    setAnchorEl(null)
  }

  const handleLogout = () => {
    handleUserMenuClose()
    logout()
  }

  const handleDrawerToggle = () => {
    setMobileDrawerOpen(!mobileDrawerOpen)
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'grey.50' }}>
      {/* App Bar */}
      <AppBar 
        position="sticky" 
        elevation={0}
        sx={{ 
          bgcolor: 'background.paper', 
          borderBottom: 1, 
          borderColor: 'divider',
          backdropFilter: 'blur(20px)',
          background: 'rgba(255, 255, 255, 0.8)'
        }}
      >
        <Toolbar>
          {/* Logo and Title */}
          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
            <Avatar
              sx={{
                width: 40,
                height: 40,
                background: 'linear-gradient(45deg, #2196F3 30%, #9C27B0 90%)',
                mr: 2
              }}
            >
              <MedicalServicesIcon />
            </Avatar>
            <Box>
              <Typography 
                variant="h6" 
                component="h1" 
                sx={{ 
                  color: 'text.primary',
                  fontWeight: 'bold',
                  display: { xs: 'none', sm: 'block' }
                }}
              >
                Home Aid Kit
              </Typography>
              {selectedHouseholdData && (
                <Typography 
                  variant="body2" 
                  sx={{ 
                    color: 'text.secondary',
                    display: { xs: 'none', sm: 'block' }
                  }}
                >
                  {selectedHouseholdData.name}
                </Typography>
              )}
            </Box>
          </Box>

          {/* Desktop User Menu */}
          {!isMobile && (
            <>
              <Box sx={{ display: 'flex', alignItems: 'center', mr: 2, gap: 2 }}>
                <LanguageSelector iconOnly size="small" />
                <Box sx={{ textAlign: 'right' }}>
                  <Typography variant="body2" sx={{ color: 'text.primary', fontWeight: 500 }}>
                    {t('dashboard.welcomeBack', 'Welcome back!')}
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                    {user?.email}
                  </Typography>
                </Box>
              </Box>
              <Button
                color="error"
                variant="outlined"
                startIcon={<LogoutIcon />}
                onClick={handleLogout}
                size="small"
              >
                {t('navigation.logout')}
              </Button>
            </>
          )}

          {/* Mobile Menu Button */}
          {isMobile && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="end"
              onClick={handleDrawerToggle}
              sx={{ color: 'text.primary' }}
            >
              <MenuIcon />
            </IconButton>
          )}
        </Toolbar>
      </AppBar>

      {/* Mobile Drawer */}
      <Drawer
        anchor="right"
        open={mobileDrawerOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true,
        }}
      >
        <Box sx={{ width: 250, p: 2 }}>
          <Box sx={{ textAlign: 'center', mb: 2 }}>
            <Avatar sx={{ width: 60, height: 60, mx: 'auto', mb: 1 }}>
              <AccountCircleIcon />
            </Avatar>
            <Typography variant="subtitle1" fontWeight="medium">
              {user?.email}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {t('auth.signedIn', 'Signed in')}
            </Typography>
          </Box>
          <Divider sx={{ mb: 2 }} />
          
          {/* Language Selector */}
          <Box sx={{ mb: 3 }}>
            <LanguageSelector variant="outlined" size="small" />
          </Box>
          
          <Button
            fullWidth
            color="error"
            variant="outlined"
            startIcon={<LogoutIcon />}
            onClick={handleLogout}
          >
            {t('navigation.logout')}
          </Button>
        </Box>
      </Drawer>

      {/* Main Content */}
      <Container maxWidth="xl" sx={{ py: 3 }}>
        {/* Household Selection Section */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ 
            display: 'flex', 
            flexDirection: { xs: 'column', sm: 'row' },
            alignItems: { xs: 'flex-start', sm: 'center' },
            justifyContent: 'space-between',
            gap: 2,
            mb: 3
          }}>
            <Box>
              <Typography variant="h4" fontWeight="bold" gutterBottom>
                {t('dashboard.yourHouseholds', 'Your Households')}
              </Typography>
              <Typography variant="body1" color="text.secondary">
                {t('dashboard.selectHousehold', 'Select a household to manage medications')}
              </Typography>
            </Box>
            {households && households.length > 0 && (
                            <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setIsCreateHouseholdOpen(true)}
                sx={{ 
                  borderRadius: 2,
                  textTransform: 'none',
                  fontWeight: 600
                }}
              >
                {t('dashboard.addHousehold', 'Add Household')}
              </Button>
            )}
          </Box>
          
          {householdsLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
              <Box sx={{ textAlign: 'center' }}>
                <CircularProgress size={40} />
                <Typography variant="body1" color="text.secondary" sx={{ mt: 2 }}>
                  Loading households...
                </Typography>
              </Box>
            </Box>
          ) : households && households.length > 0 ? (
            <Grid container spacing={3}>
              {households.map((household) => (
                <Grid item xs={12} sm={6} lg={4} key={household.id}>
                  <Card
                    sx={{
                      cursor: 'pointer',
                      transition: 'all 0.2s ease-in-out',
                      border: selectedHousehold === household.id ? 2 : 1,
                      borderColor: selectedHousehold === household.id ? 'primary.main' : 'divider',
                      bgcolor: selectedHousehold === household.id ? 'primary.50' : 'background.paper',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: 4
                      },
                      '&:active': {
                        transform: 'translateY(0px)'
                      }
                    }}
                    onClick={() => setSelectedHousehold(household.id)}
                  >
                    <CardContent sx={{ pb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography variant="h6" fontWeight="semibold" gutterBottom>
                            {household.name}
                          </Typography>
                          <Chip
                            icon={household.role === 'admin' ? <AdminIcon /> : <PersonIcon />}
                            label={household.role}
                            size="small"
                            color={household.role === 'admin' ? 'primary' : 'success'}
                            variant="outlined"
                          />
                        </Box>
                        {selectedHousehold === household.id && (
                          <Avatar
                            sx={{
                              width: 24,
                              height: 24,
                              bgcolor: 'primary.main'
                            }}
                          >
                            <CheckIcon sx={{ fontSize: 16 }} />
                          </Avatar>
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Avatar
                sx={{
                  width: 80,
                  height: 80,
                  mx: 'auto',
                  mb: 3,
                  bgcolor: 'grey.100'
                }}
              >
                <HomeIcon sx={{ fontSize: 40, color: 'grey.500' }} />
              </Avatar>
              <Typography variant="h4" fontWeight="bold" gutterBottom>
                Welcome to Home Aid Kit
              </Typography>
              <Typography 
                variant="body1" 
                color="text.secondary" 
                sx={{ mb: 4, maxWidth: 600, mx: 'auto', lineHeight: 1.6 }}
              >
                Create your first household to start managing your medications and aid kit items. 
                You can invite family members and organize your medical supplies together.
              </Typography>
                            <Button
                variant="contained"
                size="large"
                startIcon={<AddIcon />}
                onClick={() => setIsCreateHouseholdOpen(true)}
                sx={{
                  py: 1.5,
                  px: 4,
                  borderRadius: 3,
                  textTransform: 'none',
                  fontWeight: 600,
                  fontSize: '1.1rem',
                  background: 'linear-gradient(45deg, #2196F3 30%, #9C27B0 90%)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #1976D2 30%, #7B1FA2 90%)',
                  }
                }}
              >
                {t('dashboard.createFirstHousehold')}
              </Button>

              {/* Feature highlights */}
              <Paper 
                sx={{ 
                  mt: 4, 
                  p: 3, 
                  bgcolor: 'grey.50', 
                  maxWidth: 500, 
                  mx: 'auto',
                  textAlign: 'left'
                }}
              >
                <Typography variant="h6" fontWeight="semibold" sx={{ mb: 2, textAlign: 'center' }}>
                  {t('dashboard.whyUseHouseholds')}
                </Typography>
                <Stack spacing={2}>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5 }}>
                    <Avatar sx={{ width: 24, height: 24, bgcolor: 'primary.100', mt: 0.5 }}>
                      <CheckIcon sx={{ fontSize: 14, color: 'primary.main' }} />
                    </Avatar>
                    <Typography variant="body2" color="text.primary" fontWeight="medium">
                      {t('dashboard.shareWithFamily')}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5 }}>
                    <Avatar sx={{ width: 24, height: 24, bgcolor: 'primary.100', mt: 0.5 }}>
                      <CheckIcon sx={{ fontSize: 14, color: 'primary.main' }} />
                    </Avatar>
                    <Typography variant="body2" color="text.primary" fontWeight="medium">
                      {t('dashboard.organizeAidKits')}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5 }}>
                    <Avatar sx={{ width: 24, height: 24, bgcolor: 'primary.100', mt: 0.5 }}>
                      <CheckIcon sx={{ fontSize: 14, color: 'primary.main' }} />
                    </Avatar>
                    <Typography variant="body2" color="text.primary" fontWeight="medium">
                      {t('dashboard.roleBasedAccess')}
                    </Typography>
                  </Box>
                </Stack>
              </Paper>
            </Paper>
          )}
        </Box>

        {/* Medication List */}
        {selectedHousehold && selectedHouseholdData && (
          <Box sx={{ mt: 4 }}>
            <MedicationList 
              householdId={selectedHousehold}
              householdName={selectedHouseholdData.name}
            />
          </Box>
        )}
      </Container>

      {/* Create Household Dialog */}
      <CreateHouseholdDialog
        isOpen={isCreateHouseholdOpen}
        onClose={() => setIsCreateHouseholdOpen(false)}
      />
    </Box>
  )
}
