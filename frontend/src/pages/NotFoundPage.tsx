import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'

export default function NotFoundPage() {
  return (
    <div className="flex h-full items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold">404</h1>
        <p className="mt-2 text-muted-foreground">Page not found.</p>
        <Button asChild className="mt-4">
          <Link to="/dashboard">Back to Dashboard</Link>
        </Button>
      </div>
    </div>
  )
}
