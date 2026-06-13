'use client';

import { Component, type ErrorInfo, type ReactNode } from 'react';
import { useTranslations } from '@/hooks/use-translations';

interface BoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  strings: {
    globeIconTitle: string;
    webglTitle: string;
    webglDescription: string;
    genericError: string;
  };
}

interface State {
  hasError: boolean;
  isWebGLUnavailable: boolean;
}

function detectWebGL(): boolean {
  try {
    const canvas = document.createElement('canvas');
    return !!(
      canvas.getContext('webgl') ||
      // biome-ignore lint/suspicious/noExplicitAny: experimental API check
      (canvas.getContext as (type: string) => any)('experimental-webgl')
    );
  } catch {
    return false;
  }
}

class GlobeErrorBoundaryInner extends Component<BoundaryProps, State> {
  constructor(props: BoundaryProps) {
    super(props);
    this.state = { hasError: false, isWebGLUnavailable: false };
  }

  static getDerivedStateFromError(error: Error): State {
    const isWebGLUnavailable =
      error.message?.toLowerCase().includes('webgl') ||
      error.message?.toLowerCase().includes('three') ||
      !detectWebGL();
    return { hasError: true, isWebGLUnavailable };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('[Globe] Render error:', error, info.componentStack);
  }

  render() {
    const { strings } = this.props;
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;

      if (this.state.isWebGLUnavailable) {
        return (
          <div
            className="flex h-full w-full flex-col items-center justify-center gap-4 rounded-xl p-8 text-center"
            style={{ background: '#1c1917', color: '#a8a29e' }}
            role="alert"
          >
            <svg
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              aria-hidden="true"
            >
              <title>{strings.globeIconTitle}</title>
              <circle cx="12" cy="12" r="10" />
              <line x1="2" y1="12" x2="22" y2="12" />
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
            </svg>
            <div>
              <p className="text-base font-medium" style={{ color: '#faf8f5' }}>
                {strings.webglTitle}
              </p>
              <p className="mt-1 text-sm">
                {strings.webglDescription.split('\n').map((line, i) => (
                  // biome-ignore lint/suspicious/noArrayIndexKey: static split
                  <span key={i}>
                    {i > 0 && <br />}
                    {line}
                  </span>
                ))}
              </p>
            </div>
          </div>
        );
      }

      return (
        <div
          className="flex h-full w-full items-center justify-center rounded-xl"
          style={{ background: '#1c1917', color: '#a8a29e' }}
          role="alert"
        >
          <p className="text-sm">{strings.genericError}</p>
        </div>
      );
    }

    return this.props.children;
  }
}

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

export function GlobeErrorBoundary({ children, fallback }: Props) {
  const d = useTranslations();
  return (
    <GlobeErrorBoundaryInner strings={d.globe.errorBoundary} fallback={fallback}>
      {children}
    </GlobeErrorBoundaryInner>
  );
}
