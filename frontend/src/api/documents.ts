import { api } from './client'
import type { DocumentRead } from './types'

export async function listDocuments(estateId: number): Promise<DocumentRead[]> {
  const { data } = await api.get<DocumentRead[]>(`/api/estates/${estateId}/documents`)
  return data
}

export interface UploadDocumentInput {
  file: File
  stageId?: number | null
  description?: string | null
}

export async function uploadDocument(
  estateId: number,
  input: UploadDocumentInput,
): Promise<DocumentRead> {
  const form = new FormData()
  form.append('file', input.file)
  const params: Record<string, unknown> = {}
  if (input.stageId != null) params.stage_id = input.stageId
  if (input.description) params.description = input.description
  const { data } = await api.post<DocumentRead>(
    `/api/estates/${estateId}/documents`,
    form,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
      params,
    },
  )
  return data
}

export async function downloadDocument(docId: number): Promise<string> {
  const response = await api.get<Blob>(`/api/documents/${docId}`, {
    responseType: 'blob',
  })
  return URL.createObjectURL(response.data)
}

export async function deleteDocument(docId: number): Promise<void> {
  await api.delete(`/api/documents/${docId}`)
}
