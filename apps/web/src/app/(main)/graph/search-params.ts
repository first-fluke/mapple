import { createSearchParamsCache, parseAsString } from 'nuqs/server';

export const graphSearchParams = {
  focus: parseAsString.withDefault(''),
};

export const graphSearchParamsCache = createSearchParamsCache(graphSearchParams);
