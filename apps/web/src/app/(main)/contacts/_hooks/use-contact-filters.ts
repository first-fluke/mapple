'use client';

import { parseAsBoolean, parseAsString, useQueryStates } from 'nuqs';

export const contactFiltersParsers = {
  search: parseAsString.withDefault(''),
  sort: parseAsString.withDefault('created_at_desc'),
  has_email: parseAsBoolean,
  has_phone: parseAsBoolean,
};

export function useContactFilters() {
  return useQueryStates(contactFiltersParsers, {
    shallow: false,
  });
}
