'use client';

import { Check, Loader2, Plus, X } from 'lucide-react';
import { useState } from 'react';
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/components/ui/command';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { useAddContactTag, useRemoveContactTag } from '@/hooks/use-contact';
import { useTags } from '@/hooks/use-tags';
import { useToast } from '@/hooks/use-toast';
import { useTranslations } from '@/hooks/use-translations';
import type { Tag } from '@/lib/api/contacts';
import { cn } from '@/lib/utils';

interface ContactTagsProps {
  contactId: number;
  tags: Tag[];
}

export function ContactTags({ contactId, tags }: ContactTagsProps) {
  const [open, setOpen] = useState(false);
  const { data: allTags = [], isLoading: tagsLoading } = useTags();
  const addTag = useAddContactTag(contactId);
  const removeTag = useRemoveContactTag(contactId);
  const { success, error } = useToast();
  const d = useTranslations();

  const assignedIds = new Set(tags.map((t) => t.id));

  const handleAdd = async (tagId: number) => {
    if (assignedIds.has(tagId)) return;
    try {
      await addTag.mutateAsync(tagId);
      success(d.contacts.tags.toastAdded);
    } catch {
      error(d.contacts.tags.toastAddFailed);
    }
  };

  const handleRemove = async (tagId: number) => {
    try {
      await removeTag.mutateAsync(tagId);
      success(d.contacts.tags.toastRemoved);
    } catch {
      error(d.contacts.tags.toastRemoveFailed);
    }
  };

  const isPending = addTag.isPending || removeTag.isPending;

  return (
    <div className="flex flex-wrap items-center gap-2">
      {tags.map((tag) => (
        <span
          key={tag.id}
          className="inline-flex h-6 items-center gap-1.5 rounded-full border px-2.5 text-xs font-medium transition-colors"
          style={
            tag.color
              ? {
                  borderColor: tag.color,
                  color: tag.color,
                  backgroundColor: `${tag.color}18`,
                }
              : undefined
          }
        >
          {tag.color ? (
            <span className="size-2 shrink-0 rounded-full" style={{ backgroundColor: tag.color }} aria-hidden="true" />
          ) : null}
          <span>{tag.name}</span>
          <button
            type="button"
            onClick={() => handleRemove(tag.id)}
            disabled={isPending}
            aria-label={d.contacts.tags.removeLabel.replace('{{name}}', tag.name)}
            className="ml-0.5 rounded-full p-0.5 opacity-60 transition-opacity hover:opacity-100 focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-current disabled:pointer-events-none"
          >
            <X className="size-3" aria-hidden="true" />
          </button>
        </span>
      ))}

      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger
          aria-label={d.contacts.tags.addLabel}
          aria-expanded={open}
          className="inline-flex h-6 items-center gap-1 rounded-full border border-dashed border-stone-300 px-2.5 text-xs font-medium text-stone-500 transition-colors hover:border-stone-400 hover:text-stone-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-orange-500 disabled:pointer-events-none disabled:opacity-50"
          disabled={isPending}
        >
          {isPending ? (
            <Loader2 className="size-3 animate-spin" aria-hidden="true" />
          ) : (
            <Plus className="size-3" aria-hidden="true" />
          )}
          {d.contacts.tags.addButton}
        </PopoverTrigger>
        <PopoverContent className="w-56 p-0" align="start">
          <Command>
            <CommandInput
              placeholder={d.contacts.tags.searchPlaceholder}
              aria-label={d.contacts.tags.searchPlaceholder}
            />
            <CommandList>
              {tagsLoading ? (
                <div className="flex items-center justify-center py-4">
                  <Loader2 className="size-4 animate-spin text-muted-foreground" aria-hidden="true" />
                </div>
              ) : (
                <>
                  <CommandEmpty>{d.contacts.tags.empty}</CommandEmpty>
                  <CommandGroup>
                    {allTags.map((tag) => {
                      const isAssigned = assignedIds.has(tag.id);
                      return (
                        <CommandItem
                          key={tag.id}
                          value={tag.name}
                          onSelect={() => {
                            if (!isAssigned) {
                              handleAdd(tag.id);
                              setOpen(false);
                            }
                          }}
                          aria-selected={isAssigned}
                          className={cn(isAssigned && 'opacity-50')}
                        >
                          <span className="flex flex-1 items-center gap-2">
                            {tag.color ? (
                              <span
                                className="size-2.5 shrink-0 rounded-full"
                                style={{ backgroundColor: tag.color }}
                                aria-hidden="true"
                              />
                            ) : null}
                            {tag.name}
                          </span>
                          {isAssigned && (
                            <Check className="size-3.5 shrink-0 text-muted-foreground" aria-hidden="true" />
                          )}
                        </CommandItem>
                      );
                    })}
                  </CommandGroup>
                </>
              )}
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  );
}
