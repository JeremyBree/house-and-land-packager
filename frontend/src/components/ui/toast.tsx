import * as React from 'react'
import * as ToastPrimitive from '@radix-ui/react-toast'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'

type ToastVariant = 'default' | 'destructive' | 'success'

export interface ToastMessage {
  id: number
  title?: string
  description?: string
  variant?: ToastVariant
}

interface ToastContextValue {
  toast: (msg: Omit<ToastMessage, 'id'>) => void
}

const ToastContext = React.createContext<ToastContextValue | undefined>(undefined)

export function useToast(): ToastContextValue {
  const ctx = React.useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<ToastMessage[]>([])

  const toast = React.useCallback((msg: Omit<ToastMessage, 'id'>) => {
    setToasts((prev) => [...prev, { ...msg, id: Date.now() + Math.random() }])
  }, [])

  const dismiss = (id: number) => setToasts((prev) => prev.filter((t) => t.id !== id))

  return (
    <ToastContext.Provider value={{ toast }}>
      <ToastPrimitive.Provider swipeDirection="right">
        {children}
        {toasts.map((t) => (
          <ToastPrimitive.Root
            key={t.id}
            onOpenChange={(open) => !open && dismiss(t.id)}
            duration={5000}
            className={cn(
              'group pointer-events-auto relative flex w-full items-center justify-between gap-4 overflow-hidden rounded-md border p-4 pr-8 shadow-lg transition-all',
              t.variant === 'destructive' && 'border-destructive bg-destructive text-destructive-foreground',
              t.variant === 'success' && 'border-emerald-500 bg-emerald-50 text-emerald-900',
              (!t.variant || t.variant === 'default') && 'border bg-background text-foreground',
            )}
          >
            <div className="grid gap-1">
              {t.title && <ToastPrimitive.Title className="text-sm font-semibold">{t.title}</ToastPrimitive.Title>}
              {t.description && <ToastPrimitive.Description className="text-sm opacity-90">{t.description}</ToastPrimitive.Description>}
            </div>
            <ToastPrimitive.Close className="absolute right-2 top-2 rounded-md p-1 opacity-70 transition-opacity hover:opacity-100">
              <X className="h-4 w-4" />
            </ToastPrimitive.Close>
          </ToastPrimitive.Root>
        ))}
        <ToastPrimitive.Viewport className="fixed bottom-0 right-0 z-[100] flex max-h-screen w-full flex-col-reverse p-4 sm:bottom-4 sm:right-4 sm:top-auto sm:flex-col md:max-w-[420px] gap-2" />
      </ToastPrimitive.Provider>
    </ToastContext.Provider>
  )
}
