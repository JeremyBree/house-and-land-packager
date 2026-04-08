import { api } from './client'

export interface CsvUploadResult {
  created: number
  skipped: number
  errors: { row: number; error: string }[]
}

export async function uploadCsv(
  endpoint: string,
  file: File,
): Promise<CsvUploadResult> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post<CsvUploadResult>(endpoint, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}
