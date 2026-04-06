/**
 * Converts numeric row/col to Excel-style cell notation and displays it.
 * col 1 = A, 2 = B, ... 26 = Z, 27 = AA, 28 = AB, etc.
 */

interface CellReferenceProps {
  row: number
  col: number
  className?: string
}

function colToLetter(col: number): string {
  let result = ''
  let c = col
  while (c > 0) {
    c -= 1
    result = String.fromCharCode(65 + (c % 26)) + result
    c = Math.floor(c / 26)
  }
  return result
}

export function cellToExcel(row: number, col: number): string {
  return `${colToLetter(col)}${row}`
}

export function CellReference({ row, col, className }: CellReferenceProps) {
  return (
    <code className={className ?? 'rounded bg-muted px-1.5 py-0.5 text-xs font-mono'}>
      {cellToExcel(row, col)}
    </code>
  )
}
