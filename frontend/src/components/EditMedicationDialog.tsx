// @ts-nocheck
import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { z } from 'zod'
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
  Link
} from '@mui/material'
import { 
  Close, 
  Check, 
  LocalOffer, 
  ExitToApp, 
  Assignment, 
  Search 
} from '@mui/icons-material'
import { Medication } from '../types'
import api from '../lib/api'

const EditMedicationSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  quantity: z.number().min(0, 'Quantity must be non-negative'),
  notes: z.string().optional(),
})

type EditMedicationForm = z.infer<typeof EditMedicationSchema>

interface EditMedicationDialogProps {
  isOpen: boolean
  onClose: () => void
  medication: Medication
  householdId: number
}

export default function EditMedicationDialog({ 
  isOpen, 
  onClose, 
  medication, 
  householdId 
}: EditMedicationDialogProps) {
  const queryClient = useQueryClient()
  const [tags, setTags] = useState(medication.tags)
  const [currentTag, setCurrentTag] = useState('')

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(EditMedicationSchema),
    defaultValues: {
      name: medication.name,
      quantity: medication.quantity,
      notes: medication.notes || '',
    },
  })

  // Reset form when medication changes or dialog opens
  useEffect(() => {
    if (isOpen) {
      reset({
        name: medication.name,
        quantity: medication.quantity,
        notes: medication.notes || '',
      })
      setTags(medication.tags)
      setCurrentTag('')
    }
  }, [isOpen, medication, reset])

  const updateMutation = useMutation({
    mutationFn: async (data) => {
      const response = await api.patch(`/households/${householdId}/medications/${medication.id}/`, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['medications', householdId] })
      onClose()
    },
  })

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

  const onSubmit = (data) => {
    const updateData = {
      ...data,
      tags
    }
    updateMutation.mutate(updateData)
  }

  return (
    <Dialog
      open={isOpen}
      onClose={onClose}
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
              Edit Medication
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              Update medication details
            </Typography>
          </Box>
          <IconButton
            onClick={onClose}
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
          {updateMutation.isError && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {updateMutation.error?.response?.data?.detail || 'Failed to update medication. Please try again.'}
            </Alert>
          )}

          {/* Name */}
          <TextField
            {...register('name')}
            label="Medication Name"
            placeholder="e.g., Ibuprofen 200mg, Vitamin D3, Aspirin..."
            fullWidth
            required
            error={!!errors.name}
            helperText={errors.name?.message}
            sx={{ mb: 3 }}
          />

          {/* Quantity */}
          <TextField
            {...register('quantity', { valueAsNumber: true })}
            label="Quantity"
            type="number"
            inputProps={{ min: 0 }}
            placeholder="How many do you have?"
            fullWidth
            error={!!errors.quantity}
            helperText={errors.quantity?.message || 'Number of items you currently have'}
            sx={{ mb: 3 }}
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

          {/* DRLZ Information (Read-Only) */}
          {(medication.description || medication.drlz_link || medication.drlz_instruction_link || medication.tabletki_link) && (
            <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 2, border: '1px solid', borderColor: 'grey.200' }}>
              <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Assignment fontSize="small" />
                Registry Information
              </Typography>
              
              {medication.description && (
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  <strong>Description:</strong> {medication.description}
                </Typography>
              )}
              
              {(medication.drlz_link || medication.drlz_instruction_link || medication.tabletki_link) && (
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                    External Links:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {medication.drlz_link && (
                      <Link
                        href={medication.drlz_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        sx={{ fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: 0.5 }}
                      >
                        DRLZ Registry <ExitToApp fontSize="inherit" />
                      </Link>
                    )}
                    {medication.drlz_instruction_link && (
                      <Link
                        href={medication.drlz_instruction_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        sx={{ fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: 0.5 }}
                      >
                        Instruction <ExitToApp fontSize="inherit" />
                      </Link>
                    )}
                    {medication.tabletki_link && (
                      <Link
                        href={medication.tabletki_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        sx={{ fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: 0.5 }}
                      >
                        Tabletki.ua <ExitToApp fontSize="inherit" />
                      </Link>
                    )}
                  </Box>
                </Box>
              )}
            </Box>
          )}

          {/* Tags */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
              Tags (optional)
            </Typography>
            
            <TextField
              value={currentTag}
              onChange={(e) => setCurrentTag(e.target.value)}
              onKeyDown={handleAddTag}
              placeholder="Type a tag and press Enter"
              fullWidth
              size="small"
              sx={{ mb: 2 }}
            />
            
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

          {/* External Links (Read-only) */}
          {(medication.drlz_link || medication.tabletki_link || medication.drlz_instruction_link) && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                External Links
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {medication.drlz_link && (
                  <Link
                    href={medication.drlz_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    underline="none"
                  >
                    <Chip
                      icon={<ExitToApp fontSize="small" />}
                      label="DRLZ"
                      variant="outlined"
                      size="small"
                      clickable
                      sx={{
                        backgroundColor: 'blue.50',
                        borderColor: 'blue.200',
                        color: 'blue.700',
                        '&:hover': {
                          backgroundColor: 'blue.100',
                          borderColor: 'blue.300',
                        },
                      }}
                    />
                  </Link>
                )}
                {medication.drlz_instruction_link && (
                  <Link
                    href={medication.drlz_instruction_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    underline="none"
                  >
                    <Chip
                      icon={<Assignment fontSize="small" />}
                      label="Instructions"
                      variant="outlined"
                      size="small"
                      clickable
                      sx={{
                        backgroundColor: 'green.50',
                        borderColor: 'green.200',
                        color: 'green.700',
                        '&:hover': {
                          backgroundColor: 'green.100',
                          borderColor: 'green.300',
                        },
                      }}
                    />
                  </Link>
                )}
                {medication.tabletki_link && (
                  <Link
                    href={medication.tabletki_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    underline="none"
                  >
                    <Chip
                      icon={<Search fontSize="small" />}
                      label="Tabletki"
                      variant="outlined"
                      size="small"
                      clickable
                      sx={{
                        backgroundColor: 'purple.50',
                        borderColor: 'purple.200',
                        color: 'purple.700',
                        '&:hover': {
                          backgroundColor: 'purple.100',
                          borderColor: 'purple.300',
                        },
                      }}
                    />
                  </Link>
                )}
              </Box>
            </Box>
          )}
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 3, gap: 2 }}>
        <Button
          onClick={onClose}
          variant="outlined"
          sx={{ minWidth: 100 }}
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit(onSubmit)}
          variant="contained"
          disabled={updateMutation.isPending}
          startIcon={updateMutation.isPending ? <CircularProgress size={16} color="inherit" /> : <Check />}
          sx={{
            minWidth: 140,
            background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%)',
            },
          }}
        >
          {updateMutation.isPending ? 'Updating...' : 'Update Medication'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
