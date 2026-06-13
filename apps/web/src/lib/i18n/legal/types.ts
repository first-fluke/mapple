export interface LegalSection {
  heading: string;
  /** Prose paragraphs — rendered as <p> elements */
  paragraphs?: string[];
  /** List items — rendered as <ul><li> elements */
  items?: string[];
}

export interface LegalDoc {
  title: string;
  /** ISO date string (YYYY-MM-DD) */
  lastUpdated: string;
  /** Label prefix for the last-updated date line, e.g. "Last updated:" or "최종 수정일:" */
  lastUpdatedLabel: string;
  /** Introductory paragraph shown before the sections */
  intro: string;
  sections: LegalSection[];
}

export type LegalDocName = 'privacy' | 'terms';
