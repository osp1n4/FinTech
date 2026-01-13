/**
 * HUMAN REVIEW (Maria Paula Gutierrez):
 * La IA solo permitía ver reglas.
 * Agregué botones para crear, editar y eliminar reglas
 * Adicionalmente, una opción para activar/desactivar reglas
 * directamente desde el dashboard sin tocar código.
 */
import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { getRules, updateRule, createRule, deleteRule } from '@/services/api';
import type { Rule } from '@/types';

export default function RulesPage() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingRule, setEditingRule] = useState<Rule | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [newRule, setNewRule] = useState({
    name: '',
    type: 'custom',
    parameters: {},
    enabled: true,
    order: 999
  });
  const [parametersText, setParametersText] = useState('{}');
  const [deleteConfirm, setDeleteConfirm] = useState<{id: string, name: string} | null>(null);

  useEffect(() => {
    loadRules();
  }, []);

  const loadRules = async () => {
    try {
      const data = await getRules();
      setRules(data);
    } catch (error) {
      toast.error('Error al cargar reglas');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleEditRule = (rule: Rule) => {
    setEditingRule(rule);
  };

  const handleSaveRule = async () => {
    if (!editingRule) return;
    
    try {
      await updateRule(editingRule.id, editingRule.parameters);
      toast.success('Regla actualizada exitosamente');
      setEditingRule(null);
      loadRules();
    } catch (error) {
      toast.error('Error al actualizar regla');
      console.error(error);
    }
  };

  const handleCreateRule = async () => {
    if (!newRule.name || !newRule.type) {
      toast.error('Por favor completa todos los campos requeridos');
      return;
    }
    
    // Validar que el JSON sea válido
    try {
      JSON.parse(parametersText);
    } catch {
      toast.error('El formato de parámetros JSON es inválido');
      return;
    }
    
    try {
      const result = await createRule(newRule);
      console.log('Regla creada:', result);
      toast.success('Regla creada exitosamente');
      setIsCreating(false);
      setNewRule({
        name: '',
        type: 'custom',
        parameters: {},
        enabled: true,
        order: 999
      });
      setParametersText('{}');
      loadRules();
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Error al crear regla');
      console.error('Error creando regla:', error);
    }
  };

  const handleToggleEnabled = async (rule: Rule) => {
    try {
      await updateRule(rule.id, { ...rule.parameters, enabled: !rule.enabled });
      toast.success(rule.enabled ? 'Regla desactivada' : 'Regla activada');
      loadRules();
    } catch (error: any) {
      toast.error('Error al cambiar estado de regla');
      console.error(error);
    }
  };

  const handleDeleteRule = async (ruleId: string) => {
    try {
      await deleteRule(ruleId);
      toast.success('🗑️ Regla eliminada exitosamente');
      setDeleteConfirm(null);
      loadRules();
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || 'Error al eliminar regla';
      toast.error(errorMessage);
      console.error('Error eliminando regla:', error);
    }
  };



  if (loading) {
    return <div className="text-gray-400">Cargando...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Reglas de Fraude</h1>
        <button
          onClick={() => setIsCreating(true)}
          className="px-6 py-2 bg-green-600 rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
        >
          <span className="text-xl">+</span>
          {' '}
          Nueva Regla
        </button>
      </div>

      <div className="space-y-4">
        {rules.map((rule) => (
          <div key={rule.id} className="bg-admin-surface rounded-xl p-6 border border-gray-700 hover:border-admin-primary transition-all">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-4">
                <h3 className="text-lg font-semibold">{rule.name}</h3>
                {/* Toggle Switch */}
                <button
                  onClick={() => handleToggleEnabled(rule)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    rule.enabled ? 'bg-green-600' : 'bg-gray-600'
                  }`}
                  title={rule.enabled ? 'Desactivar regla' : 'Activar regla'}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      rule.enabled ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
                <span className={`text-xs font-medium ${
                  rule.enabled ? 'text-green-400' : 'text-gray-500'
                }`}>
                  {rule.enabled ? '✓ Activa' : '✕ Inactiva'}
                </span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleEditRule(rule)}
                  className="px-4 py-2 bg-admin-primary rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2"
                >
                  <span>✏️</span>
                  {' '}
                  Editar
                </button>
                <button
                  onClick={() => setDeleteConfirm({id: rule.id, name: rule.name})}
                  className="px-4 py-2 bg-red-600 rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2"
                >
                  <span>🗑️</span>
                  {' '}
                  Eliminar
                </button>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-400">Tipo:</span>
                <span className="ml-2 text-white">{rule.type}</span>
              </div>
              <div>
                <span className="text-gray-400">Prioridad:</span>
                <span className="ml-2 text-white">{rule.order}</span>
              </div>
              <div className="col-span-2">
                <span className="text-gray-400">Parámetros:</span>
                <pre className="mt-2 p-3 bg-admin-bg rounded-lg text-xs">
                  {JSON.stringify(rule.parameters, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Modal de Confirmación de Eliminación */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 backdrop-blur-sm">
          <div className="bg-gradient-to-br from-red-900/20 to-admin-surface border-2 border-red-500/50 rounded-2xl p-8 max-w-md w-full shadow-2xl animate-pulse-slow">
            <div className="flex flex-col items-center text-center">
              <div className="w-20 h-20 bg-red-600/20 rounded-full flex items-center justify-center mb-4 animate-bounce">
                <span className="text-5xl">⚠️</span>
              </div>
              <h2 className="text-2xl font-bold mb-4 text-red-400">¡Atención!</h2>
              <p className="text-gray-300 mb-2">
                Estás a punto de eliminar la regla:
              </p>
              <p className="text-xl font-semibold text-white mb-4">
                &quot;{deleteConfirm.name}&quot;
              </p>
              <div className="bg-red-950/50 border border-red-700/50 rounded-lg p-4 mb-6">
                <p className="text-sm text-red-200">
                  🔥 Esta acción es <strong>irreversible</strong>.<br />
                  💀 Las transacciones ya no serán evaluadas con esta regla.<br />
                  🚨 ¿Realmente quieres eliminarla del sistema?
                </p>
              </div>
              <div className="flex gap-3 w-full">
                <button
                  onClick={() => setDeleteConfirm(null)}
                  className="flex-1 px-6 py-3 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors font-medium"
                >
                  🛡️ Cancelar 
                </button>
                <button
                  onClick={() => handleDeleteRule(deleteConfirm.id)}
                  className="flex-1 px-6 py-3 bg-red-600 rounded-lg hover:bg-red-700 transition-colors font-medium"
                >
                  🗑️ Sí, eliminar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Edición */}
      {editingRule && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-admin-surface rounded-xl p-8 max-w-md w-full">
            <h2 className="text-xl font-bold mb-6">Editar Regla: {editingRule.name}</h2>
            <div className="space-y-4">
              {editingRule.type === 'amount_threshold' && (
                <div>
                  <label htmlFor="threshold-input" className="block text-sm mb-2">Threshold ($)</label>
                  <input
                    id="threshold-input"
                    type="number"
                    className="w-full px-4 py-2 bg-admin-bg rounded-lg border border-gray-600 focus:border-admin-primary focus:outline-none"
                    value={editingRule.parameters.threshold}
                    onChange={(e) =>
                      setEditingRule({
                        ...editingRule,
                        parameters: { ...editingRule.parameters, threshold: Number.parseFloat(e.target.value) },
                      })
                    }
                  />
                </div>
              )}
              {editingRule.type === 'location_check' && (
                <div>
                  <label htmlFor="radius-km-input" className="block text-sm mb-2">Radio de ubicación (km)</label>
                  <input
                    id="radius-km-input"
                    type="number"
                    className="w-full px-4 py-2 bg-admin-bg rounded-lg border border-gray-600 focus:border-admin-primary focus:outline-none"
                    value={editingRule.parameters.radius_km}
                    onChange={(e) =>
                      setEditingRule({
                        ...editingRule,
                        parameters: { ...editingRule.parameters, radius_km: Number.parseFloat(e.target.value) },
                      })
                    }
                  />
                </div>
              )}
              {editingRule.type === 'device_validation' && (
                <div>
                  <label htmlFor="device-memory-input" className="block text-sm mb-2">Memoria de dispositivos (días)</label>
                  <input
                    id="device-memory-input"
                    type="number"
                    className="w-full px-4 py-2 bg-admin-bg rounded-lg border border-gray-600 focus:border-admin-primary focus:outline-none"
                    value={editingRule.parameters.device_memory_days || 90}
                    onChange={(e) =>
                      setEditingRule({
                        ...editingRule,
                        parameters: { ...editingRule.parameters, device_memory_days: Number.parseInt(e.target.value, 10) },
                      })
                    }
                  />
                  <p className="text-xs text-gray-400 mt-2">Días que se recuerdan los dispositivos usados</p>
                </div>
              )}
              {editingRule.type === 'rapid_transaction' && (
                <div className="space-y-4">
                  <div>
                    <label htmlFor="max-transactions-input" className="block text-sm mb-2">Máximo de transacciones</label>
                    <input
                      id="max-transactions-input"
                      type="number"
                      className="w-full px-4 py-2 bg-admin-bg rounded-lg border border-gray-600 focus:border-admin-primary focus:outline-none"
                      value={editingRule.parameters.max_transactions || 3}
                      onChange={(e) =>
                        setEditingRule({
                          ...editingRule,
                          parameters: { ...editingRule.parameters, max_transactions: Number.parseInt(e.target.value, 10) },
                        })
                      }
                    />
                  </div>
                  <div>
                    <label htmlFor="time-window-input" className="block text-sm mb-2">Ventana de tiempo (minutos)</label>
                    <input
                      id="time-window-input"
                      type="number"
                      className="w-full px-4 py-2 bg-admin-bg rounded-lg border border-gray-600 focus:border-admin-primary focus:outline-none"
                      value={editingRule.parameters.time_window_minutes || 5}
                      onChange={(e) =>
                        setEditingRule({
                          ...editingRule,
                          parameters: { ...editingRule.parameters, time_window_minutes: Number.parseInt(e.target.value, 10) },
                        })
                      }
                    />
                    <p className="text-xs text-gray-400 mt-2">Detecta muchas transacciones en poco tiempo</p>
                  </div>
                </div>
              )}
              {editingRule.type === 'unusual_time' && (
                <div>
                  <label htmlFor="deviation-threshold-input" className="block text-sm mb-2">Umbral de desviación (0.0 - 1.0)</label>
                  <input
                    id="deviation-threshold-input"
                    type="number"
                    step="0.1"
                    min="0"
                    max="1"
                    className="w-full px-4 py-2 bg-admin-bg rounded-lg border border-gray-600 focus:border-admin-primary focus:outline-none"
                    value={editingRule.parameters.deviation_threshold || 0.3}
                    onChange={(e) =>
                      setEditingRule({
                        ...editingRule,
                        parameters: { ...editingRule.parameters, deviation_threshold: Number.parseFloat(e.target.value) },
                      })
                    }
                  />
                  <p className="text-xs text-gray-400 mt-2">Detecta transacciones en horarios inusuales para el usuario</p>
                </div>
              )}
            </div>
            <div className="flex space-x-4 mt-6">
              <button
                onClick={() => setEditingRule(null)}
                className="flex-1 px-4 py-2 bg-gray-600 rounded-lg hover:bg-gray-700 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleSaveRule}
                className="flex-1 px-4 py-2 bg-admin-primary rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Guardar Cambios
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Creación */}
      {isCreating && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-admin-surface rounded-xl p-8 max-w-md w-full">
            <h2 className="text-xl font-bold mb-6">Crear Nueva Regla</h2>
            <div className="space-y-4">
              <div>
                <label htmlFor="new-rule-name" className="block text-sm mb-2">Nombre de la Regla *</label>
                <input
                  id="new-rule-name"
                  type="text"
                  className="w-full px-4 py-2 bg-admin-bg rounded-lg border border-gray-600 focus:border-admin-primary focus:outline-none"
                  placeholder="Ej: Regla de horario nocturno"
                  value={newRule.name}
                  onChange={(e) => setNewRule({ ...newRule, name: e.target.value })}
                />
              </div>
              <div>
                <label htmlFor="new-rule-type" className="block text-sm mb-2">Tipo de Regla *</label>
                <select
                  id="new-rule-type"
                  className="w-full px-4 py-2 bg-admin-bg rounded-lg border border-gray-600 focus:border-admin-primary focus:outline-none"
                  value={newRule.type}
                  onChange={(e) => setNewRule({ ...newRule, type: e.target.value })}
                >
                  <option value="custom">Regla Personalizada</option>
                  <option value="amount_threshold">Umbral de Monto</option>
                  <option value="location_check">Verificación de Ubicación</option>
                  <option value="time_based">Basada en Horario</option>
                  <option value="frequency">Frecuencia de Transacciones</option>
                  <option value="velocity">Velocidad de Transacciones</option>
                </select>
              </div>
              <div>
                <label htmlFor="new-rule-parameters" className="block text-sm mb-2">Parámetros (JSON)</label>
                <textarea
                  id="new-rule-parameters"
                  className="w-full px-4 py-2 bg-admin-bg rounded-lg border border-gray-600 focus:border-admin-primary focus:outline-none font-mono text-sm"
                  rows={4}
                  placeholder='{\n  "threshold": 1000,\n  "action": "flag"\n}'
                  value={parametersText}
                  onChange={(e) => {
                    const text = e.target.value;
                    setParametersText(text);
                    // Intentar parsear solo para validar
                    try {
                      const params = JSON.parse(text);
                      setNewRule({ ...newRule, parameters: params });
                    } catch {
                      // JSON inválido, pero permitir que el usuario siga escribiendo
                    }
                  }}
                />
                {(() => {
                  try {
                    JSON.parse(parametersText);
                    return <p className="text-xs text-green-400 mt-1">✓ JSON válido</p>;
                  } catch {
                    return <p className="text-xs text-yellow-400 mt-1">⚠ JSON inválido</p>;
                  }
                })()}
              </div>
              <div>
                <label htmlFor="new-rule-order" className="block text-sm mb-2">Prioridad (orden)</label>
                <input
                  id="new-rule-order"
                  type="number"
                  className="w-full px-4 py-2 bg-admin-bg rounded-lg border border-gray-600 focus:border-admin-primary focus:outline-none"
                  value={newRule.order}
                  onChange={(e) => setNewRule({ ...newRule, order: Number.parseInt(e.target.value, 10) })}
                />
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="enabled"
                  className="mr-2"
                  checked={newRule.enabled}
                  onChange={(e) => setNewRule({ ...newRule, enabled: e.target.checked })}
                />
                <label htmlFor="enabled" className="text-sm">Regla activa</label>
              </div>
            </div>
            <div className="flex space-x-4 mt-6">
              <button
                onClick={() => {
                  setIsCreating(false);
                  setNewRule({
                    name: '',
                    type: 'custom',
                    parameters: {},
                    enabled: true,
                    order: 999
                  });
                  setParametersText('{}');
                }}
                className="flex-1 px-4 py-2 bg-gray-600 rounded-lg hover:bg-gray-700 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleCreateRule}
                className="flex-1 px-4 py-2 bg-green-600 rounded-lg hover:bg-green-700 transition-colors"
              >
                Crear Regla
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
