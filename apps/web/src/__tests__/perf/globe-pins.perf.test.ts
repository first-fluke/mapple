import { describe, expect, it } from 'vitest';
import type { GlobePin, SetPinsMessage } from '../../../../../packages/types/src/globe-bridge';
import { isInboundMessage } from '../../../../../packages/types/src/globe-bridge';

function generatePins(count: number): GlobePin[] {
  const pins: GlobePin[] = [];
  for (let i = 0; i < count; i++) {
    pins.push({
      id: `pin-${i}`,
      name: `Contact ${i}`,
      avatarUrl: `https://example.com/avatar/${i}.png`,
      lat: Math.random() * 180 - 90,
      lng: Math.random() * 360 - 180,
    });
  }
  return pins;
}

describe('Globe 500+ pins performance', () => {
  it('SET_PINS message creation with 500+ pins completes under 50ms', () => {
    const pins = generatePins(500);

    const start = performance.now();
    const message: SetPinsMessage = {
      type: 'SET_PINS',
      payload: { pins },
    };
    JSON.stringify(message);
    const elapsed = performance.now() - start;

    expect(elapsed).toBeLessThan(50);
  });

  it('SET_PINS message creation with 1000 pins completes under 100ms', () => {
    const pins = generatePins(1000);

    const start = performance.now();
    const message: SetPinsMessage = {
      type: 'SET_PINS',
      payload: { pins },
    };
    JSON.stringify(message);
    const elapsed = performance.now() - start;

    expect(elapsed).toBeLessThan(100);
  });

  it('JSON parse + type guard check with 500+ pins completes under 50ms', () => {
    const pins = generatePins(500);
    const message: SetPinsMessage = {
      type: 'SET_PINS',
      payload: { pins },
    };
    const serialized = JSON.stringify(message);

    const start = performance.now();
    const parsed = JSON.parse(serialized) as SetPinsMessage;
    isInboundMessage(parsed);
    const elapsed = performance.now() - start;

    expect(elapsed).toBeLessThan(50);
  });

  it('Pin filtering/searching with 500+ pins completes under 10ms', () => {
    const pins = generatePins(500);

    const start = performance.now();
    const filtered = pins.filter((pin) => pin.name.toLowerCase().includes('contact 1'));
    const elapsed = performance.now() - start;

    expect(filtered.length).toBeGreaterThan(0);
    expect(elapsed).toBeLessThan(10);
  });

  it('Batch pin operations (add/remove/update) with 500+ pins completes under 10ms', () => {
    const pins = generatePins(500);
    const pinsToAdd = generatePins(100).map((pin) => ({
      ...pin,
      id: `new-${pin.id}`,
    }));
    const idsToRemove = new Set(pins.slice(0, 100).map((pin) => pin.id));

    const start = performance.now();
    const result = [...pins.filter((pin) => !idsToRemove.has(pin.id)), ...pinsToAdd];
    const elapsed = performance.now() - start;

    expect(result.length).toBe(500);
    expect(elapsed).toBeLessThan(10);
  });
});
