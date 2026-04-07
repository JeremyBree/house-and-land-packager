import { api } from './client'

// ---- Types -------------------------------------------------------------------

export interface PendingExtractionRead {
  extraction_id: number
  file_name: string
  file_path: string
  uploaded_by: number
  status: string
  extracted_data: Record<string, unknown>
  extraction_notes: string | null
  reviewed_by: number | null
  reviewed_at: string | null
  review_notes: string | null
  ingestion_log_id: number | null
  created_at: string
  updated_at: string
}

// ---- API calls ---------------------------------------------------------------

export async function uploadPdf(file: File): Promise<PendingExtractionRead> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post<PendingExtractionRead>(
    '/api/pdf-ingestion/upload',
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  )
  return data
}

export async function listExtractions(
  status?: string,
): Promise<PendingExtractionRead[]> {
  const params: Record<string, string> = {}
  if (status) params.status = status
  const { data } = await api.get<PendingExtractionRead[]>(
    '/api/pdf-ingestion/extractions',
    { params },
  )
  return data
}

export async function getExtraction(
  id: number,
): Promise<PendingExtractionRead> {
  const { data } = await api.get<PendingExtractionRead>(
    `/api/pdf-ingestion/extractions/${id}`,
  )
  return data
}

export async function approveExtraction(
  id: number,
  reviewNotes?: string,
): Promise<PendingExtractionRead> {
  const { data } = await api.post<PendingExtractionRead>(
    `/api/pdf-ingestion/extractions/${id}/approve`,
    { review_notes: reviewNotes || null },
  )
  return data
}

export async function rejectExtraction(
  id: number,
  reviewNotes?: string,
): Promise<PendingExtractionRead> {
  const { data } = await api.post<PendingExtractionRead>(
    `/api/pdf-ingestion/extractions/${id}/reject`,
    { review_notes: reviewNotes || null },
  )
  return data
}

export async function deleteExtraction(id: number): Promise<void> {
  await api.delete(`/api/pdf-ingestion/extractions/${id}`)
}
