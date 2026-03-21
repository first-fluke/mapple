'use client';

import { useForm } from '@tanstack/react-form';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { api } from '@/lib/api/client';

interface User {
  id: number;
  provider: string;
  email: string;
  name: string | null;
  avatar_url: string | null;
}

export default function ProfilePage() {
  const queryClient = useQueryClient();

  const { data: user, isLoading } = useQuery({
    queryKey: ['me'],
    queryFn: async () => {
      const res = await api.get<User>('/auth/me');
      return res.data;
    },
  });

  const mutation = useMutation({
    mutationFn: async (name: string) => {
      const res = await api.patch<User>('/auth/me', { name });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['me'] });
    },
  });

  const form = useForm({
    defaultValues: {
      name: user?.name ?? '',
    },
    onSubmit: async ({ value }) => {
      mutation.mutate(value.name);
    },
  });

  if (isLoading) {
    return <ProfileSkeleton />;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Profile</CardTitle>
        <CardDescription>Manage your account profile information.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-center gap-4">
          <Avatar className="h-16 w-16">
            <AvatarImage src={user?.avatar_url ?? undefined} alt={user?.name ?? 'User'} />
            <AvatarFallback className="text-lg">{user?.name?.charAt(0)?.toUpperCase() ?? 'U'}</AvatarFallback>
          </Avatar>
          <div>
            <p className="font-medium">{user?.name ?? 'Unknown'}</p>
            <p className="text-sm text-muted-foreground">{user?.email}</p>
          </div>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            form.handleSubmit();
          }}
          className="space-y-4"
        >
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" value={user?.email ?? ''} disabled />
            <p className="text-xs text-muted-foreground">Email is managed by your {user?.provider} account.</p>
          </div>

          <form.Field name="name">
            {(field) => (
              <div className="space-y-2">
                <Label htmlFor="name">Display Name</Label>
                <Input
                  id="name"
                  value={field.state.value}
                  onChange={(e) => field.handleChange(e.target.value)}
                  onBlur={field.handleBlur}
                  placeholder="Your name"
                />
              </div>
            )}
          </form.Field>

          <Button type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? 'Saving...' : 'Save Changes'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

function ProfileSkeleton() {
  return (
    <Card>
      <CardHeader>
        <div className="h-6 w-24 animate-pulse rounded bg-muted" />
        <div className="h-4 w-48 animate-pulse rounded bg-muted" />
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-center gap-4">
          <div className="h-16 w-16 animate-pulse rounded-full bg-muted" />
          <div className="space-y-2">
            <div className="h-4 w-32 animate-pulse rounded bg-muted" />
            <div className="h-3 w-48 animate-pulse rounded bg-muted" />
          </div>
        </div>
        <div className="space-y-4">
          <div className="h-10 w-full animate-pulse rounded bg-muted" />
          <div className="h-10 w-full animate-pulse rounded bg-muted" />
        </div>
      </CardContent>
    </Card>
  );
}
