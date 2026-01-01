// @ts-nocheck
import { useState } from 'react'
import { 
  Card, 
  CardContent, 
  Typography, 
  IconButton, 
  Button, 
  Chip, 
  Box, 
  Menu, 
  MenuItem,
  CircularProgress,
  Link,
  Alert,
  Tooltip,
  Divider,
  Collapse
} from '@mui/material'
import { 
  MoreVert, 
  Edit, 
  Delete, 
  Refresh, 
  Remove, 
  LocalOffer,
  Search,
  Circle,
  OpenInNew,
  Description,
  LocalPharmacy,
  Info,
  ExpandMore,
  ExpandLess
} from '@mui/icons-material'
import { Medication } from '../types'
import EditMedicationDialog from './EditMedicationDialog'
import InstructionViewer from './InstructionViewer'
import { useStorePrices } from '../hooks/useMedications'

interface MedicationCardProps {
  medication: Medication
  householdId: number
  onDecrement: () => void
  onDelete: () => void
  onRefreshLinks?: () => void
  isDecrementLoading?: boolean
  isDeleteLoading?: boolean
  isRefreshLinksLoading?: boolean
}

export default function MedicationCard({
  medication,
  householdId,
  onDecrement,
  onDelete,
  onRefreshLinks,
  isDecrementLoading = false,
  isDeleteLoading = false,
  isRefreshLinksLoading = false,
}: MedicationCardProps) {
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isInstructionViewerOpen, setIsInstructionViewerOpen] = useState(false)
  const [anchorEl, setAnchorEl] = useState(null)
  const [showStorePrices, setShowStorePrices] = useState(false)

  // Fetch store prices when user wants to see them
  const { 
    data: storePrices, 
    isLoading: isLoadingPrices, 
    error: pricesError 
  } = useStorePrices(householdId, medication.id, showStorePrices)

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget)
  }

  const handleMenuClose = () => {
    setAnchorEl(null)
  }

  const isLowStock = medication.quantity <= 5 && medication.quantity > 0
  const isOutOfStock = medication.quantity === 0

  const getStatusColor = () => {
    if (isOutOfStock) return 'error'
    if (isLowStock) return 'warning'
    return 'success'
  }

  const getStatusText = () => {
    if (isOutOfStock) return 'Out of stock'
    if (isLowStock) return 'Low stock'
    return 'In stock'
  }

  return (
    <>
      <Card
        elevation={2}
        sx={{
          borderRadius: 3,
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: 6,
          },
          ...(isOutOfStock && {
            borderLeft: '4px solid',
            borderLeftColor: 'error.main',
            backgroundColor: 'error.50',
          }),
          ...(isLowStock && {
            borderLeft: '4px solid',
            borderLeftColor: 'warning.main',
            backgroundColor: 'warning.50',
          }),
        }}
      >
        <CardContent sx={{ p: 3 }}>
          {/* Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography 
                variant="h6" 
                component="h3"
                sx={{ 
                  fontWeight: 600,
                  mb: 0.5,
                  wordBreak: 'break-word'
                }}
              >
                {medication.name}
              </Typography>
              {medication.description && (
                <Typography 
                  variant="body2" 
                  color="text.secondary"
                  sx={{
                    mt: 0.5,
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                    fontStyle: 'italic'
                  }}
                >
                  {medication.description}
                </Typography>
              )}
              {medication.notes && (
                <Typography 
                  variant="body2" 
                  color="text.secondary"
                  sx={{
                    mt: 0.5,
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                  }}
                >
                  {medication.notes}
                </Typography>
              )}
            </Box>
            
            {/* Actions Menu */}
            <IconButton
              onClick={handleMenuClick}
              size="small"
              sx={{ ml: 1 }}
              aria-label="More actions"
            >
              <MoreVert />
            </IconButton>
            
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
              transformOrigin={{ horizontal: 'right', vertical: 'top' }}
              anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
              <MenuItem 
                onClick={() => {
                  setIsEditDialogOpen(true)
                  handleMenuClose()
                }}
              >
                <Edit fontSize="small" sx={{ mr: 1 }} />
                Edit
              </MenuItem>
              {onRefreshLinks && (
                <MenuItem 
                  onClick={() => {
                    onRefreshLinks()
                    handleMenuClose()
                  }}
                  disabled={isRefreshLinksLoading}
                >
                  <Refresh 
                    fontSize="small" 
                    sx={{ 
                      mr: 1,
                      ...(isRefreshLinksLoading && {
                        animation: 'spin 1s linear infinite',
                        '@keyframes spin': {
                          '0%': { transform: 'rotate(0deg)' },
                          '100%': { transform: 'rotate(360deg)' },
                        },
                      })
                    }} 
                  />
                  Refresh Links
                </MenuItem>
              )}
              <MenuItem 
                onClick={() => {
                  onDelete()
                  handleMenuClose()
                }}
                disabled={isDeleteLoading}
                sx={{ color: 'error.main' }}
              >
                {isDeleteLoading ? (
                  <CircularProgress size={16} sx={{ mr: 1 }} />
                ) : (
                  <Delete fontSize="small" sx={{ mr: 1 }} />
                )}
                Delete
              </MenuItem>
            </Menu>
          </Box>

          {/* Status and Quantity */}
          <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 2, mb: 2, alignItems: { sm: 'center' } }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip
                icon={<Circle sx={{ fontSize: '12px !important' }} />}
                label={`${medication.quantity} ${medication.quantity === 1 ? 'item' : 'items'}`}
                color={getStatusColor()}
                variant="outlined"
                size="small"
                sx={{
                  fontWeight: 600,
                  '& .MuiChip-icon': {
                    marginLeft: '8px'
                  }
                }}
              />
              
              {(isOutOfStock || isLowStock) && (
                <Chip
                  label={getStatusText()}
                  color={getStatusColor()}
                  size="small"
                  sx={{ fontWeight: 500 }}
                />
              )}
            </Box>

            {/* Decrement Button */}
            <Button
              onClick={onDecrement}
              disabled={medication.quantity <= 0 || isDecrementLoading}
              variant="contained"
              size="medium"
              startIcon={isDecrementLoading ? <CircularProgress size={16} color="inherit" /> : <Remove />}
              sx={{
                borderRadius: 2,
                fontWeight: 600,
                textTransform: 'none',
                minWidth: 'auto',
                px: 2,
                background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%)',
                },
                '&:disabled': {
                  background: 'linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)',
                },
              }}
            >
              {isDecrementLoading ? 'Updating...' : '-1'}
            </Button>
          </Box>

          {/* External Resources */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1, fontWeight: 500 }}>
              External Resources:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 1 }}>
              {/* Instruction Button */}
              {medication.drlz_instruction_link ? (
                <Tooltip title="View official medication instruction">
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<Description />}
                    onClick={() => setIsInstructionViewerOpen(true)}
                    sx={{
                      borderColor: 'info.main',
                      color: 'info.main',
                      fontSize: '0.75rem',
                      '&:hover': {
                        backgroundColor: 'info.50',
                      },
                    }}
                  >
                    Instruction
                  </Button>
                </Tooltip>
              ) : (
                <Tooltip title="No instruction available">
                  <span>
                    <Button
                      size="small"
                      variant="outlined"
                      startIcon={<Description />}
                      disabled
                      sx={{
                        fontSize: '0.75rem',
                      }}
                    >
                      Instruction
                    </Button>
                  </span>
                </Tooltip>
              )}
              
              {/* Prices Button */}
              <Button
                size="small"
                variant="outlined"
                startIcon={isLoadingPrices ? <CircularProgress size={16} /> : <LocalPharmacy />}
                endIcon={showStorePrices ? <ExpandLess /> : <ExpandMore />}
                onClick={() => setShowStorePrices(!showStorePrices)}
                disabled={isLoadingPrices}
                sx={{
                  borderColor: 'success.main',
                  color: 'success.main',
                  fontSize: '0.75rem',
                  '&:hover': {
                    backgroundColor: 'success.50',
                  },
                }}
              >
                {isLoadingPrices ? 'Loading...' : 'Prices'}
              </Button>
            </Box>

            {/* Store Prices Collapse */}
            <Collapse in={showStorePrices}>
              <Box sx={{ mt: 1, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                {isLoadingPrices && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CircularProgress size={16} />
                    <Typography variant="body2" color="text.secondary">
                      Fetching prices from stores...
                    </Typography>
                  </Box>
                )}

                {pricesError && (
                  <Alert severity="error" size="small" sx={{ mb: 1 }}>
                    Failed to load store prices
                  </Alert>
                )}

                {storePrices && (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
                      Current Prices ({new Date(storePrices.last_updated || '').toLocaleString()}):
                    </Typography>
                    
                    {storePrices.stores.map((store, index) => (
                      <Box 
                        key={index}
                        sx={{ 
                          display: 'flex', 
                          justifyContent: 'space-between', 
                          alignItems: 'center',
                          p: 1,
                          bgcolor: 'white',
                          borderRadius: 0.5,
                          border: '1px solid',
                          borderColor: 'grey.200'
                        }}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {store.link ? (
                            <Button
                              size="small"
                              variant="text"
                              startIcon={<OpenInNew sx={{ fontSize: '14px !important' }} />}
                              onClick={() => window.open(store.link, '_blank')}
                              sx={{
                                fontSize: '0.75rem',
                                textTransform: 'none',
                                minWidth: 'auto',
                                px: 1,
                              }}
                            >
                              {store.store_name}
                            </Button>
                          ) : (
                            <Typography variant="body2" color="text.secondary">
                              {store.store_name}
                            </Typography>
                          )}
                        </Box>
                        
                        <Box sx={{ textAlign: 'right' }}>
                          {store.status === 'success' && store.price ? (
                            <Typography variant="body2" sx={{ fontWeight: 600, color: 'success.main' }}>
                              from {store.price} {store.currency}
                            </Typography>
                          ) : store.status === 'not_found' ? (
                            <Typography variant="caption" color="text.secondary">
                              Not found
                            </Typography>
                          ) : (
                            <Typography variant="caption" color="error.main">
                              Error
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    ))}
                    
                    {storePrices.stores.every(store => store.status !== 'success') && (
                      <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 1 }}>
                        No prices found in any store
                      </Typography>
                    )}
                  </Box>
                )}
              </Box>
            </Collapse>
          </Box>

          {/* Tags */}
          {medication.tags.length > 0 && (
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
              {medication.tags.map((tag) => (
                <Chip
                  key={tag}
                  icon={<LocalOffer sx={{ fontSize: '14px !important' }} />}
                  label={tag}
                  variant="outlined"
                  size="small"
                  sx={{
                    backgroundColor: 'grey.100',
                    borderColor: 'grey.300',
                    '&:hover': {
                      backgroundColor: 'grey.200',
                    },
                  }}
                />
              ))}
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Dialogs */}
      <EditMedicationDialog
        isOpen={isEditDialogOpen}
        onClose={() => setIsEditDialogOpen(false)}
        medication={medication}
        householdId={householdId}
      />

      <InstructionViewer
        isOpen={isInstructionViewerOpen}
        onClose={() => setIsInstructionViewerOpen(false)}
        instructionUrl={medication.drlz_instruction_link}
        medicationName={medication.name}
      />
    </>
  )
}
