import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'

export default function ForbiddenPage() {
  return (
    <div className="flex h-full items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold">403</h1>
        <p className="mt-2 text-muted-foreground">You don't have permission to access this page.</p>
        <Button asChild className="mt-4">
          <Link to="/dashboard">Back to Dashboard</Link>
        </Button>
      </div>
    </div>
  )
}
