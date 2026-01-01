import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../lib/api'
import { 
  Medication, 
  MedicationList, 
  CreateMedication, 
  StorePricesResponse 
} from '../types'

export function useMedications(householdId: number, search?: string, tag?: string) {
  return useQuery({
    queryKey: ['medications', householdId, search, tag],
    queryFn: async (): Promise<MedicationList> => {
      const params = new URLSearchParams()
      if (search) params.append('search', search)
      if (tag) params.append('tag', tag)
      
      const response = await api.get(
        `/households/${householdId}/medications?${params.toString()}`
      )
      return response.data
    },
    enabled: !!householdId,
  })
}

export function useMedication(householdId: number, medicationId: number) {
  return useQuery({
    queryKey: ['medication', householdId, medicationId],
    queryFn: async (): Promise<Medication> => {
      const response = await api.get(
        `/households/${householdId}/medications/${medicationId}`
      )
      return response.data
    },
    enabled: !!householdId && !!medicationId,
  })
}

export function useCreateMedication(householdId: number) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (medicationData: CreateMedication): Promise<Medication> => {
      const response = await api.post(
        `/households/${householdId}/medications`,
        medicationData
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ 
        queryKey: ['medications', householdId] 
      })
    },
  })
}

export function useUpdateMedication(householdId: number, medicationId: number) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (updates: Partial<Medication>): Promise<Medication> => {
      const response = await api.patch(
        `/households/${householdId}/medications/${medicationId}`,
        updates
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ 
        queryKey: ['medications', householdId] 
      })
      queryClient.invalidateQueries({ 
        queryKey: ['medication', householdId, medicationId] 
      })
    },
  })
}

export function useDecrementMedication(householdId: number) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ medicationId, amount = 1 }: { 
      medicationId: number
      amount?: number 
    }): Promise<Medication> => {
      const response = await api.post(
        `/households/${householdId}/medications/${medicationId}/decrement`,
        { amount }
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ 
        queryKey: ['medications', householdId] 
      })
    },
  })
}

export function useDeleteMedication(householdId: number) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (medicationId: number): Promise<void> => {
      await api.delete(`/households/${householdId}/medications/${medicationId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ 
        queryKey: ['medications', householdId] 
      })
    },
  })
}

export function useStorePrices(householdId: number, medicationId: number, enabled = false) {
  return useQuery({
    queryKey: ['storePrices', householdId, medicationId],
    queryFn: async (): Promise<StorePricesResponse> => {
      const response = await api.get(
        `/households/${householdId}/medications/${medicationId}/store-prices`
      )
      return response.data
    },
    enabled: !!householdId && !!medicationId && enabled,
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes since prices change
    gcTime: 10 * 60 * 1000, // Keep in cache for 10 minutes
  })
}

export function useRefreshLinks(householdId: number, medicationId: number) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (): Promise<{ message: string; task_id: string }> => {
      const response = await api.post(
        `/households/${householdId}/medications/${medicationId}/resolve-links`
      )
      return response.data
    },
    onSuccess: () => {
      // Invalidate medication data after link resolution
      queryClient.invalidateQueries({ 
        queryKey: ['medications', householdId] 
      })
      queryClient.invalidateQueries({ 
        queryKey: ['medication', householdId, medicationId] 
      })
    },
  })
}
