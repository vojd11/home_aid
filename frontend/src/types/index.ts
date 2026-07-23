import { z } from 'zod'

// Auth schemas
export const LoginSchema = z.object({
  email: z.string().email('Invalid email format'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
})

export const RegisterSchema = z.object({
  email: z.string().email('Invalid email format'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
})

export const UserSchema = z.object({
  id: z.number(),
  email: z.string().email(),
  created_at: z.string(),
  last_login: z.string().optional(),
})

// Household schemas
export const HouseholdSchema = z.object({
  id: z.number(),
  name: z.string(),
  role: z.enum(['owner', 'editor', 'viewer']),
  created_at: z.string(),
})

// Medication schemas
export const MedicationSchema = z.object({
  id: z.number(),
  name: z.string(),
  quantity: z.number(),
  barcode: z.string().nullable().optional(),
  description: z.string().optional(),
  drlz_link: z.string().url().optional(),
  drlz_instruction_link: z.string().url().optional(),
  tabletki_link: z.string().url().optional(),
  tags: z.array(z.string()),
  notes: z.string().optional(),
  created_at: z.string(),
  updated_at: z.string(),
})

export const MedicationListSchema = z.object({
  medications: z.array(MedicationSchema),
  total: z.number(),
  next_cursor: z.number().optional(),
  has_more: z.boolean(),
})

export const CreateMedicationSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  quantity: z.number().min(0, 'Quantity must be non-negative').default(0),
  barcode: z.string().optional(),
  description: z.string().optional(),
  notes: z.string().optional(),
  drlz_link: z.string().url().optional(),
  drlz_instruction_link: z.string().url().optional(),
  tabletki_link: z.string().url().optional(),
})

// DRLZ schemas
export const DRLZMedicationSchema = z.object({
  main_name: z.string(),
  form: z.string().optional(),
  registration_number: z.string().optional(),
  manufacturer: z.string().optional(),
  medication_link: z.string().url().optional(),
  instruction_link: z.string().url().optional(),
})

export const DRLZSearchResultSchema = z.object({
  query: z.string(),
  medications: z.array(DRLZMedicationSchema),
  total: z.number(),
})

// Store price schemas
export const StorePriceSchema = z.object({
  store_name: z.string(),
  price: z.number().optional(),
  currency: z.string().default('грн'),
  link: z.string().url().optional(),
  status: z.enum(['success', 'not_found', 'error']),
})

export const StorePricesResponseSchema = z.object({
  medication_id: z.number(),
  medication_name: z.string(),
  stores: z.array(StorePriceSchema),
  total_stores: z.number(),
  last_updated: z.string().optional(),
})

// Type exports
export type LoginForm = z.infer<typeof LoginSchema>
export type RegisterForm = z.infer<typeof RegisterSchema>
export type User = z.infer<typeof UserSchema>
export type Household = z.infer<typeof HouseholdSchema>
export type Medication = z.infer<typeof MedicationSchema>
export type MedicationList = z.infer<typeof MedicationListSchema>
export type CreateMedication = z.infer<typeof CreateMedicationSchema>
export type DRLZMedication = z.infer<typeof DRLZMedicationSchema>
export type DRLZSearchResult = z.infer<typeof DRLZSearchResultSchema>
export type StorePrice = z.infer<typeof StorePriceSchema>
export type StorePricesResponse = z.infer<typeof StorePricesResponseSchema>
