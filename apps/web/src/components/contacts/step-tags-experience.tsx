'use client';

import { Plus, X } from 'lucide-react';
import { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useOrganizationSearch } from '@/hooks/use-organizations';
import { useCreateTag, useTags } from '@/hooks/use-tags';
import type { ExperienceFormValue, WizardForm } from './add-contact-wizard';

export function StepTagsExperience({ form }: { form: WizardForm }) {
  return (
    <div className="flex flex-col gap-6">
      <TagSection form={form} />
      <ExperienceSection form={form} />
    </div>
  );
}

function TagSection({ form }: { form: WizardForm }) {
  const [newTag, setNewTag] = useState('');
  const { data: existingTags } = useTags();
  const createTag = useCreateTag();
  const selectedTagIds = form.getFieldValue('tagIds');

  const handleAddTag = async () => {
    if (!newTag.trim()) return;
    const result = await createTag.mutateAsync(newTag.trim());
    if (!selectedTagIds.includes(result.id)) {
      form.setFieldValue('tagIds', [...selectedTagIds, result.id]);
    }
    setNewTag('');
  };

  const handleToggleTag = (tagId: number) => {
    const current = form.getFieldValue('tagIds');
    if (current.includes(tagId)) {
      form.setFieldValue(
        'tagIds',
        current.filter((id) => id !== tagId),
      );
    } else {
      form.setFieldValue('tagIds', [...current, tagId]);
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <Label>Tags</Label>
      <div className="flex gap-2">
        <Input
          placeholder="Add a tag..."
          value={newTag}
          onChange={(e) => setNewTag(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault();
              handleAddTag();
            }
          }}
        />
        <Button type="button" variant="outline" size="icon-sm" onClick={handleAddTag}>
          <Plus className="h-4 w-4" />
        </Button>
      </div>
      {existingTags && existingTags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 pt-1">
          {existingTags.map((tag) => (
            <Badge
              key={tag.id}
              variant={selectedTagIds.includes(tag.id) ? 'default' : 'outline'}
              className="cursor-pointer"
              onClick={() => handleToggleTag(tag.id)}
            >
              {tag.name}
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
}

function ExperienceSection({ form }: { form: WizardForm }) {
  const experiences = form.getFieldValue('experiences');

  const addExperience = () => {
    form.setFieldValue('experiences', [
      ...experiences,
      {
        _key: crypto.randomUUID(),
        organizationName: '',
        organizationType: 'company',
        organizationId: null,
        role: '',
        major: '',
      },
    ]);
  };

  const removeExperience = (index: number) => {
    form.setFieldValue(
      'experiences',
      experiences.filter((_, i) => i !== index),
    );
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <Label>Experience</Label>
        <Button type="button" variant="ghost" size="sm" onClick={addExperience}>
          <Plus className="mr-1 h-3 w-3" />
          Add
        </Button>
      </div>
      {experiences.map((exp, index) => (
        <ExperienceRow key={exp._key} form={form} index={index} onRemove={() => removeExperience(index)} />
      ))}
      {experiences.length === 0 && (
        <p className="text-center text-xs text-muted-foreground py-2">No experiences added. This is optional.</p>
      )}
    </div>
  );
}

function ExperienceRow({ form, index, onRemove }: { form: WizardForm; index: number; onRemove: () => void }) {
  const [orgQuery, setOrgQuery] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const { data: orgResults } = useOrganizationSearch(orgQuery);
  const experience = form.getFieldValue('experiences')[index];

  const updateExperience = (patch: Partial<ExperienceFormValue>) => {
    const exps = [...form.getFieldValue('experiences')];
    exps[index] = { ...exps[index], ...patch };
    form.setFieldValue('experiences', exps);
  };

  return (
    <div className="rounded-lg border p-3 relative">
      <Button type="button" variant="ghost" size="icon-sm" className="absolute top-1 right-1" onClick={onRemove}>
        <X className="h-3 w-3" />
      </Button>
      <div className="flex flex-col gap-2 pr-6">
        <div className="relative">
          <Input
            placeholder="Organization name"
            value={experience.organizationName}
            onChange={(e) => {
              const val = e.target.value;
              setOrgQuery(val);
              updateExperience({ organizationName: val, organizationId: null });
              setShowSuggestions(true);
            }}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          />
          {showSuggestions && orgResults && orgResults.length > 0 && (
            <div className="absolute z-10 mt-1 w-full rounded-md border bg-popover p-1 shadow-md">
              {orgResults.map((org) => (
                <button
                  key={org.id}
                  type="button"
                  className="flex w-full items-center rounded-sm px-2 py-1.5 text-sm hover:bg-accent"
                  onMouseDown={(e) => {
                    e.preventDefault();
                    updateExperience({
                      organizationName: org.name,
                      organizationType: org.type,
                      organizationId: org.id,
                    });
                    setShowSuggestions(false);
                    setOrgQuery('');
                  }}
                >
                  <span>{org.name}</span>
                  <span className="ml-auto text-xs text-muted-foreground">{org.type}</span>
                </button>
              ))}
            </div>
          )}
        </div>
        <div className="grid grid-cols-2 gap-2">
          <Input
            placeholder="Role / Title"
            value={experience.role}
            onChange={(e) => updateExperience({ role: e.target.value })}
          />
          <Input
            placeholder="Major / Field"
            value={experience.major}
            onChange={(e) => updateExperience({ major: e.target.value })}
          />
        </div>
      </div>
    </div>
  );
}
