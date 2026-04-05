import * as React from 'react'
import { cn } from '@/lib/utils'

export interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string
}

export const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(({ className, label, id, ...props }, ref) => {
  const generatedId = React.useId()
  const inputId = id ?? generatedId
  return (
    <div className="flex items-center gap-2">
      <input
        ref={ref}
        id={inputId}
        type="checkbox"
        className={cn(
          'h-4 w-4 rounded border border-input bg-background text-primary focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
          className,
        )}
        {...props}
      />
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium leading-none">
          {label}
        </label>
      )}
    </div>
  )
})
Checkbox.displayName = 'Checkbox'
