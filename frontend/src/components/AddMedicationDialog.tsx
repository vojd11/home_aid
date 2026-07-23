// @ts-nocheck
import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  IconButton,
  Typography,
  Box,
  Chip,
  CircularProgress,
  Alert,
  Autocomplete,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material'
import { 
  Close, 
  Add, 
  LocalOffer, 
  Search, 
  CheckCircle, 
  Info, 
  ExpandMore,
  OpenInNew,
  Description
} from '@mui/icons-material'
import { CreateMedicationSchema, CreateMedication, DRLZMedication } from '../types'
import api from '../lib/api'

interface AddMedicationDialogProps {
  isOpen: boolean
  onClose: () => void
  householdId: number
  // Optional prefilled values (e.g. coming from a barcode scan)
  initialBarcode?: string
  initialName?: string
}

export default function AddMedicationDialog({ isOpen, onClose, householdId, initialBarcode, initialName }: AddMedicationDialogProps) {
  const queryClient = useQueryClient()
  const [tags, setTags] = useState([])
  const [currentTag, setCurrentTag] = useState('')
  const [medicationName, setMedicationName] = useState('')
  const [barcode, setBarcode] = useState('')
  const [selectedDRLZMedication, setSelectedDRLZMedication] = useState<DRLZMedication | null>(null)
  const [drlzSearchQuery, setDrlzSearchQuery] = useState('')

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(CreateMedicationSchema),
    defaultValues: {
      quantity: 1,
    },
  })

  const watchedName = watch('name')

  // Apply prefilled values (e.g. from a barcode scan) when the dialog opens
  useEffect(() => {
    if (isOpen) {
      if (initialBarcode) {
        setBarcode(initialBarcode)
      }
      if (initialName) {
        setValue('name', initialName)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, initialBarcode, initialName])

  // DRLZ search query
  const { data: drlzResults, isLoading: isDrlzLoading, error: drlzError } = useQuery({
    queryKey: ['drlz-search', drlzSearchQuery],
    queryFn: async () => {
      if (!drlzSearchQuery || drlzSearchQuery.length < 3) return null
      const { drlzApi } = await import('../lib/api')
      return await drlzApi.searchMedications(drlzSearchQuery, 10)
    },
    enabled: !!drlzSearchQuery && drlzSearchQuery.length >= 3,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Auto-search DRLZ when name changes
  useEffect(() => {
    if (watchedName && watchedName.length >= 3 && watchedName !== drlzSearchQuery) {
      const timer = setTimeout(() => {
        setDrlzSearchQuery(watchedName)
      }, 500) // Debounce
      
      return () => clearTimeout(timer)
    }
  }, [watchedName, drlzSearchQuery])

  const createMutation = useMutation({
    mutationFn: async (data) => {
      // Generate Tabletki link if not already provided
      const tabletki_link = data.tabletki_link || `https://tabletki.ua/uk/search/${encodeURIComponent(data.name)}`
      
      const enhancedData = {
        ...data,
        tabletki_link,
        tags, // Include tags in the submission
        barcode: barcode || undefined // Persist scanned barcode when present
      }
      
      const response = await api.post(`/households/${householdId}/medications/`, enhancedData)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['medications', householdId] })
      handleClose()
    },
  })

  const handleClose = () => {
    reset()
    setTags([])
    setCurrentTag('')
    setMedicationName('')
    setBarcode('')
    setSelectedDRLZMedication(null)
    setDrlzSearchQuery('')
    onClose()
  }

  const handleSelectDRLZMedication = (medication: DRLZMedication) => {
    setSelectedDRLZMedication(medication)
    setValue('name', medication.main_name)
    
    // Build comprehensive description from DRLZ data
    let description = medication.main_name
    if (medication.form) {
      description += ` - ${medication.form}`
    }
    if (medication.manufacturer) {
      description += ` (${medication.manufacturer})`
    }
    setValue('description', description)
    
    // Set DRLZ links if available
    if (medication.medication_link) {
      setValue('drlz_link', medication.medication_link)
    }
    if (medication.instruction_link) {
      setValue('drlz_instruction_link', medication.instruction_link)
    }
    
    // Generate Tabletki search link
    const tablekiLink = `https://tabletki.ua/uk/search/${encodeURIComponent(medication.main_name)}`
    setValue('tabletki_link', tablekiLink)
  }

  const handleAddTag = (e) => {
    if (e.key === 'Enter' && currentTag.trim()) {
      e.preventDefault()
      const trimmedTag = currentTag.trim().toLowerCase()
      if (!tags.includes(trimmedTag)) {
        setTags([...tags, trimmedTag])
      }
      setCurrentTag('')
    }
  }

  const handleRemoveTag = (tagToRemove) => {
    setTags(tags.filter(tag => tag !== tagToRemove))
  }

  const addSuggestedTag = (suggestion) => {
    if (!tags.includes(suggestion)) {
      setTags([...tags, suggestion])
    }
  }

  const onSubmit = (data) => {
    createMutation.mutate(data)
  }

  return (
    <Dialog
      open={isOpen}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          maxHeight: '90vh'
        }
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="h5" component="h2" sx={{ fontWeight: 600 }}>
              Add New Medication
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              Track your household medications
            </Typography>
          </Box>
          <IconButton
            onClick={handleClose}
            sx={{ 
              color: 'text.secondary',
              '&:hover': { backgroundColor: 'action.hover' }
            }}
            aria-label="Close dialog"
          >
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ pb: 2 }}>
        <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ mt: 1 }}>
          {/* Error Alert */}
          {createMutation.isError && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {createMutation.error?.response?.data?.detail || 'Failed to add medication. Please try again.'}
            </Alert>
          )}

          {/* Name with DRLZ Integration */}
          <Box sx={{ mb: 3 }}>
            <TextField
              {...register('name')}
              label="Medication Name"
              placeholder="e.g., Ibuprofen 200mg, Vitamin D3, Aspirin..."
              fullWidth
              required
              error={!!errors.name}
              helperText={errors.name?.message || 'Start typing to search Ukrainian medicine registry (DRLZ)'}
              sx={{ mb: 2 }}
            />

            {/* DRLZ Search Results */}
            {isDrlzLoading && drlzSearchQuery && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <CircularProgress size={16} />
                <Typography variant="body2" color="text.secondary">
                  Searching Ukrainian medicine registry...
                </Typography>
              </Box>
            )}

            {drlzResults && drlzResults.medications && drlzResults.medications.length > 0 && (
              <Accordion sx={{ mb: 2 }}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Search fontSize="small" />
                    <Typography variant="subtitle2">
                      Found {drlzResults.medications.length} medications in Ukrainian registry
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <List dense>
                    {drlzResults.medications.slice(0, 5).map((med: DRLZMedication, index: number) => (
                      <Box key={index}>
                        <ListItem
                          button
                          onClick={() => handleSelectDRLZMedication(med)}
                          selected={selectedDRLZMedication?.main_name === med.main_name}
                          sx={{
                            borderRadius: 1,
                            mb: 1,
                            border: selectedDRLZMedication?.main_name === med.main_name ? '2px solid' : '1px solid',
                            borderColor: selectedDRLZMedication?.main_name === med.main_name ? 'primary.main' : 'divider'
                          }}
                        >
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Typography variant="subtitle2" fontWeight="medium">
                                  {med.main_name}
                                </Typography>
                                {selectedDRLZMedication?.main_name === med.main_name && (
                                  <CheckCircle color="primary" fontSize="small" />
                                )}
                              </Box>
                            }
                            secondary={
                              <Box>
                                {med.form && (
                                  <Typography variant="body2" color="text.secondary">
                                    Form: {med.form}
                                  </Typography>
                                )}
                                {med.manufacturer && (
                                  <Typography variant="caption" color="text.secondary">
                                    Manufacturer: {med.manufacturer}
                                  </Typography>
                                )}
                                {med.registration_number && (
                                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                                    Registration: {med.registration_number}
                                  </Typography>
                                )}
                              </Box>
                            }
                          />
                          <ListItemSecondaryAction>
                            <Box sx={{ display: 'flex', gap: 0.5 }}>
                              {med.instruction_link && (
                                <IconButton
                                  size="small"
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    window.open(med.instruction_link, '_blank')
                                  }}
                                  title="View instruction"
                                >
                                  <Description fontSize="small" />
                                </IconButton>
                              )}
                            </Box>
                          </ListItemSecondaryAction>
                        </ListItem>
                      </Box>
                    ))}
                    {drlzResults.medications.length > 5 && (
                      <Typography variant="caption" color="text.secondary" sx={{ pl: 2 }}>
                        Showing first 5 results of {drlzResults.medications.length} found
                      </Typography>
                    )}
                  </List>
                </AccordionDetails>
              </Accordion>
            )}

            {selectedDRLZMedication && (
              <Alert severity="success" sx={{ mb: 2 }}>
                <Box>
                  <Typography variant="body2" fontWeight="medium">
                    Selected: <strong>{selectedDRLZMedication.main_name}</strong>
                    {selectedDRLZMedication.form && ` - ${selectedDRLZMedication.form}`}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                    ✓ Description auto-filled from Ukrainian medicine registry
                    {selectedDRLZMedication.instruction_link && ' • ✓ Instruction link added'}
                    • ✓ Tabletki.ua search link generated
                  </Typography>
                </Box>
              </Alert>
            )}

            {drlzError && (
              <Alert severity="warning" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  Unable to search medicine registry. You can still add the medication manually.
                </Typography>
              </Alert>
            )}
          </Box>

          {/* Description */}
          <TextField
            {...register('description')}
            label="Description (optional)"
            placeholder="Additional details about the medication..."
            multiline
            rows={2}
            fullWidth
            sx={{ mb: 3 }}
            helperText="Auto-filled with manufacturer info when selecting from Ukrainian registry above"
          />

          {/* Quantity */}
          <TextField
            {...register('quantity', { valueAsNumber: true })}
            label="Initial Quantity"
            type="number"
            inputProps={{ min: 0 }}
            placeholder="How many do you have?"
            fullWidth
            error={!!errors.quantity}
            helperText={errors.quantity?.message || 'Number of items you currently have'}
            sx={{ mb: 3 }}
          />

          {/* Barcode */}
          <TextField
            value={barcode}
            onChange={(e) => setBarcode(e.target.value)}
            label="Barcode (optional)"
            placeholder="Scanned package barcode"
            fullWidth
            inputProps={{ inputMode: 'numeric' }}
            sx={{ mb: 3 }}
            helperText="Saved so scanning this package later updates its quantity"
          />

          {/* Notes */}
          <TextField
            {...register('notes')}
            label="Notes"
            placeholder="Dosage instructions, expiry date, storage notes..."
            multiline
            rows={3}
            fullWidth
            sx={{ mb: 3 }}
          />

          {/* Tags */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
              Tags (optional)
            </Typography>
            
            <TextField
              value={currentTag}
              onChange={(e) => setCurrentTag(e.target.value)}
              onKeyDown={handleAddTag}
              placeholder="Type a tag and press Enter (e.g., pain relief, vitamins)"
              fullWidth
              size="small"
              sx={{ mb: 2 }}
            />
            
            {/* Tag suggestions */}
            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                Quick add:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {['pain relief', 'vitamins', 'antibiotics', 'allergy', 'cold & flu'].map((suggestion) => (
                  <Chip
                    key={suggestion}
                    label={suggestion}
                    variant="outlined"
                    size="small"
                    clickable
                    onClick={() => addSuggestedTag(suggestion)}
                    icon={<Add fontSize="small" />}
                    sx={{
                      '&:hover': {
                        backgroundColor: 'primary.50',
                        borderColor: 'primary.main',
                      }
                    }}
                  />
                ))}
              </Box>
            </Box>
            
            {/* Selected tags */}
            {tags.length > 0 && (
              <Box>
                <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                  Selected tags:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {tags.map((tag) => (
                    <Chip
                      key={tag}
                      label={`#${tag}`}
                      onDelete={() => handleRemoveTag(tag)}
                      color="primary"
                      variant="outlined"
                      size="small"
                      icon={<LocalOffer fontSize="small" />}
                    />
                  ))}
                </Box>
              </Box>
            )}
          </Box>
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 3, gap: 2 }}>
        <Button
          onClick={handleClose}
          variant="outlined"
          sx={{ minWidth: 100 }}
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit(onSubmit)}
          variant="contained"
          disabled={createMutation.isPending}
          startIcon={createMutation.isPending ? <CircularProgress size={16} color="inherit" /> : <Add />}
          sx={{
            minWidth: 140,
            background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%)',
            },
          }}
        >
          {createMutation.isPending ? 'Adding...' : 'Add Medication'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
