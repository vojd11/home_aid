// @ts-nocheck
import { useState } from 'react'
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
  Alert,
  CircularProgress
} from '@mui/material'
import { Close, Add, Info } from '@mui/icons-material'
import api from '../lib/api'

const CreateHouseholdSchema = z.object({
  name: z.string().min(1, 'Household name is required').max(100, 'Name must be less than 100 characters'),
})

interface CreateHouseholdDialogProps {
  isOpen: boolean
  onClose: () => void
}

export default function CreateHouseholdDialog({ isOpen, onClose }: CreateHouseholdDialogProps) {
  const queryClient = useQueryClient()

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(CreateHouseholdSchema),
  })

  const createMutation = useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/households/', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['households'] })
      handleClose()
    },
    onError: (error) => {
      console.error('Failed to create household:', error)
    },
  })

  const handleClose = () => {
    reset()
    onClose()
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
        }
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="h5" component="h2" sx={{ fontWeight: 600 }}>
              Create New Household
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              Set up a new household to manage medications
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
          {/* Household Name */}
          <TextField
            {...register('name')}
            label="Household Name"
            placeholder="e.g., Smith Family, Main Apartment, etc."
            fullWidth
            required
            autoFocus
            error={!!errors.name}
            helperText={errors.name?.message}
            sx={{ mb: 3 }}
          />

          {/* Info Alert */}
          <Alert 
            severity="info" 
            icon={<Info />}
            sx={{ mb: 2 }}
          >
            You'll be the owner of this household and can invite other members to help manage medications.
          </Alert>

          {/* Error Display */}
          {createMutation.isError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {createMutation.error?.response?.data?.detail || 'Failed to create household. Please try again.'}
            </Alert>
          )}
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 3, gap: 2 }}>
        <Button
          onClick={handleClose}
          variant="outlined"
          disabled={createMutation.isPending}
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
          {createMutation.isPending ? 'Creating...' : 'Create Household'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
