// @ts-nocheck
import React, { useState } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  IconButton,
  Alert,
  CircularProgress,
  Paper
} from '@mui/material'
import { Close, OpenInNew, Download, Article, Warning } from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
import { authApi } from '../lib/api'

interface InstructionViewerProps {
  isOpen: boolean
  onClose: () => void
  instructionUrl?: string
  medicationName?: string
}

interface ParsedInstruction {
  success: boolean
  url: string
  title: string
  html_content: string
  text_content: string
  content_length: number
  encoding: string
  error?: string
}

export default function InstructionViewer({ 
  isOpen, 
  onClose, 
  instructionUrl, 
  medicationName 
}: InstructionViewerProps) {
  // Function to decode Unicode escape sequences
  const decodeUnicodeText = (text: string): string => {
    if (!text) return text
    
    // Decode Unicode escape sequences like \u0421\u043a\u043b\u0430\u0434
    return text.replace(/\\u([0-9a-fA-F]{4})/g, (match, code) => {
      try {
        return String.fromCharCode(parseInt(code, 16))
      } catch {
        return match // Return original if can't decode
      }
    })
  }

  // Query to fetch and parse the MHT instruction
  const { 
    data: parsedInstruction, 
    isLoading, 
    error,
    refetch 
  } = useQuery<ParsedInstruction>({
    queryKey: ['instruction', instructionUrl],
    queryFn: async () => {
      if (!instructionUrl) throw new Error('No instruction URL provided')
      
      const response = await authApi.get('/instructions/parse-instruction', {
        params: { url: instructionUrl }
      })
      
      return response.data
    },
    enabled: isOpen && !!instructionUrl,
    retry: 1,
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  })

  const handleOpenExternal = () => {
    if (instructionUrl) {
      window.open(instructionUrl, '_blank')
    }
  }

  const handleDownload = () => {
    if (instructionUrl) {
      const link = document.createElement('a')
      link.href = instructionUrl
      link.download = `${medicationName}_instruction.mht`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  const renderInstructionContent = () => {
    if (isLoading) {
      return (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
          <CircularProgress size={40} sx={{ mb: 2 }} />
          <Typography variant="body2" color="text.secondary">
            Downloading and parsing instruction file...
          </Typography>
        </Box>
      )
    }

    if (error || (parsedInstruction && !parsedInstruction.success)) {
      const errorMessage = error?.message || parsedInstruction?.error || 'Unknown error'
      
      return (
        <Box sx={{ py: 2 }}>
          <Alert severity="error" sx={{ mb: 3 }}>
            <Typography variant="body1" gutterBottom>
              <strong>Failed to load instruction</strong>
            </Typography>
            <Typography variant="body2">
              {errorMessage}
            </Typography>
          </Alert>

          {/* Fallback options */}
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>
              Alternative Options
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', justifyContent: 'center' }}>
              <Button
                variant="outlined"
                startIcon={<OpenInNew />}
                onClick={handleOpenExternal}
                size="large"
              >
                Open Original File
              </Button>
              
              <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={handleDownload}
                size="large"
              >
                Download MHT File
              </Button>

              <Button
                variant="outlined"
                onClick={() => refetch()}
                size="large"
              >
                Try Again
              </Button>
            </Box>
          </Box>
        </Box>
      )
    }

    if (!parsedInstruction) {
      return (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Alert severity="warning">
            <Typography variant="body1">
              No instruction file is available for this medication.
            </Typography>
          </Alert>
        </Box>
      )
    }

    // Successfully parsed instruction
    return (
      <Box sx={{ py: 1 }}>
        {/* Instruction metadata */}
        <Box sx={{ mb: 2, p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Article color="primary" />
            {parsedInstruction.title}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Full HTML instruction ({parsedInstruction.content_length.toLocaleString()} characters)
          </Typography>
        </Box>

        {/* Instruction content - Always show full HTML */}
        <Paper elevation={1} sx={{ mb: 2 }}>
          <Box
            sx={{ 
              p: 3,
              maxHeight: '70vh', 
              overflow: 'auto',
              fontFamily: 'Arial, sans-serif',
              lineHeight: 1.6,
              '& h1, & h2, & h3': { color: 'primary.main', mt: 2, mb: 1 },
              '& p': { mb: 1 },
              '& b, & strong': { fontWeight: 600, color: 'primary.main' },
              '& table': { width: '100%', borderCollapse: 'collapse', mb: 2 },
              '& td, & th': { border: '1px solid #ddd', p: 1, textAlign: 'left' },
              '& th': { bgcolor: 'grey.100', fontWeight: 600 },
              '& img': { maxWidth: '100%', height: 'auto' },
              '& ul, & ol': { pl: 3, mb: 2 },
              '& li': { mb: 0.5 }
            }}
            dangerouslySetInnerHTML={{ __html: parsedInstruction.html_content }}
          />
        </Paper>

        {/* Action buttons */}
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mb: 2 }}>
          <Button
            variant="outlined"
            startIcon={<OpenInNew />}
            onClick={handleOpenExternal}
            size="small"
          >
            Open Original File
          </Button>
          
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={handleDownload}
            size="small"
          >
            Download MHT File
          </Button>
        </Box>
      </Box>
    )
  }

  return (
    <Dialog
      open={isOpen}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          maxHeight: '95vh'
        }
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="h5" component="h2" sx={{ fontWeight: 600 }}>
              Instruction for {medicationName}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              Official medication instruction from Ukrainian State Register of Medicines
            </Typography>
          </Box>
          <IconButton
            onClick={onClose}
            sx={{ 
              color: 'text.secondary',
              '&:hover': { backgroundColor: 'action.hover' }
            }}
            aria-label="Close instruction viewer"
          >
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ pb: 2 }}>
        {instructionUrl ? (
          renderInstructionContent()
        ) : (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <Alert severity="warning" icon={<Warning />}>
              <Typography variant="body1">
                No instruction file is available for this medication.
              </Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>
                The instruction may not be available in the registry, or the medication 
                may not be found in the Ukrainian State Register of Medicines.
              </Typography>
            </Alert>
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 3, gap: 2 }}>
        <Button
          onClick={onClose}
          variant="outlined"
          sx={{ minWidth: 100 }}
        >
          Close
        </Button>
        {instructionUrl && !isLoading && (
          <Button
            onClick={handleOpenExternal}
            variant="contained"
            startIcon={<OpenInNew />}
            sx={{
              minWidth: 140,
              background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%)',
              },
            }}
          >
            Open Original
          </Button>
        )}
      </DialogActions>
    </Dialog>
  )
}
