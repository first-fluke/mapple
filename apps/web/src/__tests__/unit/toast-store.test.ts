import { createStore } from 'jotai';
import { describe, expect, it } from 'vitest';
import type { ToastVariant } from '@/stores/toast';
import { createToast, toastsAtom } from '@/stores/toast';

// ---------------------------------------------------------------------------
// createToast helper
// ---------------------------------------------------------------------------
describe('createToast', () => {
  it('creates a toast with the supplied message and variant', () => {
    const t = createToast('저장되었습니다', 'success');
    expect(t.message).toBe('저장되었습니다');
    expect(t.variant).toBe('success');
  });

  it('assigns a non-empty id', () => {
    const t = createToast('msg', 'info');
    expect(t.id).toBeTruthy();
    expect(typeof t.id).toBe('string');
  });

  it('generates unique ids on each call', () => {
    const a = createToast('msg', 'info');
    const b = createToast('msg', 'info');
    expect(a.id).not.toBe(b.id);
  });

  it.each<ToastVariant>(['success', 'error', 'info'])('accepts variant=%s', (variant) => {
    const t = createToast('test', variant);
    expect(t.variant).toBe(variant);
  });
});

// ---------------------------------------------------------------------------
// toastsAtom — add / dismiss via Jotai store
// ---------------------------------------------------------------------------
describe('toastsAtom', () => {
  it('starts empty', () => {
    const store = createStore();
    expect(store.get(toastsAtom)).toHaveLength(0);
  });

  it('adds a toast', () => {
    const store = createStore();
    const t = createToast('오류가 발생했습니다', 'error');
    store.set(toastsAtom, [t]);
    expect(store.get(toastsAtom)).toHaveLength(1);
    expect(store.get(toastsAtom)[0]).toEqual(t);
  });

  it('adds multiple toasts', () => {
    const store = createStore();
    const t1 = createToast('첫 번째', 'success');
    const t2 = createToast('두 번째', 'error');
    store.set(toastsAtom, [t1, t2]);
    expect(store.get(toastsAtom)).toHaveLength(2);
  });

  it('dismisses a toast by id', () => {
    const store = createStore();
    const t1 = createToast('첫 번째', 'success');
    const t2 = createToast('두 번째', 'info');
    store.set(toastsAtom, [t1, t2]);

    // Dismiss t1 by filtering it out (mirrors the dismiss logic in Toaster)
    store.set(
      toastsAtom,
      store.get(toastsAtom).filter((x) => x.id !== t1.id),
    );

    const remaining = store.get(toastsAtom);
    expect(remaining).toHaveLength(1);
    expect(remaining[0]?.id).toBe(t2.id);
  });

  it('dismissing a non-existent id leaves list unchanged', () => {
    const store = createStore();
    const t = createToast('msg', 'info');
    store.set(toastsAtom, [t]);

    store.set(
      toastsAtom,
      store.get(toastsAtom).filter((x) => x.id !== 'ghost-id'),
    );
    expect(store.get(toastsAtom)).toHaveLength(1);
  });

  it('clearing all toasts', () => {
    const store = createStore();
    store.set(toastsAtom, [createToast('a', 'success'), createToast('b', 'error')]);
    store.set(toastsAtom, []);
    expect(store.get(toastsAtom)).toHaveLength(0);
  });
});
