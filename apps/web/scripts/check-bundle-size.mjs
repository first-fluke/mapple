import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';
import { gzipSync } from 'node:zlib';

const BUDGET_BYTES = 2 * 1024 * 1024; // 2MB

/**
 * Recursively collect all .js files under a directory.
 * @param {string} dir
 * @returns {string[]}
 */
function collectJsFiles(dir) {
  /** @type {string[]} */
  const results = [];

  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const fullPath = join(dir, entry.name);

    if (entry.isDirectory()) {
      results.push(...collectJsFiles(fullPath));
    } else if (entry.isFile() && entry.name.endsWith('.js')) {
      results.push(fullPath);
    }
  }

  return results;
}

/**
 * Format bytes into a human-readable string.
 * @param {number} bytes
 * @returns {string}
 */
function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

// Resolve .next/static relative to the script's parent directory (apps/web)
const webRoot = join(import.meta.dirname, '..');
const staticDir = join(webRoot, '.next', 'static');

try {
  statSync(staticDir);
} catch {
  console.error(`ERROR: ${staticDir} does not exist. Run "next build" first.`);
  process.exit(1);
}

const jsFiles = collectJsFiles(staticDir);

if (jsFiles.length === 0) {
  console.error('ERROR: No .js files found in .next/static/');
  process.exit(1);
}

/** @type {{ path: string; rawSize: number; gzipSize: number }[]} */
const entries = [];

for (const filePath of jsFiles) {
  const content = readFileSync(filePath);
  const gzipped = gzipSync(content);
  entries.push({
    path: relative(staticDir, filePath),
    rawSize: content.length,
    gzipSize: gzipped.length,
  });
}

const totalRaw = entries.reduce((sum, e) => sum + e.rawSize, 0);
const totalGzip = entries.reduce((sum, e) => sum + e.gzipSize, 0);

// Sort by gzipped size descending for the top-5 report
entries.sort((a, b) => b.gzipSize - a.gzipSize);

console.log('=== Bundle Size Report ===\n');
console.log(`Total files:         ${entries.length}`);
console.log(`Total raw size:      ${formatBytes(totalRaw)}`);
console.log(`Total gzipped size:  ${formatBytes(totalGzip)}`);
console.log(`Budget:              ${formatBytes(BUDGET_BYTES)}`);
console.log();

console.log('Top 5 largest chunks (gzipped):');
for (const entry of entries.slice(0, 5)) {
  console.log(`  ${formatBytes(entry.gzipSize).padStart(10)}  ${entry.path}`);
}
console.log();

if (totalGzip > BUDGET_BYTES) {
  console.error(`FAIL: Total gzipped size (${formatBytes(totalGzip)}) exceeds budget (${formatBytes(BUDGET_BYTES)})`);
  process.exit(1);
} else {
  console.log(`PASS: Total gzipped size (${formatBytes(totalGzip)}) is within budget (${formatBytes(BUDGET_BYTES)})`);
  process.exit(0);
}
