'use client';

import { useAtom } from 'jotai';
import { MapPin } from 'lucide-react';
import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { useReverseGeocode } from '@/hooks/use-reverse-geocode';
import { globeModeAtom } from '@/lib/atoms';
import type { WizardForm } from './add-contact-wizard';

export function StepLocation({ form }: { form: WizardForm }) {
  const [globeMode, setGlobeMode] = useAtom(globeModeAtom);
  const lat = form.getFieldValue('latitude');
  const lng = form.getFieldValue('longitude');
  const country = form.getFieldValue('country');
  const city = form.getFieldValue('city');
  const { data: geocodeResult } = useReverseGeocode(lat, lng);

  useEffect(() => {
    if (geocodeResult) {
      if (geocodeResult.country) {
        form.setFieldValue('country', geocodeResult.country);
      }
      if (geocodeResult.city) {
        form.setFieldValue('city', geocodeResult.city);
      }
    }
  }, [geocodeResult, form]);

  useEffect(() => {
    function handleGlobeMessage(event: MessageEvent) {
      if (event.data?.type === 'LOCATION_SELECTED') {
        const { lat, lng } = event.data.payload;
        form.setFieldValue('latitude', lat);
        form.setFieldValue('longitude', lng);
        setGlobeMode('explore');
      }
    }

    window.addEventListener('message', handleGlobeMessage);
    return () => window.removeEventListener('message', handleGlobeMessage);
  }, [form, setGlobeMode]);

  useEffect(() => {
    return () => {
      setGlobeMode('explore');
    };
  }, [setGlobeMode]);

  const isPlacingPin = globeMode === 'select_location';
  const hasLocation = lat != null && lng != null;

  return (
    <div className="flex flex-col gap-4">
      <p className="text-sm text-muted-foreground">Place a pin on the globe to set this contact&apos;s location.</p>

      <Button
        type="button"
        variant={isPlacingPin ? 'default' : 'outline'}
        onClick={() => setGlobeMode(isPlacingPin ? 'explore' : 'select_location')}
        className="w-full"
      >
        <MapPin className="mr-2 h-4 w-4" />
        {isPlacingPin ? 'Placing pin... Click on the globe' : hasLocation ? 'Change location' : 'Place pin on globe'}
      </Button>

      {hasLocation && (
        <div className="rounded-lg border bg-muted/50 p-3">
          <div className="flex flex-col gap-1 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Coordinates</span>
              <span className="font-mono text-xs">
                {lat.toFixed(4)}, {lng.toFixed(4)}
              </span>
            </div>
            {country && (
              <div className="flex justify-between">
                <span className="text-muted-foreground">Country</span>
                <span>{country}</span>
              </div>
            )}
            {city && (
              <div className="flex justify-between">
                <span className="text-muted-foreground">City</span>
                <span>{city}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {!hasLocation && !isPlacingPin && (
        <p className="text-center text-xs text-muted-foreground">Location is optional. You can skip this step.</p>
      )}
    </div>
  );
}
