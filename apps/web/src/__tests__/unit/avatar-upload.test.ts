/**
 * Tests the avatar upload flow logic in isolation (no React renderer needed).
 *
 * Strategy: extract the mutationFn logic into a testable pure function,
 * mock `fetch` and the contacts API calls, verify the full presign → PUT → confirm
 * pipeline, client-side file validation, and error propagation.
 */

import { afterEach, beforeEach, describe, expect, it, type Mock, vi } from 'vitest';
import { validateAvatarFile } from '@/lib/validation';

// ---------------------------------------------------------------------------
// Inline the avatar upload mutationFn for unit-testability
// (mirrors the implementation in hooks/use-contact.ts useAvatarUpload)
// ---------------------------------------------------------------------------
interface PresignResult {
  upload_url: string;
  avatar_url: string;
}

interface AvatarConfirmResult {
  id: number;
  avatar_url: string | null;
}

async function avatarUploadFn(
  file: File,
  deps: {
    getPresignUrl: () => Promise<PresignResult>;
    putFile: (url: string, file: File) => Promise<void>;
    confirmAvatar: (url: string) => Promise<AvatarConfirmResult>;
  },
): Promise<AvatarConfirmResult> {
  const { upload_url, avatar_url } = await deps.getPresignUrl();
  await deps.putFile(upload_url, file);
  return deps.confirmAvatar(avatar_url);
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
const makeFile = (name: string, type: string, size = 1024): File => {
  const blob = new Blob([new Uint8Array(size)], { type });
  return new File([blob], name, { type });
};

const PRESIGN_RESULT: PresignResult = {
  upload_url: 'https://s3.example.com/presigned?sig=abc',
  avatar_url: 'https://cdn.example.com/avatars/contact-1.jpg',
};
const CONFIRM_RESULT: AvatarConfirmResult = {
  id: 1,
  avatar_url: PRESIGN_RESULT.avatar_url,
};

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------
describe('avatar upload flow (pure logic)', () => {
  let getPresignUrl: Mock<() => Promise<PresignResult>>;
  let putFile: Mock<(url: string, file: File) => Promise<void>>;
  let confirmAvatar: Mock<(url: string) => Promise<AvatarConfirmResult>>;

  beforeEach(() => {
    getPresignUrl = vi.fn<() => Promise<PresignResult>>().mockResolvedValue(PRESIGN_RESULT);
    putFile = vi.fn<(url: string, file: File) => Promise<void>>().mockResolvedValue(undefined);
    confirmAvatar = vi.fn<(url: string) => Promise<AvatarConfirmResult>>().mockResolvedValue(CONFIRM_RESULT);
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  it('calls getPresignUrl, then PUT, then confirmAvatar in order', async () => {
    const file = makeFile('photo.jpg', 'image/jpeg');
    const order: string[] = [];

    const deps = {
      getPresignUrl: vi.fn().mockImplementation(async () => {
        order.push('presign');
        return PRESIGN_RESULT;
      }),
      putFile: vi.fn().mockImplementation(async () => {
        order.push('put');
      }),
      confirmAvatar: vi.fn().mockImplementation(async () => {
        order.push('confirm');
        return CONFIRM_RESULT;
      }),
    };

    await avatarUploadFn(file, deps);
    expect(order).toEqual(['presign', 'put', 'confirm']);
  });

  it('passes the presigned upload_url to putFile', async () => {
    const file = makeFile('photo.png', 'image/png');
    await avatarUploadFn(file, { getPresignUrl, putFile, confirmAvatar });
    expect(putFile).toHaveBeenCalledWith(PRESIGN_RESULT.upload_url, file);
  });

  it('passes the avatar_url from presign response to confirmAvatar', async () => {
    const file = makeFile('photo.webp', 'image/webp');
    await avatarUploadFn(file, { getPresignUrl, putFile, confirmAvatar });
    expect(confirmAvatar).toHaveBeenCalledWith(PRESIGN_RESULT.avatar_url);
  });

  it('returns the result from confirmAvatar', async () => {
    const file = makeFile('photo.jpg', 'image/jpeg');
    const result = await avatarUploadFn(file, { getPresignUrl, putFile, confirmAvatar });
    expect(result).toEqual(CONFIRM_RESULT);
  });

  it('propagates presign errors', async () => {
    const file = makeFile('photo.jpg', 'image/jpeg');
    getPresignUrl.mockRejectedValue(new Error('Network error'));
    await expect(avatarUploadFn(file, { getPresignUrl, putFile, confirmAvatar })).rejects.toThrow('Network error');
    expect(putFile).not.toHaveBeenCalled();
    expect(confirmAvatar).not.toHaveBeenCalled();
  });

  it('propagates PUT errors and does not call confirm', async () => {
    const file = makeFile('photo.jpg', 'image/jpeg');
    putFile.mockRejectedValue(new Error('Upload failed'));
    await expect(avatarUploadFn(file, { getPresignUrl, putFile, confirmAvatar })).rejects.toThrow('Upload failed');
    expect(confirmAvatar).not.toHaveBeenCalled();
  });

  it('propagates confirm errors', async () => {
    const file = makeFile('photo.jpg', 'image/jpeg');
    confirmAvatar.mockRejectedValue(new Error('Confirm failed'));
    await expect(avatarUploadFn(file, { getPresignUrl, putFile, confirmAvatar })).rejects.toThrow('Confirm failed');
  });
});

// ---------------------------------------------------------------------------
// Client-side validation gate (mirrors ContactProfile handleFileChange)
// ---------------------------------------------------------------------------
describe('avatar upload – client-side validation gate', () => {
  it('blocks upload when file type is invalid', () => {
    const file = makeFile('doc.pdf', 'application/pdf');
    const err = validateAvatarFile(file);
    expect(err).not.toBeNull();
    // If we were in a component, we'd call error(err) and return early.
    // Here we just assert the gate produces an error message.
  });

  it('blocks upload when file is over 5 MB', () => {
    const file = makeFile('huge.jpg', 'image/jpeg', 5 * 1024 * 1024 + 1);
    expect(validateAvatarFile(file)).not.toBeNull();
  });

  it('allows upload for a valid file', () => {
    const file = makeFile('ok.jpg', 'image/jpeg', 512 * 1024);
    expect(validateAvatarFile(file)).toBeNull();
  });
});
