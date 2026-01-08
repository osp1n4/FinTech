import React, { useState } from 'react';

interface LocationInputProps {
  value: string;
  onChange: (value: string) => void;
  error?: string;
  disabled?: boolean;
}

export const LocationInput: React.FC<LocationInputProps> = ({
  value,
  onChange,
  error,
  disabled,
}) => {
  const [isGettingLocation, setIsGettingLocation] = useState(false);
  const [locationMethod, setLocationMethod] = useState<'gps' | 'manual'>('manual');

  const getCurrentLocation = () => {
    if (!navigator.geolocation) {
      alert('Tu navegador no soporta geolocalizacion');
      return;
    }

    setIsGettingLocation(true);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude.toFixed(4);
        const lon = position.coords.longitude.toFixed(4);
        onChange(`${lat},${lon}`);
        setLocationMethod('gps');
        setIsGettingLocation(false);
      },
      (error) => {
        console.error('Error getting location:', error);
        alert('No se pudo obtener la ubicacion. Asegurate de dar permiso al navegador.');
        setIsGettingLocation(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  };

  const handleManualInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
    setLocationMethod('manual');
  };

  // Validar si el valor es coordenadas (formato: "lat,lon")
  const isCoordinates = /^-?\d+\.?\d*,-?\d+\.?\d*$/.test(value);

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        Ubicacion
      </label>

      <div className="flex gap-2">
        {/* Input de ubicación */}
        <div className="flex-1">
          <input
            type="text"
            value={value}
            onChange={handleManualInput}
            placeholder="4.6097,-74.0817 o Ciudad, País"
            disabled={disabled || isGettingLocation}
            className={`
              w-full px-4 py-3 rounded-lg border transition-colors
              ${error ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-user-primary'}
              ${disabled || isGettingLocation ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}
              focus:outline-none focus:ring-2
            `}
          />
          {error && (
            <p className="mt-1 text-sm text-red-600">{error}</p>
          )}
        </div>

        {/* Botón de GPS */}
        <button
          type="button"
          onClick={getCurrentLocation}
          disabled={disabled || isGettingLocation}
          className={`
            px-4 py-3 rounded-lg font-medium transition-colors flex items-center gap-2
            ${isGettingLocation
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-user-primary hover:bg-indigo-700 text-white'
            }
          `}
          title="Usar mi ubicación actual"
        >
          {isGettingLocation ? (
            <>
              <span className="animate-spin">⟳</span>
              <span className="hidden sm:inline">Obteniendo...</span>
            </>
          ) : (
            <>
              <span>📍</span>
              <span className="hidden sm:inline">GPS</span>
            </>
          )}
        </button>
      </div>

      {/* Información sobre el formato */}
      <div className="flex items-start gap-2 text-xs text-gray-600">
        <div className="flex-1 space-y-1">
          {isCoordinates ? (
            <div className="flex items-center gap-1 text-green-600">
              <span>✓</span>
              <span>Coordenadas validas: Lat {value.split(',')[0]}, Lon {value.split(',')[1]}</span>
            </div>
          ) : (
            <div className="flex items-center gap-1 text-blue-600">
              <span>ℹ️</span>
              <span>Formato: latitud,longitud (ej: 4.6097,-74.0817)</span>
            </div>
          )}
          
          {locationMethod === 'gps' && isCoordinates && (
            <div className="flex items-center gap-1 text-indigo-600">
              <span>📍</span>
              <span>Ubicacion detectada automaticamente</span>
            </div>
          )}
        </div>
      </div>

      {/* Ejemplos de ciudades comunes */}
      {!isCoordinates && (
        <div className="text-xs text-gray-500">
          <details className="cursor-pointer">
            <summary className="hover:text-gray-700">Ver ejemplos de coordenadas</summary>
            <div className="mt-2 space-y-1 pl-3">
              <button
                type="button"
                onClick={() => onChange('4.6097,-74.0817')}
                className="block hover:text-indigo-600"
              >
                📍 Bogotá: 4.6097,-74.0817
              </button>
              <button
                type="button"
                onClick={() => onChange('6.2442,-75.5812')}
                className="block hover:text-indigo-600"
              >
                📍 Medellín: 6.2442,-75.5812
              </button>
              <button
                type="button"
                onClick={() => onChange('3.4516,-76.5320')}
                className="block hover:text-indigo-600"
              >
                📍 Cali: 3.4516,-76.5320
              </button>
              <button
                type="button"
                onClick={() => onChange('40.7128,-74.0060')}
                className="block hover:text-indigo-600"
              >
                📍 New York: 40.7128,-74.0060
              </button>
            </div>
          </details>
        </div>
      )}
    </div>
  );
};
