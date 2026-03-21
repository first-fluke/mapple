'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Pencil, Plus, Trash2 } from 'lucide-react';
import { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { api } from '@/lib/api/client';

interface Tag {
  id: number;
  name: string;
  color: string;
}

const PRESET_COLORS = [
  '#ef4444',
  '#f97316',
  '#f59e0b',
  '#eab308',
  '#84cc16',
  '#22c55e',
  '#14b8a6',
  '#06b6d4',
  '#3b82f6',
  '#6366f1',
  '#8b5cf6',
  '#a855f7',
  '#d946ef',
  '#ec4899',
  '#f43f5e',
  '#64748b',
];

export default function TagsPage() {
  const queryClient = useQueryClient();
  const [newTag, setNewTag] = useState({ name: '', color: '#6366f1' });
  const [editingTag, setEditingTag] = useState<Tag | null>(null);

  const { data: tags = [], isLoading } = useQuery({
    queryKey: ['tags'],
    queryFn: async () => {
      const res = await api.get<Tag[]>('/tags');
      return res.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: async (data: { name: string; color: string }) => {
      const res = await api.post<Tag>('/tags', data);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
      setNewTag({ name: '', color: '#6366f1' });
    },
  });

  const updateMutation = useMutation({
    mutationFn: async ({ id, ...data }: { id: number; name?: string; color?: string }) => {
      const res = await api.patch<Tag>(`/tags/${id}`, data);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
      setEditingTag(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/tags/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
    },
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Tags</CardTitle>
        <CardDescription>Create and manage tags to organize your contacts.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (newTag.name.trim()) {
              createMutation.mutate(newTag);
            }
          }}
          className="flex items-end gap-2"
        >
          <div className="flex-1 space-y-2">
            <Label htmlFor="tag-name">New Tag</Label>
            <Input
              id="tag-name"
              value={newTag.name}
              onChange={(e) => setNewTag((prev) => ({ ...prev, name: e.target.value }))}
              placeholder="Tag name"
              maxLength={100}
            />
          </div>
          <ColorPicker color={newTag.color} onChange={(color) => setNewTag((prev) => ({ ...prev, color }))} />
          <Button type="submit" size="icon" disabled={createMutation.isPending || !newTag.name.trim()}>
            <Plus className="h-4 w-4" />
          </Button>
        </form>

        {isLoading ? (
          <TagsSkeleton />
        ) : tags.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">No tags yet. Create your first tag above.</p>
        ) : (
          <ul className="space-y-2">
            {tags.map((tag) => (
              <li key={tag.id} className="flex items-center justify-between rounded-md border p-3">
                {editingTag?.id === tag.id ? (
                  <form
                    onSubmit={(e) => {
                      e.preventDefault();
                      updateMutation.mutate({
                        id: editingTag.id,
                        name: editingTag.name,
                        color: editingTag.color,
                      });
                    }}
                    className="flex flex-1 items-center gap-2"
                  >
                    <Input
                      value={editingTag.name}
                      onChange={(e) => setEditingTag({ ...editingTag, name: e.target.value })}
                      className="h-8"
                      autoFocus
                    />
                    <ColorPicker
                      color={editingTag.color}
                      onChange={(color) => setEditingTag({ ...editingTag, color })}
                    />
                    <Button type="submit" size="sm" disabled={updateMutation.isPending}>
                      Save
                    </Button>
                    <Button type="button" size="sm" variant="ghost" onClick={() => setEditingTag(null)}>
                      Cancel
                    </Button>
                  </form>
                ) : (
                  <>
                    <Badge variant="outline" style={{ borderColor: tag.color, color: tag.color }}>
                      {tag.name}
                    </Badge>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => setEditingTag(tag)}>
                        <Pencil className="h-3.5 w-3.5" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 text-destructive"
                        onClick={() => deleteMutation.mutate(tag.id)}
                        disabled={deleteMutation.isPending}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </>
                )}
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}

function ColorPicker({ color, onChange }: { color: string; onChange: (color: string) => void }) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button type="button" variant="outline" className="h-9 w-9 p-0" aria-label="Pick color">
          <span className="h-5 w-5 rounded-sm" style={{ backgroundColor: color }} />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-3" align="end">
        <div className="grid grid-cols-4 gap-2">
          {PRESET_COLORS.map((preset) => (
            <button
              key={preset}
              type="button"
              className="h-7 w-7 rounded-md border-2 transition-transform hover:scale-110"
              style={{
                backgroundColor: preset,
                borderColor: color === preset ? 'var(--foreground)' : 'transparent',
              }}
              onClick={() => onChange(preset)}
              aria-label={`Color ${preset}`}
            />
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
}

function TagsSkeleton() {
  return (
    <div className="space-y-2">
      {['skeleton-1', 'skeleton-2', 'skeleton-3'].map((key) => (
        <div key={key} className="flex items-center justify-between rounded-md border p-3">
          <div className="h-5 w-20 animate-pulse rounded bg-muted" />
          <div className="flex gap-1">
            <div className="h-8 w-8 animate-pulse rounded bg-muted" />
            <div className="h-8 w-8 animate-pulse rounded bg-muted" />
          </div>
        </div>
      ))}
    </div>
  );
}
