import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Checkbox } from '@/components/ui/checkbox'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { createUser, updateUser, updateUserRoles } from '@/api/users'
import { USER_ROLES, type UserRead, type UserRoleType } from '@/api/types'
import { useToast } from '@/components/ui/toast'
import { extractErrorMessage } from '@/api/client'

const createSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8, 'At least 8 characters'),
  first_name: z.string().min(1).max(100),
  last_name: z.string().min(1).max(100),
  job_title: z.string().max(255).optional().or(z.literal('')),
  roles: z.array(z.enum(['admin', 'pricing', 'sales', 'requester'])).min(1, 'Select at least one role'),
})

const editSchema = z.object({
  email: z.string().email(),
  first_name: z.string().min(1).max(100),
  last_name: z.string().min(1).max(100),
  job_title: z.string().max(255).optional().or(z.literal('')),
  roles: z.array(z.enum(['admin', 'pricing', 'sales', 'requester'])).min(1, 'Select at least one role'),
})

type CreateValues = z.infer<typeof createSchema>
type EditValues = z.infer<typeof editSchema>

interface UserFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  user?: UserRead | null
}

export function UserFormDialog({ open, onOpenChange, user }: UserFormDialogProps) {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const isEdit = Boolean(user)

  const form = useForm<CreateValues>({
    resolver: zodResolver(isEdit ? (editSchema as unknown as typeof createSchema) : createSchema),
    defaultValues: {
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      job_title: '',
      roles: ['requester'] as UserRoleType[],
    },
  })

  useEffect(() => {
    if (open) {
      form.reset({
        email: user?.email ?? '',
        password: '',
        first_name: user?.first_name ?? '',
        last_name: user?.last_name ?? '',
        job_title: user?.job_title ?? '',
        roles: user?.roles ?? (['requester'] as UserRoleType[]),
      })
    }
  }, [open, user, form])

  const mutation = useMutation({
    mutationFn: async (values: CreateValues | EditValues) => {
      if (isEdit && user) {
        await updateUser(user.profile_id, {
          first_name: values.first_name,
          last_name: values.last_name,
          job_title: values.job_title || null,
        })
        await updateUserRoles(user.profile_id, values.roles)
        return
      }
      const create = values as CreateValues
      await createUser({
        email: create.email,
        password: create.password,
        first_name: create.first_name,
        last_name: create.last_name,
        job_title: create.job_title || null,
        roles: create.roles,
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      toast({ title: isEdit ? 'User updated' : 'User created', variant: 'success' })
      onOpenChange(false)
    },
    onError: (err) => {
      toast({ title: 'Error', description: extractErrorMessage(err), variant: 'destructive' })
    },
  })

  const selectedRoles = form.watch('roles')

  const toggleRole = (role: UserRoleType) => {
    const current = form.getValues('roles')
    if (current.includes(role)) {
      form.setValue(
        'roles',
        current.filter((r) => r !== role),
        { shouldValidate: true },
      )
    } else {
      form.setValue('roles', [...current, role], { shouldValidate: true })
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{isEdit ? 'Edit user' : 'New user'}</DialogTitle>
          <DialogDescription>
            {isEdit ? 'Update user details and roles.' : 'Create a new user and assign roles.'}
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit((v) => mutation.mutate(v))} className="space-y-4">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email *</FormLabel>
                  <FormControl>
                    <Input type="email" {...field} disabled={isEdit} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            {!isEdit && (
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Password *</FormLabel>
                    <FormControl>
                      <Input type="password" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="first_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>First name *</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="last_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Last name *</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <FormField
              control={form.control}
              name="job_title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Job title</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="space-y-2">
              <div className="text-sm font-medium">Roles *</div>
              <div className="grid grid-cols-2 gap-2 rounded-md border p-3">
                {USER_ROLES.map((role) => (
                  <Checkbox
                    key={role}
                    label={role}
                    checked={selectedRoles.includes(role)}
                    onChange={() => toggleRole(role)}
                  />
                ))}
              </div>
              {form.formState.errors.roles && (
                <p className="text-sm font-medium text-destructive">{form.formState.errors.roles.message}</p>
              )}
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? 'Saving...' : isEdit ? 'Save changes' : 'Create user'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
