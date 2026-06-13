import type { Metadata } from 'next';
import { getLegalContent } from '@/lib/i18n/legal';
import { getServerLocale } from '@/lib/i18n/server';

export async function generateMetadata(): Promise<Metadata> {
  const locale = await getServerLocale();
  const content = getLegalContent(locale, 'terms');
  return { title: `Globe CRM ${content.title}` };
}

export default async function TermsPage() {
  const locale = await getServerLocale();
  const content = getLegalContent(locale, 'terms');

  return (
    <article className="prose mx-auto max-w-3xl px-4 py-12">
      <h1>{content.title}</h1>
      <p className="text-muted-foreground">
        {content.lastUpdatedLabel} {content.lastUpdated}
      </p>

      <p>{content.intro}</p>

      {content.sections.map((section) => (
        <section key={section.heading}>
          <h2>{section.heading}</h2>
          {section.paragraphs?.map((para) => (
            <p key={para}>{para}</p>
          ))}
          {section.items && (
            <ul>
              {section.items.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          )}
        </section>
      ))}
    </article>
  );
}
