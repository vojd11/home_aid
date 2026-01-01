// @ts-nocheck
import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Box,
  Typography,
  Button,
  Paper,
  Grid,
  Chip,
  Alert,
  CircularProgress,
  Container,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material'
import {
  Add,
  LocalHospital,
  Warning,
  Error,
  Search,
  FilterList,
  CheckCircle
} from '@mui/icons-material'
import { Medication, MedicationList as MedicationListType } from '../types'
import api from '../lib/api'
import MedicationCard from './MedicationCard'
import AddMedicationDialog from './AddMedicationDialog'
import SearchBar from './SearchBar'

interface MedicationListProps {
  householdId: number
  householdName: string
}

export default function MedicationList({ householdId, householdName }: MedicationListProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedTag, setSelectedTag] = useState(null)
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const queryClient = useQueryClient()

  // Fetch medications for the household (without search/filter parameters)
  const { data: medicationData, isLoading, error } = useQuery({
    queryKey: ['medications', householdId],
    queryFn: async () => {
      const response = await api.get(`/households/${householdId}/medications/`)
      return response.data
    },
    enabled: !!householdId,
  })

  // Extract medications array from the response
  const allMedications = medicationData?.medications || []

  // Client-side filtering for immediate feedback without page refreshing
  const medications = useMemo(() => {
    let filtered = allMedications

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase().trim()
      filtered = filtered.filter(med => 
        med.name.toLowerCase().includes(query) ||
        (med.notes && med.notes.toLowerCase().includes(query)) ||
        (med.tags && med.tags.some(tag => tag.toLowerCase().includes(query)))
      )
    }

    // Filter by selected tag
    if (selectedTag) {
      filtered = filtered.filter(med => 
        med.tags && med.tags.includes(selectedTag)
      )
    }

    return filtered
  }, [allMedications, searchQuery, selectedTag])

  // Get unique tags from all medications (not filtered)
  const allTags = Array.isArray(allMedications) ? allMedications.flatMap(med => med.tags || []) : []
  const uniqueTags = [...new Set(allTags)].sort()

  // Decrement medication mutation
  const decrementMutation = useMutation({
    mutationFn: async (medicationId) => {
      await api.post(`/households/${householdId}/medications/${medicationId}/decrement/`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['medications', householdId] })
    },
  })

  // Delete medication mutation
  const deleteMutation = useMutation({
    mutationFn: async (medicationId) => {
      await api.delete(`/households/${householdId}/medications/${medicationId}/`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['medications', householdId] })
    },
  })

  // Refresh links mutation
  const refreshLinksMutation = useMutation({
    mutationFn: async (medicationId) => {
      await api.post(`/households/${householdId}/medications/${medicationId}/resolve-links`)
    },
    onSuccess: () => {
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['medications', householdId] })
      }, 2000)
    },
  })

  const handleDecrement = (medicationId) => {
    decrementMutation.mutate(medicationId)
  }

  const handleDelete = (medicationId) => {
    if (window.confirm('Are you sure you want to delete this medication?')) {
      deleteMutation.mutate(medicationId)
    }
  }

  const handleRefreshLinks = (medicationId) => {
    refreshLinksMutation.mutate(medicationId)
  }

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 12 }}>
        <Box sx={{ textAlign: 'center' }}>
          <CircularProgress size={32} sx={{ mb: 2 }} />
          <Typography color="text.secondary">Loading medications...</Typography>
        </Box>
      </Box>
    )
  }

  if (error) {
    return (
      <Alert 
        severity="error" 
        sx={{ 
          borderRadius: 3, 
          p: 3,
          textAlign: 'center',
          '& .MuiAlert-icon': { fontSize: 48, mb: 2 }
        }}
        action={
          <Button 
            variant="contained" 
            onClick={() => window.location.reload()}
            sx={{ mt: 2 }}
          >
            Reload Page
          </Button>
        }
      >
        <Typography variant="h6" component="div" sx={{ mb: 1 }}>
          Error loading medications
        </Typography>
        <Typography variant="body2">
          {error instanceof Error ? error.message : 'Unable to load medications. Please try again.'}
        </Typography>
      </Alert>
    )
  }

  // Calculate summary stats from all medications
  const totalMedications = Array.isArray(allMedications) ? allMedications.length : 0
  const lowStockCount = Array.isArray(allMedications) ? allMedications.filter(med => med.quantity <= 5 && med.quantity > 0).length : 0
  const outOfStockCount = Array.isArray(allMedications) ? allMedications.filter(med => med.quantity === 0).length : 0

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Header with Stats */}
      <Paper elevation={2} sx={{ p: { xs: 2, sm: 3 }, mb: 3, borderRadius: 3 }}>
        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, justifyContent: 'space-between', alignItems: { sm: 'center' }, gap: 2 }}>
          <Box>
            <Typography variant="h4" component="h2" sx={{ fontWeight: 600, mb: 1 }}>
              {householdName} Medications
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
              <Chip 
                icon={<LocalHospital />}
                label={`${totalMedications} total`} 
                variant="outlined"
                color="primary"
              />
              {(searchQuery || selectedTag) && (
                <Chip 
                  icon={<Search />}
                  label={`${medications.length} shown`} 
                  variant="filled"
                  color="info"
                  size="small"
                />
              )}
              {lowStockCount > 0 && (
                <Chip 
                  icon={<Warning />}
                  label={`${lowStockCount} low stock`} 
                  color="warning"
                />
              )}
              {outOfStockCount > 0 && (
                <Chip 
                  icon={<Error />}
                  label={`${outOfStockCount} out of stock`} 
                  color="error"
                />
              )}
            </Box>
          </Box>
          <Button
            onClick={() => setIsAddDialogOpen(true)}
            variant="contained"
            size="large"
            startIcon={<Add />}
            sx={{
              borderRadius: 2,
              textTransform: 'none',
              fontWeight: 600,
              px: 3,
              background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%)',
              },
            }}
          >
            Add Medication
          </Button>
        </Box>
      </Paper>

      {/* Search and Filters */}
      <Box sx={{ mb: 3 }}>
        <SearchBar
          value={searchQuery}
          onChange={setSearchQuery}
          placeholder="Search by name, notes, or tags..."
          sx={{ maxWidth: 400, mb: 2 }}
        />

        {/* Tag Filter */}
        {uniqueTags.length > 0 && (
          <Box>
            <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
              <FilterList fontSize="small" />
              Filter by tags:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              <Chip
                label="All tags"
                onClick={() => setSelectedTag(null)}
                color={selectedTag === null ? 'primary' : 'default'}
                variant={selectedTag === null ? 'filled' : 'outlined'}
                clickable
              />
              {uniqueTags.map((tag) => (
                <Chip
                  key={tag}
                  label={`#${tag}`}
                  onClick={() => setSelectedTag(tag === selectedTag ? null : tag)}
                  color={selectedTag === tag ? 'primary' : 'default'}
                  variant={selectedTag === tag ? 'filled' : 'outlined'}
                  clickable
                />
              ))}
            </Box>
          </Box>
        )}
      </Box>

      {/* Medications Grid */}
      {Array.isArray(medications) && medications.length > 0 ? (
        <Grid container spacing={3}>
          {medications.map((medication) => (
            <Grid item xs={12} sm={6} lg={4} key={medication.id}>
              <MedicationCard
                medication={medication}
                householdId={householdId}
                onDecrement={() => handleDecrement(medication.id)}
                onDelete={() => handleDelete(medication.id)}
                onRefreshLinks={() => handleRefreshLinks(medication.id)}
                isDecrementLoading={decrementMutation.isPending}
                isDeleteLoading={deleteMutation.isPending}
                isRefreshLinksLoading={refreshLinksMutation.isPending}
              />
            </Grid>
          ))}
        </Grid>
      ) : !isLoading && householdId ? (
        <Paper elevation={2} sx={{ borderRadius: 3, overflow: 'hidden' }}>
          <Box sx={{ textAlign: 'center', py: 8, px: 3 }}>
            <Box sx={{ maxWidth: 600, mx: 'auto' }}>
              {/* Empty State Icon */}
              <Box
                sx={{
                  width: 96,
                  height: 96,
                  background: 'linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%)',
                  borderRadius: 3,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mx: 'auto',
                  mb: 4,
                  boxShadow: 2
                }}
              >
                <LocalHospital sx={{ fontSize: 48, color: 'primary.main' }} />
              </Box>
              
              {searchQuery || selectedTag ? (
                <>
                  <Typography variant="h5" sx={{ fontWeight: 600, mb: 2 }}>
                    No medications found
                  </Typography>
                  <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
                    Try adjusting your search or filter criteria, or add a new medication to get started.
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 2, justifyContent: 'center' }}>
                    <Button
                      variant="outlined"
                      onClick={() => {
                        setSearchQuery('')
                        setSelectedTag(null)
                      }}
                    >
                      Clear filters
                    </Button>
                    <Button
                      variant="contained"
                      startIcon={<Add />}
                      onClick={() => setIsAddDialogOpen(true)}
                      sx={{
                        background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%)',
                        },
                      }}
                    >
                      Add Medication
                    </Button>
                  </Box>
                </>
              ) : (
                <>
                  <Typography variant="h4" sx={{ fontWeight: 700, mb: 2 }}>
                    Start building your medicine cabinet
                  </Typography>
                  <Typography variant="h6" color="text.secondary" sx={{ mb: 4 }}>
                    Keep track of your medications, quantities, and important information all in one place.
                    Get started by adding your first medication.
                  </Typography>
                  
                  <Button
                    variant="contained"
                    size="large"
                    startIcon={<Add />}
                    onClick={() => setIsAddDialogOpen(true)}
                    sx={{
                      borderRadius: 2,
                      textTransform: 'none',
                      fontWeight: 600,
                      fontSize: '1.1rem',
                      px: 4,
                      py: 1.5,
                      mb: 4,
                      background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                      boxShadow: 3,
                      '&:hover': {
                        background: 'linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%)',
                        boxShadow: 4,
                      },
                    }}
                  >
                    Add Your First Medication
                  </Button>
                  
                  {/* Feature highlights */}
                  <Card variant="outlined" sx={{ mt: 4, textAlign: 'left', backgroundColor: 'grey.50' }}>
                    <CardContent sx={{ p: 3 }}>
                      <Typography variant="h6" sx={{ fontWeight: 600, mb: 3, textAlign: 'center' }}>
                        What you can track:
                      </Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={12} sm={6}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                            <CheckCircle color="success" fontSize="small" />
                            <Typography variant="body2" sx={{ fontWeight: 500 }}>
                              Medication names & quantities
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                            <CheckCircle color="success" fontSize="small" />
                            <Typography variant="body2" sx={{ fontWeight: 500 }}>
                              Organize with tags
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                            <CheckCircle color="success" fontSize="small" />
                            <Typography variant="body2" sx={{ fontWeight: 500 }}>
                              Quick quantity updates
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                            <CheckCircle color="success" fontSize="small" />
                            <Typography variant="body2" sx={{ fontWeight: 500 }}>
                              External drug information
                            </Typography>
                          </Box>
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>
                </>
              )}
            </Box>
          </Box>
        </Paper>
      ) : null}

      {/* Add Medication Dialog */}
      <AddMedicationDialog
        isOpen={isAddDialogOpen}
        onClose={() => setIsAddDialogOpen(false)}
        householdId={householdId}
      />
    </Container>
  )
}
