// @ts-nocheck
import { useEffect, useRef, useState, useCallback } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Button,
  IconButton,
  Typography,
  TextField,
  CircularProgress,
  Alert,
  Chip,
  Divider,
} from '@mui/material'
import {
  Close,
  QrCodeScanner,
  Add,
  Remove,
  Replay,
  CheckCircle,
  Keyboard,
  CameraAlt,
} from '@mui/icons-material'
import { medicationApi } from '../lib/api'

interface ScanMedicationDialogProps {
  isOpen: boolean
  onClose: () => void
  householdId: number
  // Called when the user chooses to create a medication for an unknown barcode.
  onCreateForBarcode: (barcode: string) => void
}

export default function ScanMedicationDialog({
  isOpen,
  onClose,
  householdId,
  onCreateForBarcode,
}: ScanMedicationDialogProps) {
  const queryClient = useQueryClient()

  const [barcode, setBarcode] = useState('')
  const [manualEntry, setManualEntry] = useState('')
  const [useManual, setUseManual] = useState(false)
  const [cameraError, setCameraError] = useState('')
  const [amount, setAmount] = useState(1)

  const videoRef = useRef(null)
  const streamRef = useRef(null)
  const detectorRef = useRef(null)
  const rafRef = useRef(null)
  const runningRef = useRef(false)

  const barcodeDetectorSupported =
    typeof window !== 'undefined' && 'BarcodeDetector' in window

  // Look up the barcode once we have one
  const {
    data: lookup,
    isLoading: isLookingUp,
    error: lookupError,
  } = useQuery({
    queryKey: ['med-lookup', householdId, barcode],
    queryFn: () => medicationApi.lookupByBarcode(householdId, barcode),
    enabled: !!barcode && isOpen,
    staleTime: 0,
  })

  const foundMedication = lookup?.found ? lookup.medication : null

  const stopCamera = useCallback(() => {
    runningRef.current = false
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current)
      rafRef.current = null
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop())
      streamRef.current = null
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null
    }
  }, [])

  const scanLoop = useCallback(async () => {
    if (!runningRef.current || !detectorRef.current || !videoRef.current) return
    try {
      const codes = await detectorRef.current.detect(videoRef.current)
      if (codes && codes.length > 0 && codes[0].rawValue) {
        const value = String(codes[0].rawValue).trim()
        if (value) {
          stopCamera()
          setBarcode(value)
          return
        }
      }
    } catch {
      // Ignore transient detection errors and keep scanning
    }
    if (runningRef.current) {
      rafRef.current = requestAnimationFrame(scanLoop)
    }
  }, [stopCamera])

  const startCamera = useCallback(async () => {
    if (!barcodeDetectorSupported) {
      setUseManual(true)
      return
    }
    setCameraError('')
    try {
      if (!detectorRef.current) {
        try {
          detectorRef.current = new window.BarcodeDetector({
            formats: ['ean_13', 'ean_8', 'upc_a', 'upc_e', 'code_128', 'code_39', 'qr_code'],
          })
        } catch {
          detectorRef.current = new window.BarcodeDetector()
        }
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' },
        audio: false,
      })
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        await videoRef.current.play()
      }
      runningRef.current = true
      rafRef.current = requestAnimationFrame(scanLoop)
    } catch (err) {
      setCameraError(
        'Unable to access the camera. You can enter the barcode manually instead.'
      )
      setUseManual(true)
    }
  }, [barcodeDetectorSupported, scanLoop])

  // Manage camera based on dialog / barcode / manual state
  useEffect(() => {
    if (isOpen && !barcode && !useManual) {
      startCamera()
    }
    return () => {
      stopCamera()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, barcode, useManual])

  const incrementMutation = useMutation({
    mutationFn: (amt: number) =>
      medicationApi.increment(householdId, foundMedication.id, amt),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['medications', householdId] })
      queryClient.invalidateQueries({ queryKey: ['med-lookup', householdId, barcode] })
    },
  })

  const decrementMutation = useMutation({
    mutationFn: (amt: number) =>
      medicationApi.decrement(householdId, foundMedication.id, amt),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['medications', householdId] })
      queryClient.invalidateQueries({ queryKey: ['med-lookup', householdId, barcode] })
    },
  })

  const resetToScan = () => {
    stopCamera()
    setBarcode('')
    setManualEntry('')
    setAmount(1)
    incrementMutation.reset()
    decrementMutation.reset()
    setUseManual(false)
  }

  const handleClose = () => {
    stopCamera()
    setBarcode('')
    setManualEntry('')
    setAmount(1)
    setUseManual(false)
    setCameraError('')
    incrementMutation.reset()
    decrementMutation.reset()
    onClose()
  }

  const handleManualSubmit = (e) => {
    e.preventDefault()
    const value = manualEntry.trim()
    if (value) {
      stopCamera()
      setBarcode(value)
    }
  }

  const busy = incrementMutation.isPending || decrementMutation.isPending
  const canDecrement = foundMedication && foundMedication.quantity >= amount

  return (
    <Dialog
      open={isOpen}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{ sx: { borderRadius: 3 } }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <QrCodeScanner color="primary" />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Scan Medication
            </Typography>
          </Box>
          <IconButton onClick={handleClose} aria-label="Close dialog">
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ pb: 2 }}>
        {/* Scanning stage */}
        {!barcode && (
          <Box>
            {!useManual && barcodeDetectorSupported && (
              <>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Point your camera at the barcode on the medication package.
                </Typography>
                <Box
                  sx={{
                    position: 'relative',
                    width: '100%',
                    aspectRatio: '4 / 3',
                    bgcolor: 'black',
                    borderRadius: 2,
                    overflow: 'hidden',
                    mb: 2,
                  }}
                >
                  <video
                    ref={videoRef}
                    playsInline
                    muted
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                  {/* Scan frame overlay */}
                  <Box
                    sx={{
                      position: 'absolute',
                      top: '25%',
                      left: '10%',
                      width: '80%',
                      height: '50%',
                      border: '2px solid rgba(255,255,255,0.8)',
                      borderRadius: 2,
                      boxShadow: '0 0 0 9999px rgba(0,0,0,0.25)',
                    }}
                  />
                </Box>
              </>
            )}

            {cameraError && (
              <Alert severity="warning" sx={{ mb: 2 }}>
                {cameraError}
              </Alert>
            )}

            {!barcodeDetectorSupported && !useManual && (
              <Alert severity="info" sx={{ mb: 2 }}>
                Live barcode scanning isn't supported by this browser. Enter the
                barcode number manually below.
              </Alert>
            )}

            {/* Manual entry */}
            {(useManual || !barcodeDetectorSupported) ? (
              <Box component="form" onSubmit={handleManualSubmit}>
                <TextField
                  value={manualEntry}
                  onChange={(e) => setManualEntry(e.target.value)}
                  label="Barcode number"
                  placeholder="e.g. 4820000000000"
                  fullWidth
                  autoFocus
                  inputProps={{ inputMode: 'numeric' }}
                  sx={{ mb: 2 }}
                />
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Button
                    type="submit"
                    variant="contained"
                    startIcon={<QrCodeScanner />}
                    disabled={!manualEntry.trim()}
                  >
                    Look up
                  </Button>
                  {barcodeDetectorSupported && (
                    <Button
                      variant="outlined"
                      startIcon={<CameraAlt />}
                      onClick={() => {
                        setUseManual(false)
                        setCameraError('')
                      }}
                    >
                      Use camera
                    </Button>
                  )}
                </Box>
              </Box>
            ) : (
              <Button
                variant="text"
                startIcon={<Keyboard />}
                onClick={() => {
                  stopCamera()
                  setUseManual(true)
                }}
              >
                Enter barcode manually
              </Button>
            )}
          </Box>
        )}

        {/* Result stage */}
        {barcode && (
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Chip
                icon={<QrCodeScanner />}
                label={barcode}
                variant="outlined"
                color="primary"
              />
              <Button size="small" startIcon={<Replay />} onClick={resetToScan}>
                Scan again
              </Button>
            </Box>

            {isLookingUp && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, py: 2 }}>
                <CircularProgress size={20} />
                <Typography color="text.secondary">Looking up barcode…</Typography>
              </Box>
            )}

            {lookupError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                Failed to look up the barcode. Please try again.
              </Alert>
            )}

            {/* Existing medication → adjust quantity */}
            {!isLookingUp && foundMedication && (
              <Box>
                <Alert
                  icon={<CheckCircle fontSize="inherit" />}
                  severity="success"
                  sx={{ mb: 2 }}
                >
                  This medication is already in your inventory.
                </Alert>

                <Box
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: 'divider',
                    mb: 2,
                  }}
                >
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    {foundMedication.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    In stock:{' '}
                    <strong>
                      {foundMedication.quantity}{' '}
                      {foundMedication.quantity === 1 ? 'item' : 'items'}
                    </strong>
                  </Typography>
                </Box>

                {(incrementMutation.isError || decrementMutation.isError) && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {incrementMutation.error?.response?.data?.detail ||
                      decrementMutation.error?.response?.data?.detail ||
                      'Failed to update quantity. Please try again.'}
                  </Alert>
                )}

                {/* Amount stepper */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    Amount:
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <IconButton
                      size="small"
                      onClick={() => setAmount((a) => Math.max(1, a - 1))}
                      disabled={amount <= 1}
                    >
                      <Remove fontSize="small" />
                    </IconButton>
                    <Typography sx={{ minWidth: 24, textAlign: 'center', fontWeight: 600 }}>
                      {amount}
                    </Typography>
                    <IconButton size="small" onClick={() => setAmount((a) => a + 1)}>
                      <Add fontSize="small" />
                    </IconButton>
                  </Box>
                </Box>

                <Divider sx={{ mb: 2 }} />

                <Box sx={{ display: 'flex', gap: 2 }}>
                  <Button
                    fullWidth
                    variant="contained"
                    color="success"
                    startIcon={<Add />}
                    disabled={busy}
                    onClick={() => incrementMutation.mutate(amount)}
                  >
                    Add {amount}
                  </Button>
                  <Button
                    fullWidth
                    variant="outlined"
                    color="error"
                    startIcon={<Remove />}
                    disabled={busy || !canDecrement}
                    onClick={() => decrementMutation.mutate(amount)}
                  >
                    Subtract {amount}
                  </Button>
                </Box>
                {!canDecrement && foundMedication.quantity < amount && (
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                    Not enough in stock to subtract {amount}.
                  </Typography>
                )}
              </Box>
            )}

            {/* Unknown barcode → suggest creating */}
            {!isLookingUp && lookup && !foundMedication && (
              <Box>
                <Alert severity="info" sx={{ mb: 2 }}>
                  No medication with this barcode was found in your inventory.
                </Alert>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Would you like to add it as a new medication? The barcode will be
                  saved so future scans update it automatically.
                </Typography>
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<Add />}
                  onClick={() => {
                    const code = barcode
                    handleClose()
                    onCreateForBarcode(code)
                  }}
                  sx={{
                    background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%)',
                    },
                  }}
                >
                  Create new medication
                </Button>
              </Box>
            )}
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={handleClose} variant="outlined">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  )
}
